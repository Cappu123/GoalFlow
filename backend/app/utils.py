import hashlib
import json

#A function to change human friendly timeframes eg: 10days to calculation convinient(like 10(int), days(str))
def parse_timeframe(timeframe: str) -> tuple[int, str]:
    value, unit = timeframe.split()
    return int(value), unit.lower()

#A function to check whether if goal is already saved in drafts or actives
def generate_fingerprint(payload: dict) -> str:
    canonical = {
        "goal_title": payload["goal_title"],
        "goal_description": payload["goal_description"],
        "time_frame": payload["time_frame"],
        "milestones": [
            {
                "name": m["milestone_name"],
                "description": m["milestone_description"]
            }
            for m in payload["milestones"]
        ]
    }

    normalized = json.dumps(canonical, sort_keys=True)
    return hashlib.sha256(normalized.encode()).hexdigest()
    