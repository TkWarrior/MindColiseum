"""
Debate Stream Service
======================
Runs a debate step-by-step using LangGraph's agent.stream() and yields
Server-Sent Events (SSE) for each agent's text output and TTS audio.

Data Flow:
    1. Frontend connects via SSE → GET /debates/{id}/stream
    2. This service runs agent.stream(initial_state)
    3. For each LangGraph node that completes:
       a. Extract the agent's argument text from the updated state
       b. Yield an "agent_text" SSE event (frontend shows text)
       c. Call TTS miniservice to generate audio
       d. Yield an "agent_audio" SSE event (frontend plays audio)
    4. After all rounds, save results to database
    5. Yield "debate_complete" SSE event

SSE Events Emitted:
    - debate_started  → {debate_id, topic, max_rounds}
    - agent_text      → {agent, round, text}
    - agent_audio     → {agent, round, audio} (base64 WAV)
    - round_complete  → {round, scores}
    - debate_complete → {debate_id, pro_score, con_score, summary}
    - error           → {message}
"""

import json
import logging
from typing import AsyncGenerator

from backend.database.models import Debate, Round, DebateStatus
from backend.services.tts_client import get_audio_base64, NODE_TO_VOICE
from graph.graph import agent

logger = logging.getLogger(__name__)


def _make_sse_event(event: str, data: dict) -> dict:
    """
    Format an SSE event dict for sse-starlette's EventSourceResponse.
    
    Args:
        event: SSE event name (e.g., "agent_text", "agent_audio").
        data: Event payload dict — will be JSON-serialized.
        
    Returns:
        Dict with "event" and "data" keys for EventSourceResponse.
    """
    return {"event": event, "data": json.dumps(data)}


def _extract_text_from_step(step: dict, node_name: str, state: dict) -> str:
    """
    Extract the latest argument/comment text from a LangGraph step.
    
    Each agent appends to a different list in the state:
        - pro_agent   → pro_arguments[-1]
        - conn_agent  → conn_arguments[-1]  
        - judge_agent → judge_comments[-1]
        - summary_agent → looks in transcript for [SUMMARY]
    
    Args:
        step: The step dict from agent.stream(), e.g. {"pro_agent": {state}}.
        node_name: Which node just ran (e.g., "pro_agent").
        state: The updated state after this node ran.
        
    Returns:
        The extracted text string.
    """
    if node_name == "pro_agent":
        args = state.get("pro_arguments", [])
        return args[-1] if args else ""
        
    elif node_name == "conn_agent":
        args = state.get("conn_arguments", [])
        return args[-1] if args else ""
        
    elif node_name == "judge_agent":
        comments = state.get("judge_comments", [])
        return comments[-1] if comments else ""
        
    elif node_name == "summary_agent":
        # Summary is stored in transcript with [SUMMARY] tag
        transcript = state.get("transcript", [])
        for entry in reversed(transcript):
            content = entry.get("content", "")
            if "[SUMMARY]" in content:
                return content.replace("[SUMMARY]", "").strip()
        return "Debate summary not available."
    
    return ""


