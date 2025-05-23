from sqlalchemy import Column, Integer, DateTime, Date
from db.database import Base # Adjusted import path assuming db_models.py is in models/

class SleepOrm(Base):
    __tablename__ = "sleep_entries"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    bedtime = Column(DateTime, nullable=False)
    waketime = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    rem_minutes = Column(Integer, nullable=False)
    deep_minutes = Column(Integer, nullable=False)
    core_minutes = Column(Integer, nullable=False)

    def __repr__(self):
        return f"<SleepOrm(id={self.id}, date='{self.date}')>" 