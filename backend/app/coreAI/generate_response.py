from .prompts.ai_prompts import INTENT_CLASSIFIER_SYSTEM_PROMPT
from groq import Groq
from langchain_core.output_parsers import PydanticOutputParser
from fastapi import FastAPI, Depends, APIRouter, HTTPException, Response, BackgroundTasks, status
from sqlalchemy.orm import Session
from config import settings
from schemas import *
from .AI_schemas import *
from models import *
import uuid
import json


import models
from database import get_db


#initialize groq client
groq_client = Groq(api_key=settings.GROQ_API_KEY)

def generate_response(db: Session, message: CreateChat):

    if not groq_client:
        return {
            "message": "Groq client not found"
        }

    if message.chat_id:
        chat = db.query(Chat).filter(Chat.id == message.chat_id).first()
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found. The provided chat_id does not exist."
            )
    else:
        chat = None
        #create and add chat into db
    if not chat:
        chat = Chat(id=str(uuid.uuid4()))
        db.add(chat)
        db.commit()
        db.refresh(chat)
    
    #again add the user message into db
    usr_message = Message(
        chat_id=chat.id,
        role="user",
        content=message.content
    )
    db.add(usr_message)
    db.commit()


    messages_to_send = [
        {"role": "system", "content": INTENT_CLASSIFIER_SYSTEM_PROMPT}
    ]

    msg_history = (
        db.query(Message)
        .filter(Message.chat_id == chat.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    for msg in msg_history:
        if msg.role == "assistant": #for json response of the assistant
            import json
            messages_to_send.append({
                "role": msg.role,
                "content": json.dumps(msg.content)
            })
        else: #for user message(string)
            messages_to_send.append({
                "role": msg.role,
                "content": msg.content
            })

    #now call the llm for assistant response
    llm_response = groq_client.chat.completions.create(
        model="moonshotai/kimi-k2-instruct-0905",
        messages=messages_to_send
    )

    assistant_reply = llm_response.choices[0].message.content
  
    validated_reply = LLMResponse.model_validate_json(assistant_reply)
    
    assistant_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=validated_reply.model_dump()
    )
    db.add(assistant_msg)
    db.commit()

    #return json format 
    import json
    result = validated_reply.model_dump() 
   
    return {
        "chat_id": chat.id,
        "reply": result
    }
    



