import threading
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.database.models import Debate, Round, DebateStatus
from backend.schemas.debate import DebateCreate
from graph.graph import agent


def create_debate(db: Session, debate_data: DebateCreate) -> Debate:
    """Create a new debate in pending state."""
    debate = Debate(
        topic=debate_data.topic,
        max_rounds=debate_data.max_rounds,
        status=DebateStatus.PENDING
    )
    db.add(debate)
    db.commit()
    db.refresh(debate)
    return debate


def get_debate(db: Session, debate_id: int) -> Optional[Debate]:
    """Get a debate by ID."""
    return db.query(Debate).filter(Debate.id == debate_id).first()


def get_all_debates(db: Session, skip: int = 0, limit: int = 100) -> List[Debate]:
    """Get all debates with pagination."""
    return db.query(Debate).order_by(Debate.created_at.desc()).offset(skip).limit(limit).all()


def count_debates(db: Session) -> int:
    """Count total debates."""
    return db.query(Debate).count()


def _run_debate_async(debate_id: int, db_session_factory):
    """
    Run debate in a background thread.
    This function creates its own database session since it runs in a separate thread.
    """
    db = db_session_factory()
    try:
        debate = db.query(Debate).filter(Debate.id == debate_id).first()
        if not debate:
            return

        # Update status to running
        debate.status = DebateStatus.RUNNING
        db.commit()

        # Prepare initial state for LangGraph agent
        initial_state = {
            "debate_topic": debate.topic,
            "round_no": 1,
            "max_rounds": debate.max_rounds,
            "current_agent": "pro_agent",
            "pro_arguments": [],
            "conn_arguments": [],
            "judge_comments": [],
            "scores": {"pro": 0, "con": 0},
            "transcript": [],
            "debate_over": False
        }

        # Run the LangGraph agent
        result = agent.invoke(initial_state)

        # Save rounds to database
        pro_args = result.get("pro_arguments", [])
        con_args = result.get("conn_arguments", [])
        judge_comments = result.get("judge_comments", [])
        
        num_rounds = max(len(pro_args), len(con_args))
        for i in range(num_rounds):
            round_obj = Round(
                debate_id=debate.id,
                round_number=i + 1,
                pro_argument=pro_args[i] if i < len(pro_args) else None,
                con_argument=con_args[i] if i < len(con_args) else None,
                judge_comment=judge_comments[i] if i < len(judge_comments) else None,
            )
            db.add(round_obj)

        # Update debate with final scores and status
        scores = result.get("scores", {"pro": 0, "con": 0})
        debate.pro_score = scores.get("pro", 0)
        debate.con_score = scores.get("con", 0)
        debate.current_round = num_rounds
        debate.status = DebateStatus.COMPLETED

        # Extract summary from transcript if available
        transcript = result.get("transcript", [])
        if transcript:
            # Find summary in transcript (usually the last entry from summary_agent)
            for entry in reversed(transcript):
                content = entry.get("content", "")
                if "[SUMMARY]" in content:
                    debate.summary = content.replace("[SUMMARY]", "").strip()
                    break

        db.commit()

    except Exception as e:
        print(f"Debate execution failed: {e}")
        debate = db.query(Debate).filter(Debate.id == debate_id).first()
        if debate:
            debate.status = DebateStatus.FAILED
            db.commit()
    finally:
        db.close()


def start_debate(db: Session, debate_id: int, db_session_factory) -> Optional[Debate]:
    """
    Start debate execution asynchronously.
    Returns the debate immediately, execution happens in background.
    """
    debate = get_debate(db, debate_id)
    if not debate:
        return None
    
    if debate.status != DebateStatus.PENDING:
        return debate  # Already started or completed

    # Start debate in background thread
    thread = threading.Thread(
        target=_run_debate_async,
        args=(debate_id, db_session_factory),
        daemon=True
    )
    thread.start()

    # Update status to indicate it's starting
    debate.status = DebateStatus.RUNNING
    db.commit()
    db.refresh(debate)
    
    return debate
