import hashlib
import json
from datetime import datetime, timedelta

#A function to change human friendly timeframes eg: 10days to calculation convinient(like 10(int), days(str))
def parse_timeframe(timeframe: str) -> tuple[int, str]:
    value, unit = timeframe.split()
    return int(value), unit.lower()

#A function to help check whether if goal is already saved in drafts or actives
def generate_fingerprint(payload: dict) -> str:
    # canonical = {
    #     "goal_title": payload.get("goal_title"),
    #     "goal_description": payload.get("goal_description"),
    #     "time_frame": payload.get("time_frame"),
    #     "milestones": [
    #         {
    #             "name": m.get("milestone_name"),
    #             "description": m.get("milestone_description")
    #         }
    #         for m in payload.get("milestones", [])
    #     ]
    # }

    normalized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()

def date_formatter(date: datetime | None) -> str:
    if date is None:
        return None
    if isinstance(date, str):
        date = datetime.fromisoformat(date)
    return date.strftime('%B %d, %Y, %I:%M %p' )

 
def calculate_due_date(start_date: datetime, 
                       duration_value: int,
                       duration_unit: str) -> datetime:
    if not start_date:
        raise ValueError(f"Start_date is required")
    unit = duration_unit.lower()

    if unit in ("day", "days"):
        delta = timedelta(days=duration_value)
    elif unit in ("hour", "hours"):
        delta = timedelta(hours=duration_value)
    elif unit in ("minute", "minutes"):
        delta = timedelta(minutes=duration_value)
    elif unit in ("second", "seconds"):
        delta = timedelta(seconds=duration_value)
    else:
        raise ValueError(f"Unsupported duration unit {duration_unit}")
    
    return start_date + delta


