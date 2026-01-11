import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks, Cookie
from sqlalchemy.orm.session import Session
from datetime import datetime
from database import get_db
from schemas import *
from models import *
from coreAI.AI_schemas import *
from coreAI.generate_response import generate_response


router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

# @router.post("/save_draft_goal")
# def save_draft_goal(goal_id)


@router.post("/save_draft_goal")
def save_draft_goal(payload: ChatResponse, db:Session = Depends(get_db)):
    # existing_goal = db.query(Goal).filter(Goal.chat_id == payload.chat_id).first()
    # if existing_goal:
    #     print("Goal already exists. Please create on a new session.")
    #     return 
    goal_draft = Goal(
        chat_id = payload.chat_id,
        goal_title = payload.reply.payload["goal_title"],
        goal_description = payload.reply.payload["goal_description"],
        
    )
    db.add(goal_draft)
    db.commit()

    #save the milestones draft
    draft_milestone = []
    
    for m in payload.reply.payload["milestones"]:
        milestone_draft = Milestone(
            goal_id = goal_draft.id,
            milestone_name = m["milestone_name"],
            milestone_description = m["milestone_description"]
        )
        db.add(milestone_draft)

        #append to draft milestone after being added to db,, for the .id property populated
        draft_milestone.append(milestone_draft)
    db.commit()
   
    return {
        "confirmation_message": payload.reply.payload["confirmation_message"],
        "Draft Goal": {
            "id": goal_draft.id,
            "chat_id": goal_draft.chat_id,
            "title": goal_draft.goal_title,
            "description": goal_draft.goal_description,
            "status": goal_draft.status
        },
        "Draft Milestones": [{
            "id": m.id,
            "name": m.milestone_name,
            "description": m.milestone_description
        } for m in draft_milestone],

        "next_prompt": payload.reply.payload["next_step_prompt"]

    }
@router.post("/save_goal_draft", response_model=GoalResponse | None)
def save_goal_draft(goal_id: str, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.status == "draft").first()
    if not goal:
        print("This draft goal wasn’t found. You can check your saved goals or create a new one.")
        return
    goal.status = "active"
    goal.created_at = datetime.now()
    db.commit()
    db.refresh(goal)
    return goal

@router.post("/saved_goals")
def saved_goals(db: Session = Depends(get_db)):
    goals = db.query(Goal).filter(Goal.status == "active").all()
    return goals