import httpx
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError # For database errors
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
    analysis_issues: List[str] = []
    coaching_suggestions: List[str] = []

    try:
        # 1. Store sleep data
        collector_agent = SleepCollectorAgent(db_session=db)
        await collector_agent.store_sleep_data(sleep_entry_pydantic)
        
        # 2. Analyze sleep data
        analyzer_agent = SleepAnalyzerAgent(ollama_client=ollama_client)
        analysis_issues = await analyzer_agent.analyze_sleep_data_with_llm(sleep_entry_pydantic)
        # Check if analysis itself failed and returned an error message in the list
        if analysis_issues and analysis_issues[0].startswith("Error:") or analysis_issues[0].startswith("Sleep analysis by LLM failed:"):
            # Allow processing to continue, but the error will be in the response.
            # We could also choose to raise an HTTPException here if critical.
            pass # Error is already captured in analysis_issues

        # 3. Generate coaching suggestions
        coach_agent = CoachAgent(ollama_client=ollama_client)
        coaching_suggestions = await coach_agent.generate_coaching_tips(sleep_entry_pydantic, analysis_issues)
        if coaching_suggestions and coaching_suggestions[0].startswith("Error:") or coaching_suggestions[0].startswith("Coaching tip generation failed:"):
            # Allow processing to continue, error captured in coaching_suggestions
            pass
        
        return {
            "message": "Sleep data submitted, analyzed, and suggestions generated.",
            "submitted_data": sleep_entry_pydantic.model_dump(),
            "analysis": analysis_issues,
            "suggestions": coaching_suggestions
        }
    except httpx.RequestError as e:
        # Network error communicating with Ollama
        print(f"Ollama connection error: {e}")
        raise HTTPException(status_code=503, detail=f"Could not connect to Ollama service: {str(e)}")
    except httpx.HTTPStatusError as e:
        # HTTP error from Ollama (e.g., model not found, bad request)
        print(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        error_detail = f"Ollama API error: Status {e.response.status_code}"
        try:
            ollama_error = e.response.json()
            if ollama_error and "error" in ollama_error:
                error_detail += f" - {ollama_error['error']}"
        except Exception:
            error_detail += f" - {e.response.text[:100]}..." # Truncate long raw responses
        raise HTTPException(status_code=e.response.status_code, detail=error_detail)
    except SQLAlchemyError as e:
        # Database related error
        print(f"Database error: {e}")
        # Potentially rollback session, though get_db might handle this with a context manager approach in a real app
        # For now, just report a generic server error for DB issues
        raise HTTPException(status_code=500, detail=f"A database error occurred: {str(e)}")
    except Exception as e:
        # Catch-all for any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")

# Final response structure is now complete as per system overview. 