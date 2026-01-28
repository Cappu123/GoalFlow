from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, Json, field_serializer
from uuid import UUID, uuid4
from coreAI.AI_schemas import LLMResponse
from utils import date_formatter

#users schema

class ORMBase(BaseModel):
    model_config = {"from_attributes": True}

    @field_serializer("created_at", "start_date", "due_date", "updated_at", when_used="json", check_fields=False)
    def serialize(self, value: datetime):
        return date_formatter(value)
    
class CreateUser(ORMBase):
    email: str
    username: Optional[str]
    password: str
class ReturnUser(ORMBase):
    id: str
    email: str

#Chats Schema
class CreateChat(ORMBase):
    chat_id: Optional[str] = None
    content: str

class ChatResponse(ORMBase):
    chat_id: str
    reply: LLMResponse

class Testt(ORMBase):
    any

class StepDraft(ORMBase):
    step_order: int
    step_description: str
    created_at: datetime
    status: str
    duration_value: int
    duration_unit: str

class StepFinal(StepDraft):
    start_date: datetime
    due_date: datetime

class MilestoneDraft(ORMBase):
    milestone_order: int
    milestone_name: str
    milestone_description: str
    created_at: datetime 
    status: str
    duration_value: int
    duration_unit: str
    milestone_steps: list[StepDraft]

class MilestoneFinal(MilestoneDraft):
    milestone_steps: list[StepFinal]
    start_date: datetime
    due_date: datetime  

class GoalDraft(ORMBase):
    goal_title: str
    goal_description: str
    created_at: datetime
    status: str
    duration_value: int
    duration_unit: str
    milestones: list[MilestoneDraft]
    
class GoalFinal(GoalDraft):
    milestones: list[MilestoneFinal]  
    start_date: datetime
    due_date: datetime

class NotFound(ORMBase):
    status: str
    message: str

class StepUpdate(ORMBase):
    step_progress: Optional[Literal["not_started", "in_progress", "completed"]] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

class MilestoneUpdate(ORMBase):
    milestone_progress: Optional[Literal["not_started", "in_progress", "completed"]] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None


class GoalUpdate(ORMBase):
    goal_progress: Optional[Literal["not_started", "in_progress", "completed"]] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    
model_config = {
        "from_attributes": True  # Pydantic v2
    }



