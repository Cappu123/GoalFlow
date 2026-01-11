import uuid
from fastapi import APIRouter, Depends, HTTPException, Response, BackgroundTasks, Cookie
from sqlalchemy.orm.session import Session
from database import get_db
from schemas import *
from models import *
from coreAI.AI_schemas import *
from coreAI.generate_response import generate_response

router = APIRouter(
    prefix="/chats",
    tags=["Chats"]
)

@router.post("/conversation")
    
def conversation(userInput: CreateChat, db:Session = Depends(get_db)):
    res =  generate_response(
        db,
        userInput
    )
    return res

