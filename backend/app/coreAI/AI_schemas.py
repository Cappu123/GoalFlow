from typing import List, Optional, Dict, Literal
from datetime import datetime
from pydantic import BaseModel, json



class LLMResponse(BaseModel):
    intent: Literal["casual", "create_goal", "update_progress", "ask_help"]
    payload: dict