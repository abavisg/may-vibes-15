import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

from models.sleep_entry import SleepEntry
from ollama_client import OllamaClient

# Path for load_dotenv in agents is ../../.env for project root .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

class SleepAnalyzerAgent:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.analyzer_model_name = os.getenv("OLLAMA_ANALYZER_MODEL_NAME", "tinyllama")

    async def _construct_analysis_prompt(self, sleep_entry: SleepEntry) -> str:
        prompt = f"""You are a sleep analysis assistant.
Based on the following sleep data, identify any potential sleep quality issues.

Sleep Data:
- Date: {sleep_entry.date.isoformat()}
- Bedtime: {sleep_entry.bedtime.isoformat()}
- Waketime: {sleep_entry.waketime.isoformat()}
- Total Duration: {sleep_entry.duration_minutes} minutes
- REM Sleep: {sleep_entry.rem_minutes} minutes
- Deep Sleep: {sleep_entry.deep_minutes} minutes
- Core Sleep: {sleep_entry.core_minutes} minutes

Common thresholds for adult sleep are:
- Total Duration: At least 420 minutes (7 hours).
- REM Sleep: At least 90 minutes.
- Deep Sleep: At least 60 minutes.

List the identified issues strictly as a JSON array of strings. For example: ["Issue 1", "Issue 2"].
If no significant issues are found based on these common thresholds, return an empty array [].
Do not wrap the array in any other JSON object. The output should be the array itself.
"""
        return prompt

    async def analyze_sleep_data_with_llm(self, sleep_entry: SleepEntry) -> List[str]:
        """
        Analyzes sleep data using an LLM via OllamaClient to identify sleep quality issues.
        Requests JSON output from the LLM and parses it.
        Returns a list of identified issue strings.
        """
        prompt = await self._construct_analysis_prompt(sleep_entry)
        
        print(f"SleepAnalyzerAgent: Analyzing sleep data for {sleep_entry.date} with model {self.analyzer_model_name}.")
        print(f"Prompt being sent:\n{prompt}")

        try:
            response_data = await self.ollama_client.generate(
                model_name=self.analyzer_model_name,
                prompt=prompt,
                stream=False,
                output_format="json"  # Request JSON output from Ollama
            )
            
            # The 'response' field from Ollama (when format="json") should contain a string 
            # that is itself a JSON formatted list of strings.
            llm_output_str = response_data.get("response")
            if not llm_output_str:
                print("Error: LLM response did not contain a 'response' field.")
                return ["Error: LLM did not provide a response string."]

            print(f"LLM raw output string for issues: {llm_output_str}")
            
            # Parse the LLM's string output (which should be a JSON array string)
            try:
                # Attempt to parse the string as JSON. It might be a JSON object or directly a JSON array string.
                parsed_llm_json: Any = json.loads(llm_output_str)

                issues_list: List[str] = []

                if isinstance(parsed_llm_json, list):
                    # Ideal case: LLM returned a direct JSON array of strings
                    if all(isinstance(item, str) for item in parsed_llm_json):
                        issues_list = parsed_llm_json
                    else:
                        print(f"Warning: LLM returned a list, but not all items are strings: {parsed_llm_json}")
                        # Attempt to stringify non-string items or handle as error
                        issues_list = [str(item) for item in parsed_llm_json] # Convert all to string as a fallback
                elif isinstance(parsed_llm_json, dict):
                    # Case: LLM returned a JSON object like {"slees": [["Issue 1"]], ...} or {"issues": [...]} 
                    print(f"Info: LLM returned a JSON object. Attempting to extract issues list. Object: {parsed_llm_json}")
                    # Try common keys, case-insensitive, and handle potential nesting
                    found_key = None
                    for key in ["issues", "slees", "analysis", "results"]:
                        if key in parsed_llm_json:
                            found_key = key
                            break
                        elif key.lower() in (k.lower() for k in parsed_llm_json.keys()):
                             # a bit more robust key finding
                            actual_key = next((k for k in parsed_llm_json.keys() if k.lower() == key.lower()), None)
                            if actual_key:
                                found_key = actual_key
                                break
                    
                    if found_key:
                        potential_issues = parsed_llm_json[found_key]
                        if isinstance(potential_issues, list):
                            if potential_issues and isinstance(potential_issues[0], list) and all(isinstance(i,str) for i in potential_issues[0]):
                                # Handles cases like [["Issue 1", "Issue 2"]]
                                issues_list = potential_issues[0]
                            elif all(isinstance(item, str) for item in potential_issues):
                                # Handles cases like ["Issue 1", "Issue 2"]
                                issues_list = potential_issues
                            else:
                                print(f"Warning: Found list for key '{found_key}', but items are not all strings or not a simple list of strings: {potential_issues}")
                                issues_list = [str(item) for item in potential_issues if isinstance(potential_issues, list)] # fallback stringification
                        else:
                             print(f"Warning: Value for key '{found_key}' was not a list: {potential_issues}")
                    else:
                        print("Warning: LLM returned a JSON object, but no known issues key found.")
                else:
                    print(f"Error: LLM output was neither a list nor a dict after JSON parsing. Output: {parsed_llm_json}")
                    return ["Error: LLM output was not a recognized JSON structure (list or dict)."]

                print(f"Extracted issues: {issues_list}")
                return issues_list

            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse LLM's response string as JSON. Error: {e}. LLM String: {llm_output_str}")
                return [f"Error: Could not parse LLM JSON output - {llm_output_str}"]

        except Exception as e:
            error_message = f"Sleep analysis failed due to an error: {str(e)}"
            print(error_message)
            return [error_message] # Return the error message as an issue 