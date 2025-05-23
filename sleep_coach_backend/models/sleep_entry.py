from pydantic import BaseModel
from datetime import datetime, time

class SleepEntry(BaseModel):
    user_id: str
    date: datetime
    bedtime: time
    wakeup_time: time
    sleep_duration: float  # in hours
    awakenings: int = 0
    sleep_quality_rating: int  # e.g., 1-5 scale 