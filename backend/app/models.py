import uuid
import enum
from sqlalchemy import Column, Integer, JSON, String, ForeignKey, DateTime, UUID, Boolean, Enum
from typing import Dict
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default = lambda: str(uuid.uuid4()))
    user_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True)
    #user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False)
    content = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    chat = relationship("Chat", back_populates="messages")
    
# class GoalStatus(enum.Enum):
#     draft = "draft"
#     confirmed = "active"


class Goal(Base):
    __tablename__ = "goals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    goal_title = Column(String)
    goal_description = Column(String)
    status = Column(Enum("draft", "active", "paused", "completed", name="goal_status", default="draft" ))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    duration_value = Column(Integer, nullable=False)
    duration_unit = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    draft_fingerprint = Column(String, unique=True, nullable=True)
    saved_fingerprint = Column(String, unique=True, nullable=True)

    chat = relationship("Chat", back_populates="goals")
    milestones = relationship("Milestone", back_populates="goal", cascade="all, delete-orphan")
    

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    goal_id = Column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    milestone_name = Column(String)
    milestone_description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_value = Column(Integer, nullable=False)
    duration_unit = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)

    goal = relationship("Goal", back_populates="milestones")