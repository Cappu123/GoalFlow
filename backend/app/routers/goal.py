import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks, Cookie, status
from sqlalchemy.orm import joinedload, contains_eager
from sqlalchemy.orm.session import Session
from datetime import datetime, timedelta, timezone
from database import get_db
from schemas import *
from models import *
from coreAI.AI_schemas import *
from coreAI.generate_response import generate_response
from utils import parse_timeframe, generate_fingerprint, date_formatter, calculate_due_date

router = APIRouter(
    prefix="/goals",
    tags=["Goals"]
)

@router.post("/save_draft_goal", status_code=status.HTTP_201_CREATED, response_model=GoalDraft)
def save_draft_goal(payload: ChatResponse, db:Session = Depends(get_db)):
    if payload.reply.intent != "create_goal":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please enter a valid goal draft") 
   
    fingerprint = generate_fingerprint(payload.reply.payload)

    #Check first: if goal is triggered already(started)
    started = db.query(Goal).filter(Goal.saved_fingerprint == fingerprint).first()
    if started:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Goal already started, cannot save as draft.")
    
    #Check 2nd if draft already saved
    existing = db.query(Goal).filter(Goal.draft_fingerprint == fingerprint).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Draft goal already saved.")


    #Since time frame is human langueage, need to parse it.
    data = payload.reply.payload

    value, unit = parse_timeframe(data["time_frame"])

    #now save draft goal into db
    goal_draft = Goal(
        chat_id = payload.chat_id,
        goal_title = data["goal_title"],
        goal_description = data["goal_description"],
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
   
    for m in data["milestones"]:
        m_value, m_unit = parse_timeframe(m["time_frame"])
        milestone_draft = Milestone(
            chat_id = payload.chat_id,
            goal_id = goal_draft.id,
            status = "draft",
            milestone_order = m["milestone_order"],
            milestone_name = m["milestone_name"],
            milestone_description = m["milestone_description"],
            duration_value = m_value,
            duration_unit = m_unit
           
        )
        db.add(milestone_draft)
        db.commit()

        #append to draft milestone after being added to db,, for the .id property populated
        draft_milestone.append(milestone_draft)

        draft_steps = []
        #again save the milestone_steps
        for ms in m["steps"]:
                ms_value, ms_unit = parse_timeframe(ms["time_frame"])

                steps_draft = MilestoneStep(
                chat_id = payload.chat_id,
                goal_id = goal_draft.id,
                milestone_id = milestone_draft.id,
                step_order = ms["step_order"],
                step_description = ms["step_description"],
                status = "draft",
                duration_unit = ms_unit,
                duration_value = ms_value
            )
                db.add(steps_draft)
                draft_steps.append(draft_steps)

    db.commit()
    print(datetime.utcnow())
    print(calculate_due_date(datetime.utcnow(), 10, "days"))
   
    return {    
        "goal_id": goal_draft.id,
        "status": "draft",
        "message": "Goal saved in drafts successfully."
    }


@router.post("/save_goal", status_code=status.HTTP_201_CREATED, response_model=GoalFinal)
def save_goal(payload: ChatResponse, 
              db:Session = Depends(get_db)):
    print(payload.chat_id)
    if payload.reply.intent != "create_goal":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Please enter a valid goal") 
    #Check if draft already saved
    data = payload.reply.payload
    fingerprint = generate_fingerprint(data)
    existing = db.query(Goal).filter(Goal.saved_fingerprint == fingerprint).first()

    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="goal already saved.")
    #if drafted
    goal = db.query(Goal).filter(Goal.draft_fingerprint == fingerprint).first()
    if not goal:

        #parse timeframe
        value, unit = parse_timeframe(data["time_frame"])
    
        #now save goal into db
        
        start = (datetime.utcnow())
        due = calculate_due_date(start, value, unit)
        goal = Goal(
            chat_id = payload.chat_id,
            goal_title = data["goal_title"],
            goal_description = data["goal_description"],
            status = "active",
            duration_value = value,
            duration_unit = unit,
            saved_fingerprint = fingerprint,
            start_date =  start,
            due_date = due
        )
        #goal.due_date = goal.start_date + goal.duration_value
        db.add(goal)
        db.commit()


        #save the milestones draft
        milestone = []
    
        #same with milestones timeframe
        current_start = goal.start_date
        for m in data["milestones"]:
            m_value, m_unit = parse_timeframe(m["time_frame"])
            
            m_start = current_start
            m_due = calculate_due_date(m_start, m_value, m_unit)
             
            milestone = Milestone(
            chat_id = payload.chat_id,
            goal_id = goal.id,
            milestone_order = m["milestone_order"],
            milestone_name = m["milestone_name"],
            milestone_description = m["milestone_description"],
            status = "active",
            duration_value = m_value,
            duration_unit = m_unit,
            start_date = m_start,
            due_date = m_due,
                
            )
            db.add(milestone)
            db.commit()
            current_start = milestone.due_date

            #milestone_steps
            ms_start = m_start
            
            for ms in m["steps"]:
                ms_value, ms_unit = parse_timeframe(ms["time_frame"])
                ms_due = calculate_due_date(ms_start, ms_value, ms_unit)

                steps = MilestoneStep(
                    chat_id = payload.chat_id,
                    goal_id = goal.id,
                    milestone_id = milestone.id,
                    step_order = ms["step_order"],
                    step_description = ms["step_description"],
                    status = "active",
                    duration_unit = ms_unit,
                    duration_value = ms_value,
                    start_date = ms_start,
                    due_date = ms_due
                )

                db.add(steps)
                ms_start = ms_due
    else:
        #if draft found set only few remaining info
        goal.draft_fingerprint = ""
        goal.saved_fingerprint = fingerprint
        goal.start_date = datetime.utcnow()
        goal.status = "active"
        start = goal.start_date
        due = calculate_due_date(start, goal.duration_value, goal.duration_unit)
        goal.due_date = due
        mstart = goal.start_date 
        for milestone in goal.milestones:
            milestone.start_date = mstart
            milestone.status = "active"
            mdue = calculate_due_date(mstart, milestone.duration_value, milestone.duration_unit)
            milestone.due_date = mdue
            mstart = mdue

            ms_start = milestone.start_date
            for step in milestone.milestone_steps:
                step.start_date = ms_start
                step.status = "active"
                ms_due = calculate_due_date(ms_start, step.duration_value, step.duration_unit)
                step.due_date = ms_due
                ms_start = ms_due
    db.commit()
    return {
        "goal_id": goal.id,
        "status": "activated",
        "start_date": goal.start_date,
        "due_date": goal.due_date,
        "message": "Goal activated successfully."
        }


