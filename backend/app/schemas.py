from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, Json
from uuid import UUID, uuid4

class CreateUser(BaseModel):
    email: str
    username: Optional[str]
    password: str


class ReturnUser(BaseModel):
    id: str
    email: str



class CreateChat(BaseModel):
    chat_id: Optional[str] = None
    content: str


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str | dict


class ChatResponse(BaseModel):
    id: str
    user_id: int
    chat_id: uuid4
    messages: List[Message] = Field(default_factory=list)
    created_at: datetime


class AIResponse(BaseModel):
    intent: Literal[
        "create_goal",
        "update_progress",
        "delete_goal",
        "casual_chat",
        "ask_clarification"
    ] 
    payload: List[Message]