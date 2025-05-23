import os
from dotenv import load_dotenv
from typing import List

from models.sleep_entry import SleepEntry
from ollama_client import OllamaClient

# Path for load_dotenv in agents is ../../.env for project root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class CoachAgent:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.coach_model_name = os.getenv("OLLAMA_COACH_MODEL_NAME", "mistral") # Default to mistral

        if not self.coach_model_name:
            # This case should ideally not be hit if default is provided and .env is read
            print("Warning: OLLAMA_COACH_MODEL_NAME not found, defaulting to 'mistral' explicitly.")
            self.coach_model_name = "mistral"

    async def generate_coaching_tips(self, sleep_entry: SleepEntry, issues: List[str]) -> List[str]:
        """
        Generates personalized coaching tips based on sleep data and identified issues
        using an LLM (e.g., Mistral or Llama3 via Ollama).
        Returns a list of tip strings.
        """
        # 1. Construct the prompt for the LLM based on sleep_entry and issues.
        # 2. Make the API call to Ollama via OllamaClient.
        # 3. Parse the LLM response to extract a list of tips.
        
        # Placeholder implementation:
        print(f"CoachAgent: Generating tips for issues: {issues} with model {self.coach_model_name}")
        # This will be replaced with actual LLM call and parsing
        placeholder_tips = [
            f"Placeholder tip 1 for {issues[0] if issues else 'general sleep'}",
            f"Placeholder tip 2 for {issues[0] if issues else 'general sleep'}",
            "Placeholder tip 3: Ensure a consistent sleep schedule."
        ]
        return placeholder_tips 