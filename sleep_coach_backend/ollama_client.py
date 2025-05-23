import os
import httpx
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any

# Load .env file. Assuming it's at the project root.
# For a file in sleep_coach_backend/, ../.env should point to the root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class OllamaClient:
    def __init__(self, client: httpx.AsyncClient):
        self.api_url = os.getenv("OLLAMA_API_URL")
        if not self.api_url:
            raise ValueError("OLLAMA_API_URL not found in environment variables.")
        self.http_client = client

    async def generate(
        self, 
        model_name: str, 
        prompt: str, 
        stream: bool = False,
        output_format: Optional[str] = None # e.g., "json"
    ) -> Dict[str, Any]:
        """
        Sends a prompt to the specified Ollama model and returns the response.
        
        Args:
            model_name: The name of the Ollama model to use.
            prompt: The prompt string to send to the model.
            stream: Whether to stream the response (default: False).
            output_format: The desired output format (e.g., "json").

        Returns:
            A dictionary containing the parsed JSON response from Ollama.
        
        Raises:
            HTTPStatusError: If the API request returns an error status code.
            RequestError: For other request-related issues (e.g., network).
            JSONDecodeError: If the response cannot be parsed as JSON.
        """
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": stream,
        }
        if output_format:
            payload["format"] = output_format
            
        print(f"OllamaClient: Sending prompt to model {model_name} at {self.api_url}. Format: {output_format or 'text'}")

        try:
            response = await self.http_client.post(self.api_url, json=payload, timeout=60.0) # Increased timeout
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            response_data = response.json()
            # Log the full response for debugging if needed, then extract relevant part
            # print(f"Full Ollama Response Data: {response_data}") 
            return response_data
            
        except httpx.HTTPStatusError as e:
            error_message = f"Ollama API request failed with status {e.response.status_code}: {e.response.text}"
            print(error_message)
            # Re-raise or handle more gracefully depending on desired behavior
            raise  
        except httpx.RequestError as e:
            error_message = f"Ollama API request (network/connection) failed: {str(e)}"
            print(error_message)
            raise
        except json.JSONDecodeError as e:
            error_message = f"Failed to parse Ollama response as JSON: {str(e)}. Response text: {response.text if 'response' in locals() else 'N/A'}"
            print(error_message)
            raise 