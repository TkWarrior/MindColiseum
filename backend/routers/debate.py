from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.config import get_db, SessionLocal
from backend.schemas.debate import (
    DebateCreate, 
    DebateResponse, 
    DebateDetailResponse, 
    DebateListResponse
)
from backend.services import debate_service

router = APIRouter(prefix="/debates", tags=["debates"])


@router.post("", response_model=DebateResponse, status_code=status.HTTP_201_CREATED)
def create_debate(debate_data: DebateCreate, db: Session = Depends(get_db)):
    """Create a new debate."""
    debate = debate_service.create_debate(db, debate_data)
    return debate


@router.get("", response_model=DebateListResponse)
def list_debates(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List all debates with pagination."""
    debates = debate_service.get_all_debates(db, skip=skip, limit=limit)
    total = debate_service.count_debates(db)
    return DebateListResponse(debates=debates, total=total)


@router.get("/{debate_id}", response_model=DebateDetailResponse)
def get_debate(debate_id: int, db: Session = Depends(get_db)):
    """Get a debate by ID with all rounds."""
    debate = debate_service.get_debate(db, debate_id)
    if not debate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debate with id {debate_id} not found"
        )
    return debate


@router.post("/{debate_id}/start", response_model=DebateResponse)
def start_debate(debate_id: int, db: Session = Depends(get_db)):
    """
    Start debate execution asynchronously.
    Returns immediately with status 'running'. 
    Poll GET /debates/{id} to check progress.
    """
    debate = debate_service.get_debate(db, debate_id)
    if not debate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Debate with id {debate_id} not found"
        )
    
    if debate.status.value != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Debate is already {debate.status.value}"
        )
    
    # Pass session factory for background thread
    debate = debate_service.start_debate(db, debate_id, SessionLocal)
    return debate
