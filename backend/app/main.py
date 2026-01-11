import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_tables
from config import settings

from routers import chat, user, goal

create_tables()

def main():
    print("This is goalflow api!")

app = FastAPI(
    title="GoalFlow API",
    description="AI powered multi-step personal development workflow system",
    version="1.0"
)
origins = settings.ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(user.router)
app.include_router(goal.router)

if __name__ =="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

@app.get("/")
def root():
    return {"message": "goalflowapi"}



# @app.post("/intent")
# def get_response(payload: IntentRequest):
#     intent = classify_intent(payload.user_request)
#     return {"intent": intent}