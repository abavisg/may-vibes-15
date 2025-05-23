from pydantic import BaseModel
from datetime import datetime, date

class SleepEntry(BaseModel):
    date: date
    bedtime: datetime
    waketime: datetime
    duration_minutes: int
    rem_minutes: int
    deep_minutes: int
    core_minutes: int 