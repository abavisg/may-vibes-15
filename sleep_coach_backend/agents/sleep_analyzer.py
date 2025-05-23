import os
import json
from dotenv import load_dotenv

from models.sleep_entry import SleepEntry
from ollama_client import OllamaClient # Import the new client

# Path for load_dotenv in agents is ../../.env for project root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class SleepAnalyzerAgent:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.analyzer_model_name = os.getenv("OLLAMA_ANALYZER_MODEL_NAME", "tinyllama")

    async def test_ollama_prompt(self) -> list[str]:
        """
        Sends a simple test prompt to Ollama using OllamaClient.
        """
        test_prompt = "Briefly, in one sentence, what is a neural network?"
        print(f"SleepAnalyzerAgent: Sending test prompt via OllamaClient with model {self.analyzer_model_name}")
        try:
            response_data = await self.ollama_client.generate(
                model_name=self.analyzer_model_name,
                prompt=test_prompt,
                stream=False
            )
            llm_response_content = response_data.get("response", "No 'response' field found in Ollama output.")
            print(f"Ollama test response: {llm_response_content}")
            return ["Ollama test successful", llm_response_content]
        except Exception as e:
            # Catching a general exception here as OllamaClient might raise various httpx errors
            error_message = f"Ollama test failed: {str(e)}"
            print(error_message)
            return ["Ollama test failed", error_message]

    async def analyze_sleep_data_with_llm(self, sleep_entry: SleepEntry) -> list[str]:
        """
        Placeholder for LLM-based sleep analysis. Currently calls the test prompt.
        Actual implementation will construct a detailed prompt based on sleep_entry,
        request JSON output, and parse it.
        """
        # For now, let's continue to use the test_ollama_prompt for verifying the new client.
        # We will implement the full analysis prompt and logic in the next step.
        print(f"SleepAnalyzerAgent: analyze_sleep_data_with_llm for {sleep_entry.date} (using test_ollama_prompt via OllamaClient).")
        return await self.test_ollama_prompt()

    async def analyze_sleep_data_with_llm_full(self, sleep_entry: SleepEntry) -> list[str]:
        # This is the original method, we'll use test_ollama_prompt for now
        # We will implement this fully later.
        print(f"SleepAnalyzerAgent: analyze_sleep_data_with_llm called for {sleep_entry.date} - placeholder.")
        return await self.test_ollama_prompt() # For now, let's route the test here 