@router.get("/saved_goals", response_model=list[GoalFinal])
def saved_goals(db: Session = Depends(get_db)):
    #goals = db.query(Goal).options(joinedload(Goal.milestones).joinedload(Milestone.milestone_steps)).filter(Goal.status == "active").order_by(Goal.created_at.desc()).all()
    goals = db.query(Goal).join(Goal.milestones).join(Milestone.milestone_steps).options(contains_eager(Goal.milestones).contains_eager(Milestone.milestone_steps)).filter(Goal.status == "active").order_by(Goal.created_at.desc(), Milestone.start_date.asc(), MilestoneStep.step_order.asc()).all()
    if not goals:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No saved goals found.")
    return goals


@router.get("/draft_goals", response_model=list[GoalDraft])
def saved_drafts(db: Session = Depends(get_db)):
    #drafts = db.query(Goal).options(joinedload(Goal.milestones).joinedload(Milestone.milestone_steps)).filter(Goal.status == "draft").order_by(Goal.created_at.desc()).all()
    drafts = db.query(Goal).join(Goal.milestones).join(Milestone.milestone_steps).options(contains_eager(Goal.milestones).contains_eager(Milestone.milestone_steps)).filter(Goal.status == "draft").order_by(Goal.created_at.desc(), Milestone.start_date.asc(), MilestoneStep.step_order.asc()).all()
    if not drafts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No saved drafts found.")
    return drafts


@router.put("/update_goal/{goal_id}", status_code=status.HTTP_200_OK, response_model = Optional[GoalDraft | GoalFinal])
def update_goal_status(goal_id: str, updated_goal: GoalUpdate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Goal not found.")
    update_data = updated_goal.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(goal, key, value)
    db.commit()
    db.refresh(goal)    

    return goal

@router.put("/update_milestone/{milestone_id}", status_code=status.HTTP_200_OK, response_model = Optional[MilestoneDraft | MilestoneFinal])
def update_milestone_status(milestone_id: str, updated_milestone: MilestoneUpdate, db: Session = Depends(get_db)):  
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Milestone not found.")
    update_data = updated_milestone.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(milestone, key, value) 

    db.commit()
    db.refresh(milestone)   

    return milestone


@router.put("/update_step/{step_id}", status_code=status.HTTP_200_OK, response_model = Optional[StepsUpdate])
def update_step_status(step_id: str, updated_step: StepsUpdate, db: Session = Depends(get_db)):  
    step = db.query(MilestoneStep).filter(MilestoneStep.id == step_id).first()
    if not step:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Step not found.")
    update_data = updated_step.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(step, key, value) 

    db.commit()
    db.refresh(step)   

    return step