from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class DebateStatusEnum(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Request schemas
class DebateCreate(BaseModel):
    topic: str = Field(..., min_length=5, max_length=500, description="The debate topic")
    max_rounds: int = Field(default=3, ge=1, le=10, description="Maximum number of debate rounds")


# Response schemas
class RoundResponse(BaseModel):
    id: int
    round_number: int
    pro_argument: Optional[str] = None
    con_argument: Optional[str] = None
    judge_comment: Optional[str] = None
    pro_score: int = 0
    con_score: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class DebateResponse(BaseModel):
    id: int
    topic: str
    status: DebateStatusEnum
    max_rounds: int
    current_round: int
    pro_score: int
    con_score: int
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DebateDetailResponse(DebateResponse):
    rounds: List[RoundResponse] = []


class DebateListResponse(BaseModel):
    debates: List[DebateResponse]
    total: int
