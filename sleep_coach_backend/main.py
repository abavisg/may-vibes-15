from fastapi import FastAPI
from models.sleep_entry import SleepEntry

app = FastAPI()

@app.post("/submit-sleep")
async def submit_sleep_data(sleep_entry: SleepEntry):
    # This will eventually trigger the SleepCollectorAgent, SleepAnalyzerAgent, and CoachAgent
    # For now, we'll just return a confirmation.
    return {"message": "Sleep data submitted successfully", "data": sleep_entry}

# Placeholder for Ollama interaction and other logic
# We will fill this in later. 