# Sleep Coach Backend

This project is a FastAPI backend service designed to receive sleep data, analyze it, and provide personalized improvement suggestions using a local LLM via Ollama.

## Project Structure

```
sleep_coach_backend/
├── main.py                 # FastAPI application
├── agents/
│   ├── sleep_collector.py  # Handles data collection and storage
│   ├── sleep_analyzer.py   # Analyzes sleep data
│   └── coach_agent.py      # Interacts with LLM for suggestions
├── models/
│   └── sleep_entry.py      # Pydantic model for sleep data
├── db/
│   └── database.py         # Database connection and ORM (if used)
├── requirements.txt        # Project dependencies
├── .env                    # Environment variables (create manually)
└── data/
    └── sample_sleep_data.json # Sample data for testing
```

## Setup and Installation

1.  **Clone the repository (if applicable)**
    ```bash
    # git clone <repository_url>
    # cd sleep_coach_backend
    ```

2.  **Create and activate a virtual environment (recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**
    ```bash
    pip install -r sleep_coach_backend/requirements.txt
    ```

4.  **Create a `.env` file**
    Create a `.env` file in the `sleep_coach_backend` directory. This file will store environment-specific configurations. For example:
    ```env
    # Example .env content (adjust as needed)
    OLLAMA_API_URL="http://localhost:11434/api/generate"
    LLM_MODEL_NAME="mistral"
    ```

## Running the Application

1.  **Start the FastAPI server**
    ```bash
    uvicorn main:app --reload --app-dir sleep_coach_backend
    ```
    The application will typically be available at `http://120.0.0.1:8000`.

## Usage

Send a POST request to the `/submit-sleep/` endpoint with JSON data matching the `SleepEntry` model.

**Example using `curl`:**
```bash
curl -X POST "http://127.0.0.1:8000/submit-sleep/" \
-H "Content-Type: application/json" \
-d '{
  "date": "2025-05-22",
  "bedtime": "2025-05-21T23:15:00",
  "waketime": "2025-05-22T06:30:00",
  "duration_minutes": 435,
  "rem_minutes": 85,
  "deep_minutes": 65,
  "core_minutes": 140
}'
```

This will be expanded as more features are added.

