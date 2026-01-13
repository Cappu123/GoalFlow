import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks, Cookie, status
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import Session
from datetime import datetime, timedelta
from database import get_db
from schemas import *
from models import *
from coreAI.AI_schemas import *
from coreAI.generate_response import generate_response
from utils import parse_timeframe, generate_fingerprint 

router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

# @router.post("/save_draft_goal")
# def save_draft_goal(goal_id)


@router.post("/save_draft_goal")
def save_draft_goal(payload: ChatResponse, db:Session = Depends(get_db)):
    if payload.reply.intent != "create_goal":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please enter a valid goal draft") 
   
    fingerprint = generate_fingerprint(payload.reply.payload)

    #Check first: if goal is triggered already(started)
    started = db.query(Goal).filter(Goal.saved_fingerprint == fingerprint)
    if started:
        return {
            "status": "already started",
            "message": "Goal already started"
        }
    
    #Check 2nd if draft already saved
    existing = db.query(Goal).filter(Goal.draft_fingerprint == fingerprint).first()
    if existing:
        return {
            "status": "already_exists",
            "message": "Draft goal already saved."
        }

    #Since time frame is human langueage, need to parse it.
    value, unit = parse_timeframe(payload.reply.payload["time_frame"])

    #now save draft goal into db
    goal_draft = Goal(
        chat_id = payload.chat_id,
        goal_title = payload.reply.payload["goal_title"],
        goal_description = payload.reply.payload["goal_description"],
        status = "draft",
        duration_value = value,
        duration_unit = unit,
        draft_fingerprint = fingerprint        
    )
    db.add(goal_draft)
    db.commit()

    #save the milestones draft
    draft_milestone = []
    
    #same with milestones timeframe
   
    for m in payload.reply.payload["milestones"]:
        m_value, m_unit = parse_timeframe(m["time_frame"])
        milestone_draft = Milestone(
            goal_id = goal_draft.id,
            milestone_name = m["milestone_name"],
            milestone_description = m["milestone_description"],
            duration_value = m_value,
            duration_unit = m_unit
           
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
            "status": goal_draft.status,
            "created_at": goal_draft.created_at,
            "duration": goal_draft.duration_value,
            "duration_unit": goal_draft.duration_unit
        },
        "Draft Milestones": [{
            "id": m.id,
            "name": m.milestone_name,
            "description": m.milestone_description,
            "duration": m.duration_value,
            "duration_unit": m.duration_unit
        } for m in draft_milestone],

        "next_prompt": payload.reply.payload["next_step_prompt"]

    }


@router.post("/save_goal")
def save_goal(payload: ChatResponse, db:Session = Depends(get_db)):
    if payload.reply.intent != "create_goal":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please enter a valid goal") 
    #Check if draft already saved
    fingerprint = generate_fingerprint(payload.reply.payload)
    existing = db.query(Goal).filter(Goal.saved_fingerprint == fingerprint).first()

    if existing:
        return {
            "status": "already_exists",
            "message": "Goal already saved."
        }
    #in drafts
    goal = db.query(Goal).filter(Goal.draft_fingerprint == fingerprint).first()
    if not goal:

        #parse timeframe
        value, unit = parse_timeframe(payload.reply.payload["time_frame"])
    
        #now save goal into db
        goal = Goal(
            chat_id = payload.chat_id,
            goal_title = payload.reply.payload["goal_title"],
            goal_description = payload.reply.payload["goal_description"],
            status = "active",
            duration_value = value,
            duration_unit = unit,
            saved_fingerprint = fingerprint   ,
            start_date = datetime.utcnow()     
        )
        #goal.due_date = goal.start_date + goal.duration_value
        db.add(goal)
        db.flush()

        #save the milestones draft
        milestone = []
    
        #same with milestones timeframe
   
        for m in payload.reply.payload["milestones"]:
            m_value, m_unit = parse_timeframe(m["time_frame"])

            milestone = Milestone(
            goal_id = goal.id,
            milestone_name = m["milestone_name"],
            milestone_description = m["milestone_description"],
            milestone_steps = m["milestone_steps"],
            duration_value = m_value,
            duration_unit = m_unit
                
            )
            db.add(milestone)
            
    else:
        #if draft found set only few remaining info
        goal.start_date = datetime.utcnow()
        #goal.due_date = (goal.start_date + goal.duration_value).isoformat(),
        goal.status = "active"
        goal.saved_fingerprint = fingerprint
    db.commit()
    return {
        "goal_id": goal.id,
        "status": "activated",
        "message": "Goal activated successfully."
        }

@router.post("/saved_goals")
def saved_goals(db: Session = Depends(get_db)):
    goals = db.query(Goal).options(joinedload(Goal.milestones)).filter(Goal.status == "active").order_by(Goal.created_at.desc()).all()
    if not goals:
        return {
            "status": "Empty",
            "message": "No saved goals found."
        }
   
    return goals

@router.post("/saved_drafts")
def saved_drafts(db: Session = Depends(get_db)):
    drafts = db.query(Goal).options(joinedload(Goal.milestones)).filter(Goal.status == "draft").order_by(Goal.created_at.desc()).all()
    if not drafts:
        return {
            "status": "Empty",
            "message": "No saved drafts found."
        }

    return drafts