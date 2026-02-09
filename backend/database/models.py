from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship
from backend.database.config import Base


class DebateStatus(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Debate(Base):
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(500), nullable=False)
    status = Column(Enum(DebateStatus), default=DebateStatus.PENDING, nullable=False)
    max_rounds = Column(Integer, default=3)
    current_round = Column(Integer, default=0)
    pro_score = Column(Integer, default=0)
    con_score = Column(Integer, default=0)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rounds = relationship("Round", back_populates="debate", cascade="all, delete-orphan")


class Round(Base):
    __tablename__ = "rounds"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, ForeignKey("debates.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    pro_argument = Column(Text, nullable=True)
    con_argument = Column(Text, nullable=True)
    judge_comment = Column(Text, nullable=True)
    pro_score = Column(Integer, default=0)
    con_score = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    debate = relationship("Debate", back_populates="rounds")
