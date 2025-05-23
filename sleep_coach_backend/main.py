from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from models.sleep_entry import SleepEntry
from agents.sleep_collector import SleepCollectorAgent
from db.database import get_db

app = FastAPI(title="Sleep Coach Backend")

@app.post("/submit-sleep", response_model=SleepEntry) # Use SleepEntry for response model for now
async def submit_sleep_data_endpoint(
    sleep_entry_pydantic: SleepEntry, 
    db: AsyncSession = Depends(get_db)
):
    """
    Receives sleep data, stores it via SleepCollectorAgent.
    (Later will call analyzer and coach)
    """
    collector_agent = SleepCollectorAgent(db_session=db)
    stored_sleep_data_orm = await collector_agent.store_sleep_data(sleep_entry_pydantic)
    
    # For now, we can just return the Pydantic model that was passed in,
    # as a confirmation that it was processed and (presumably) stored.
    # The actual ORM object `stored_sleep_data_orm` has been added to the session which will be committed.
    return sleep_entry_pydantic

# Placeholder for SleepAnalyzerAgent and CoachAgent integration
# We will fill this in later. 