# Sleep Coach Backend
💤 Sleep Data Analysis & Coaching API

[SHORT_DESCRIPTION]
Receives sleep data, analyzes it using local LLMs (Ollama), stores it in PostgreSQL, and provides personalized improvement suggestions.

---

## Features

- **Sleep Data Submission** – Accepts sleep data (date, bedtime, waketime, duration, REM, deep, core) via a POST request.
- **Data Storage** – Stores submitted sleep data persistently in a PostgreSQL database using async SQLAlchemy and Alembic for migrations.
- **LLM-Powered Sleep Analysis** – Uses a local LLM (e.g., TinyLlama via Ollama) to analyze sleep data and identify potential quality issues.
- **LLM-Powered Coaching** – Uses a local LLM (e.g., Llama3 via Ollama) to generate personalized sleep improvement tips based on the analysis.
- **Modular Agent-Based Design** – Separates concerns into collector, analyzer, and coach agents.

---

## Tech stack

- **Backend Framework:** FastAPI
- **Data Validation:** Pydantic
- **Database:** PostgreSQL
- **ORM & Migrations:** SQLAlchemy (async), Alembic
- **LLM Orchestration:** Ollama (for running local models like Llama3, Mistral, TinyLlama)
- **HTTP Client:** HTTPX (for communicating with Ollama)
- **Environment Management:** python-dotenv
- **Server:** Uvicorn

---

## Architecture

1.  **FastAPI Application (`main.py`)**: Exposes the `/submit-sleep` endpoint.
2.  **Models (`models/`)**:
    *   `sleep_entry.py`: Pydantic model for API request/response data.
    *   `db_models.py`: SQLAlchemy ORM model for database interaction.
3.  **Agents (`agents/`)**:
    *   `SleepCollectorAgent`: Validates and stores sleep data in PostgreSQL.
    *   `SleepAnalyzerAgent`: Sends sleep data to an LLM (e.g., TinyLlama) via `OllamaClient` to identify issues.
    *   `CoachAgent`: Sends sleep data and identified issues to another LLM (e.g., Llama3) via `OllamaClient` for personalized tips.
4.  **Ollama Client (`ollama_client.py`)**: A dedicated client to interact with the Ollama API (e.g., `http://localhost:11434/api/generate`).
5.  **Database (`db/`)**:
    *   `database.py`: Configures the async database connection (SQLAlchemy) and provides session management.
    *   Alembic (`alembic/`): Manages database schema migrations.
6.  **Data (`data/`)**: Contains sample JSON data for testing.

**Flow:**
`iOS App (External) -> FastAPI Endpoint -> SleepCollectorAgent -> DB`
`FastAPI Endpoint -> SleepAnalyzerAgent -> OllamaClient -> LLM (Analysis) -> FastAPI Endpoint`
`FastAPI Endpoint -> CoachAgent -> OllamaClient -> LLM (Coaching) -> FastAPI Endpoint (Response)`

---

## API Endpoints

- **`POST /submit-sleep`**
    - **Description:** Submits sleep data for storage, analysis, and coaching advice.
    - **Request Body:** JSON object matching the `SleepEntry` model (see `models/sleep_entry.py` for fields like `date`, `bedtime`, `duration_minutes`, etc.).
    - **Response Body:** JSON object containing:
        - `message`: Status message.
        - `submitted_data`: The sleep data that was submitted.
        - `analysis`: A list of sleep quality issues identified by the analyzer LLM.
        - `suggestions`: A list of personalized improvement tips from the coach LLM.

---

## Setup the application

1.  **Clone the repository (if applicable)**
    ```bash
    # git clone <repository_url>
    # cd <project_directory_name> 
    ```

2.  **Create and activate a virtual environment (recommended)**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies**
    (Ensure `requirements.txt` is in the `sleep_coach_backend` subdirectory)
    ```bash
    pip install -r sleep_coach_backend/requirements.txt
    ```

4.  **Set up PostgreSQL Database**
    - Install PostgreSQL if you haven't already.
    - Create a new database (e.g., `sleep_coach_db`).
      ```sql
      -- Example using psql:
      CREATE DATABASE sleep_coach_db;
      ```

5.  **Configure Environment Variables**
    - Create a `.env` file in the project root directory (e.g., alongside this README).
    - Add the following variables, replacing placeholders with your actual values:
      ```env
      DATABASE_URL="postgresql+asyncpg://YOUR_DB_USER:YOUR_DB_PASSWORD@YOUR_DB_HOST:YOUR_DB_PORT/YOUR_DB_NAME"
      OLLAMA_API_URL="http://localhost:11434/api/generate"
      OLLAMA_ANALYZER_MODEL_NAME="tinyllama"  # Or your preferred model for analysis
      OLLAMA_COACH_MODEL_NAME="llama3"      # Or your preferred model for coaching
      ```

6.  **Run Database Migrations**
    - Navigate to the `sleep_coach_backend` directory:
      ```bash
      cd sleep_coach_backend
      ```
    - Run Alembic migrations to create the tables:
      ```bash
      alembic upgrade head
      ```
      (If you get an error about alembic command not found, ensure your virtual environment is active and dependencies are installed.)

7.  **Set up Ollama and Download Models**
    - Install Ollama from [ollama.ai](https://ollama.ai/).
    - Download the LLMs specified in your `.env` file:
      ```bash
      ollama pull tinyllama  # Or OLLAMA_ANALYZER_MODEL_NAME
      ollama pull llama3     # Or OLLAMA_COACH_MODEL_NAME
      ```
    - Ensure Ollama is running.

---

## Run the application

1.  **Start the FastAPI server**
    From the project root directory:
    ```bash
    uvicorn main:app --reload --app-dir sleep_coach_backend
    ```
    The application will typically be available at `http://127.0.0.1:8000`.

2.  **Test the Endpoint**
    Send a POST request to `http://127.0.0.1:8000/submit-sleep` with your sleep data. See `data/sample_sleep_data.json` or the API Endpoints section for the payload structure.
    Example `curl` command (from project root or any terminal):
    ```bash
    curl -X POST "http://127.0.0.1:8000/submit-sleep" \
    -H "Content-Type: application/json" \
    -d '{ # Ensure to use actual valid data based on models/sleep_entry.py
      "date": "2025-05-24",
      "bedtime": "2025-05-23T23:00:00",
      "waketime": "2025-05-24T07:00:00",
      "duration_minutes": 480,
      "rem_minutes": 100,
      "deep_minutes": 70,
      "core_minutes": 310
    }'
    ```

---

## License
MIT

