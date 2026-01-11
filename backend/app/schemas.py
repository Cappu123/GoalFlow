from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, Json
from uuid import UUID, uuid4
from coreAI.AI_schemas import LLMResponse

#users schema
class CreateUser(BaseModel):
    email: str
    username: Optional[str]
    password: str
class ReturnUser(BaseModel):
    id: str
    email: str




#Chats Schema
class CreateChat(BaseModel):
    chat_id: Optional[str] = None
    content: str

class ChatResponse(BaseModel):
    chat_id: str
    reply: LLMResponse

class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str | dict

class CreateGoal(BaseModel):
    goal_drafted: ChatResponse


class GoalResponse(BaseModel):
    id: str
    chat_id: str
    goal_title: str
    goal_description: str
    status: str
    created_at: datetime | None

    model_config = {
        "from_attributes": True  # Pydantic v2
    }

class GoalsResponse(BaseModel):
    goals: list[GoalResponse]