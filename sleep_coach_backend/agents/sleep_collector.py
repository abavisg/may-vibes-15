from sqlalchemy.ext.asyncio import AsyncSession
from models.sleep_entry import SleepEntry
from models.db_models import SleepOrm # Import the SQLAlchemy model

class SleepCollectorAgent:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def store_sleep_data(self, sleep_entry_pydantic: SleepEntry) -> SleepOrm:
        """Converts Pydantic SleepEntry to SleepOrm and adds to session for commit."""
        # Create a SleepOrm instance from the Pydantic model data
        # The Pydantic model fields directly map to SleepOrm constructor arguments
        sleep_orm_instance = SleepOrm(
            date=sleep_entry_pydantic.date,
            bedtime=sleep_entry_pydantic.bedtime,
            waketime=sleep_entry_pydantic.waketime,
            duration_minutes=sleep_entry_pydantic.duration_minutes,
            rem_minutes=sleep_entry_pydantic.rem_minutes,
            deep_minutes=sleep_entry_pydantic.deep_minutes,
            core_minutes=sleep_entry_pydantic.core_minutes
        )
        
        self.db_session.add(sleep_orm_instance)
        # The commit will be handled by the get_db dependency after the endpoint function finishes
        # We can flush to get the ID if needed, but let's keep it simple for now.
        # await self.db_session.flush() 
        # await self.db_session.refresh(sleep_orm_instance) 
        
        print(f"SleepOrm instance for date {sleep_orm_instance.date} added to session.") # Temporary
        return sleep_orm_instance # Return the ORM instance, it might be useful 