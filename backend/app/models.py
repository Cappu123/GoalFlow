import uuid
import enum
import sqlalchemy as sa
from sqlalchemy import Column, Integer, JSON, String, ForeignKey, DateTime, UUID, Boolean, Enum
from typing import Dict
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, server_default=sa.text("gen_random_uuid()"))
    user_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Chat(Base):
    __tablename__ = "chats"

    id = Column(String, primary_key=True, server_default=sa.text("gen_random_uuid()"))
    #user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

    goals = relationship("Goal", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    id = Column(String, primary_key=True, server_default=sa.text("gen_random_uuid()"))
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
    id = Column(String, primary_key=True, server_default=sa.text("gen_random_uuid()"))
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    goal_title = Column(String)
    goal_description = Column(String)
    status = Column(Enum("draft", "active", "paused", "completed", name="goal_status", default="draft" ))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    duration_value = Column(Integer, nullable=False)
    duration_unit = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    draft_fingerprint = Column(String, nullable=True)
    saved_fingerprint = Column(String, unique=True, nullable=True)

    chat = relationship("Chat", back_populates="goals")
    milestones = relationship("Milestone", back_populates="goal", cascade="all, delete-orphan")

class Milestone(Base):
    __tablename__ = "milestones"
    id = Column(String, primary_key=True, server_default=sa.text("gen_random_uuid()"))
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    milestone_order = Column(Integer, nullable=False)
    milestone_name = Column(String)
    milestone_description = Column(String)
    status = Column(Enum("draft", "active", "paused", "completed", name="goal_status", default="draft" ))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_value = Column(Integer, nullable=False)
    duration_unit = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)

    goal = relationship("Goal", back_populates="milestones")
    milestone_steps = relationship("MilestoneStep", back_populates="milestone", cascade="all, delete-orphan")

class MilestoneStep(Base):
    __tablename__ = "milestone_steps"
    id = Column(String, primary_key=True, server_default=sa.text("gen_random_uuid()"))
    chat_id = Column(String, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    milestone_id = Column(String, ForeignKey("milestones.id", ondelete="CASCADE"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_description = Column(String)
    status = Column(Enum("draft", "active", "paused", "completed", name="goal_status", default="draft" ))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_value = Column(Integer, nullable=False)
    duration_unit = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)

    milestone = relationship("Milestone", back_populates="milestone_steps")