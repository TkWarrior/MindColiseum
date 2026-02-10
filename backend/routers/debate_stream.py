"""
Debate Stream Router
=====================
SSE (Server-Sent Events) endpoint for real-time debate streaming.

When the frontend connects to GET /debates/{id}/stream, this endpoint:
1. Opens a persistent HTTP connection (SSE)
2. Runs the debate via debate_stream_service
3. Pushes events (text + audio) to the frontend as they happen

Frontend Usage:
    const eventSource = new EventSource("/debates/5/stream");
    
    eventSource.addEventListener("debate_started", (e) => {
        const data = JSON.parse(e.data);
        console.log("Debate started:", data.topic);
    });
    
    eventSource.addEventListener("agent_text", (e) => {
        const data = JSON.parse(e.data);
        showArgument(data.agent, data.round, data.text);
    });
    
    eventSource.addEventListener("agent_audio", (e) => {
        const data = JSON.parse(e.data);
        playAudio(data.audio);  // base64 WAV
    });
    
    eventSource.addEventListener("debate_complete", (e) => {
        const data = JSON.parse(e.data);
        showResults(data.pro_score, data.con_score, data.summary);
        eventSource.close();
    });
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from backend.database.config import get_db, SessionLocal
from backend.services import debate_stream_service
from backend.services.debate_service import get_debate

router = APIRouter(prefix="/debates", tags=["debate-stream"])


@router.get("/{debate_id}/stream")
async def stream_debate(debate_id: int, db: Session = Depends(get_db)):
    """
    SSE endpoint — streams a debate in real-time with text + TTS audio.
    
    Flow:
        1. Validates the debate exists and is in "pending" status
        2. Opens an SSE connection (persistent HTTP stream)
        3. Runs the LangGraph agent step-by-step
        4. For each agent: sends text event, then audio event
        5. After all rounds: saves to DB and sends completion event
    
    SSE Events:
        - debate_started  → {debate_id, topic, max_rounds}
        - agent_text      → {agent, round, text}
        - agent_audio     → {agent, round, audio}  (base64 WAV)
        - round_complete  → {round, scores}
        - debate_complete → {debate_id, pro_score, con_score, summary}
        - error           → {message}
    
    Args:
        debate_id: ID of the debate to stream.
        
    Returns:
        EventSourceResponse — persistent SSE connection.
    """
    # Validate debate exists before opening SSE stream
    debate = get_debate(db, debate_id)
    if not debate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debate with id {debate_id} not found",
        )

    if debate.status.value != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Debate is already {debate.status.value}. Only pending debates can be streamed.",
        )

    # Return SSE response — this keeps the connection open
    # and streams events from debate_stream_service.stream_debate()
    return EventSourceResponse(
        debate_stream_service.stream_debate(debate_id, SessionLocal)
    )