async def stream_debate(debate_id: int, db_session_factory) -> AsyncGenerator:
    """
    Async generator that runs a debate and yields SSE events.
    
    This is the core function that connects LangGraph, TTS, and SSE:
    
        agent.stream()  →  yield text event  →  call TTS  →  yield audio event
              ↑                                                       ↓
         LangGraph                                              Frontend plays
    
    Args:
        debate_id: ID of the debate to run.
        db_session_factory: SQLAlchemy session factory for DB operations.
        
    Yields:
        SSE event dicts with "event" and "data" keys.
    """
    db = db_session_factory()
    
    try:
        # ── Step 1: Validate and prepare debate ─────────────────────
        debate = db.query(Debate).filter(Debate.id == debate_id).first()
        if not debate:
            yield _make_sse_event("error", {"message": f"Debate {debate_id} not found"})
            return
        
        if debate.status != DebateStatus.PENDING:
            yield _make_sse_event("error", {
                "message": f"Debate is already {debate.status.value}"
            })
            return

        # Mark debate as running
        debate.status = DebateStatus.RUNNING
        db.commit()

        # ── Step 2: Build initial state for LangGraph ───────────────
        # Same initial state as the existing debate_service._run_debate_async
        initial_state = {
            "debate_topic": debate.topic,
            "round_no": 1,
            "max_rounds": debate.max_rounds,
            "current_agent": "pro_agent",
            "pro_arguments": [],
            "conn_arguments": [],
            "judge_comments": [],
            "scores": {"pro": 0, "con": 0},
            "round_scores": [],
            "transcript": [],
            "debate_over": False,
        }

        # ── Step 3: Send debate_started event ───────────────────────
        yield _make_sse_event("debate_started", {
            "debate_id": debate_id,
            "topic": debate.topic,
            "max_rounds": debate.max_rounds,
        })

        # ── Step 4: Stream through LangGraph node by node ───────────
        # agent.stream() is a generator that yields after each node runs
        # Each step is a dict: {"node_name": updated_state}
        current_round = 1
        final_state = initial_state.copy()

        for step in agent.stream(initial_state):
            # Get which node just completed and its output state
            node_name = list(step.keys())[0]
            state = step[node_name]
            final_state.update(state)

            # Track current round number from state
            current_round = state.get("round_no", current_round)

            # Extract the text this agent just produced
            text = _extract_text_from_step(step, node_name, state)
            if not text:
                continue

            # Map node name to friendly agent name for the frontend
            agent_voice = NODE_TO_VOICE.get(node_name, "pro")

            # ── 4a. Yield text event → frontend shows argument ─────
            yield _make_sse_event("agent_text", {
                "agent": agent_voice,
                "round": current_round,
                "text": text,
            })

            # ── 4b. Generate TTS audio → yield audio event ──────────
            audio_b64 = await get_audio_base64(text, node_name)
            if audio_b64:
                yield _make_sse_event("agent_audio", {
                    "agent": agent_voice,
                    "round": current_round,
                    "audio": audio_b64,
                })

            # ── 4c. After judge scores, emit round_complete ─────────
            if node_name == "judge_agent":
                round_scores = state.get("round_scores", [])
                latest_score = round_scores[-1] if round_scores else {"pro": 0, "con": 0}
                yield _make_sse_event("round_complete", {
                    "round": current_round,
                    "scores": latest_score,
                })

        # ── Step 5: Save results to database ────────────────────────
        # Same logic as debate_service._run_debate_async
        pro_args = final_state.get("pro_arguments", [])
        con_args = final_state.get("conn_arguments", [])
        judge_comments = final_state.get("judge_comments", [])
        round_scores = final_state.get("round_scores", [])
        
        num_rounds = max(len(pro_args), len(con_args))
        for i in range(num_rounds):
            round_score = round_scores[i] if i < len(round_scores) else {"pro": 0, "con": 0}
            round_obj = Round(
                debate_id=debate.id,
                round_number=i + 1,
                pro_argument=pro_args[i] if i < len(pro_args) else None,
                con_argument=con_args[i] if i < len(con_args) else None,
                judge_comment=judge_comments[i] if i < len(judge_comments) else None,
                pro_score=round_score.get("pro", 0),
                con_score=round_score.get("con", 0),
            )
            db.add(round_obj)

        # Update debate with final scores
        scores = final_state.get("scores", {"pro": 0, "con": 0})
        debate.pro_score = scores.get("pro", 0)
        debate.con_score = scores.get("con", 0)
        debate.current_round = num_rounds
        debate.status = DebateStatus.COMPLETED

        # Extract summary from transcript
        transcript = final_state.get("transcript", [])
        for entry in reversed(transcript):
            content = entry.get("content", "")
            if "[SUMMARY]" in content:
                debate.summary = content.replace("[SUMMARY]", "").strip()
                break

        db.commit()

        # ── Step 6: Send debate_complete event ──────────────────────
        yield _make_sse_event("debate_complete", {
            "debate_id": debate_id,
            "pro_score": scores.get("pro", 0),
            "con_score": scores.get("con", 0),
            "summary": debate.summary,
        })

    except Exception as e:
        logger.error("Debate streaming failed: %s", str(e))
        
        # Mark debate as failed in DB
        try:
            debate = db.query(Debate).filter(Debate.id == debate_id).first()
            if debate:
                debate.status = DebateStatus.FAILED
                db.commit()
        except Exception:
            pass
        
        yield _make_sse_event("error", {"message": str(e)})
    
    finally:
        db.close()
