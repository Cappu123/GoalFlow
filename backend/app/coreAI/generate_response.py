from .prompts.ai_prompts import INTENT_CLASSIFIER_SYSTEM_PROMPT
from groq import Groq
from langchain_core.output_parsers import PydanticOutputParser
from fastapi import FastAPI, Depends, APIRouter, HTTPException, Response, BackgroundTasks
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

def generate_response(db: Session, message: CreateChat)->Chat:

    if message.chat_id:
        chat = db.query(Chat).filter(Chat.id == message.chat_id).first()
    else:
        chat = None

    if not chat:
        #create and add chat into db
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

    history = (
        db.query(Message)
        .filter(Message.chat_id == chat.id)
        .order_by(Message.created_at.asc())
        .all()
    )

    for msg in history:
        if msg.role == "assistant":
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
    return {
        "chat_id": chat.id,
        "reply": validated_reply.model_dump()  
        }





# @router.post("/request_chat")
# def classify_intent(payload: UserInput, db: Session = Depends(get_db)):
#     #try fetch current chat_id from localstorate
#     chat_ID = ##help me this part retrieve chat_id from local storage??
#     if not chat_ID:
#         chat_ID = str(uuid.uuid4())        
#     conversation = db.query(models.Chat).filter(models.Chat.chat_id == chat_ID)

#     if not conversation:
 
#         generated_result = generate_response(payload)
#         .messages.append(
#             {"role": "user", "content": payload}
#         )
#         conversation.messages.append(
#             {"role": "assistant", "content": generated_result}
#         )
#         db.commit()
#         return generated_result
    
#     # response = groq_client.chat.completions.create(
#     #     model="moonshotai/kimi-k2-instruct-0905",
#     #     messages=[
#     #         {"role": "system", "content": INTENT_CLASSIFIER_SYSTEM_PROMPT},
#     #         {"role": "user", "content": user_request}
#     #     ]
#     # )
#     # import json

#     # raw_output = response.choices[0].message.content
#     # parsed_output = json.loads(raw_output)
#     # return parsed_output
