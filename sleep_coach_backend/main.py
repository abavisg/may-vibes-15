import httpx
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Annotated, List

from models.sleep_entry import SleepEntry
from agents.sleep_collector import SleepCollectorAgent
from agents.sleep_analyzer import SleepAnalyzerAgent
from agents.coach_agent import CoachAgent
from db.database import get_db
from ollama_client import OllamaClient

app = FastAPI(title="Sleep Coach Backend")

# Manage httpx.AsyncClient and OllamaClient lifecycle with lifespan events
@app.on_event("startup")
async def startup_event():
    # Create a single httpx.AsyncClient for the app lifetime
    app.state.http_client = httpx.AsyncClient()
    # Create an OllamaClient instance using the http_client
    app.state.ollama_client = OllamaClient(client=app.state.http_client)
    print("FastAPI app started, HTTP client and Ollama client initialized.")

@app.on_event("shutdown")
async def shutdown_event():
    await app.state.http_client.aclose()
    print("FastAPI app shutting down, HTTP client closed.")

# Dependency to get OllamaClient
def get_ollama_client() -> OllamaClient:
    return app.state.ollama_client

@app.post("/submit-sleep")
async def submit_sleep_data_endpoint(
    sleep_entry_pydantic: SleepEntry, 
    db: Annotated[AsyncSession, Depends(get_db)],
    ollama_client: Annotated[OllamaClient, Depends(get_ollama_client)]
) -> Dict[str, Any]:
    """
    Receives sleep data, stores it, analyzes it, and generates coaching suggestions.
    """
    # 1. Store sleep data
    collector_agent = SleepCollectorAgent(db_session=db)
    await collector_agent.store_sleep_data(sleep_entry_pydantic)
    
    # 2. Analyze sleep data
    analyzer_agent = SleepAnalyzerAgent(ollama_client=ollama_client)
    analysis_issues: List[str] = await analyzer_agent.analyze_sleep_data_with_llm(sleep_entry_pydantic)
    
    # 3. Generate coaching suggestions
    coach_agent = CoachAgent(ollama_client=ollama_client)
    coaching_suggestions: List[str] = await coach_agent.generate_coaching_tips(sleep_entry_pydantic, analysis_issues)
    
    return {
        "message": "Sleep data submitted, analyzed, and suggestions generated.",
        "submitted_data": sleep_entry_pydantic.model_dump(),
        "analysis": analysis_issues,
        "suggestions": coaching_suggestions
    }

# Final response structure is now complete as per system overview. 