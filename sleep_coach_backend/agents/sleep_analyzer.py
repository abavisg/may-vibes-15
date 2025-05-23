import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

from models.sleep_entry import SleepEntry
from ollama_client import OllamaClient

# Path for load_dotenv in agents is ../../.env for project root .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if not os.path.exists(dotenv_path):
    # Fallback for cases where .env might be in the same directory as main.py (project root)
    # or if agents are structured differently.
    # This assumes main.py is in sleep_coach_backend/
    dotenv_path_alt = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(dotenv_path_alt):
        dotenv_path = dotenv_path_alt
    else:
        # If still not found, try the current directory of this file (agents/)
        # though this is less likely for typical project structures.
        dotenv_path_cwd = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path_cwd):
            dotenv_path = dotenv_path_cwd
        else:
            # Finally, try the parent of the current file's directory (sleep_coach_backend/)
            dotenv_path_parent_of_agents = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(dotenv_path_parent_of_agents):
                dotenv_path = dotenv_path_parent_of_agents
            else:
                print(f"Warning: .env file not found at primary path: {os.path.join(os.path.dirname(__file__), '..', '..', '.env')} or fallbacks.")
                # Allow to proceed, assuming env vars might be set globally
    load_dotenv(dotenv_path=dotenv_path if os.path.exists(dotenv_path) else None, override=True)

class SleepAnalyzerAgent:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.model_name = os.getenv("OLLAMA_ANALYZER_MODEL_NAME", "tinyllama")
        if ':' not in self.model_name:
            self.model_name += ':latest'
        print(f"SleepAnalyzerAgent initialized with model: {self.model_name}")

    async def _construct_analysis_prompt(self, sleep_entry: SleepEntry) -> str:
        prompt = f"""You are a sleep data checker. Your task is to identify specific sleep quality issues from the provided data based on common thresholds and output ONLY a JSON array of strings listing those issues.

Sleep Data:
- Total Duration: {sleep_entry.duration_minutes} minutes
- REM Sleep: {sleep_entry.rem_minutes} minutes
- Deep Sleep: {sleep_entry.deep_minutes} minutes

Thresholds:
- Issue "Short total sleep": if Total Duration is less than 420 minutes.
- Issue "Low REM sleep": if REM Sleep is less than 90 minutes.
- Issue "Low Deep sleep": if Deep Sleep is less than 60 minutes.

Based *only* on these rules and data, provide your response *strictly* as a JSON array of strings containing the exact issue descriptions if their conditions are met.
For example, if total duration is 300 and REM is 70, output: ["Short total sleep", "Low REM sleep"]
If only deep sleep is 50, output: ["Low Deep sleep"]
If all values are above thresholds, output an empty array: []
Do not add any other text, explanation, or JSON keys. Your entire response must be only the JSON array of issue strings.

Data to analyze:
Total Duration: {sleep_entry.duration_minutes}
REM Sleep: {sleep_entry.rem_minutes}
Deep Sleep: {sleep_entry.deep_minutes}

Output JSON array:""" 
        return prompt

    async def analyze_sleep_data_with_llm(self, sleep_entry: SleepEntry) -> List[str]:
        """
        Analyzes sleep data using an LLM via OllamaClient to identify sleep quality issues.
        Requests JSON output from the LLM and parses it.
        Returns a list of identified issue strings.
        """
        prompt = await self._construct_analysis_prompt(sleep_entry)
        
        print(f"SleepAnalyzerAgent: Analyzing sleep data for {sleep_entry.date} with model {self.model_name}.")
        print(f"Prompt being sent to Analyzer LLM:\n{prompt}")

        try:
            response_data = await self.ollama_client.generate(
                model_name=self.model_name,
                prompt=prompt,
                stream=False,
                output_format="json"
            )
            
            llm_output_str = response_data.get("response")
            if not llm_output_str:
                print("Error: Analyzer LLM response did not contain a 'response' field.")
                return ["Error: Analyzer LLM did not provide a response string."]

            print(f"Analyzer LLM raw output string for issues: {llm_output_str}")
            
            try:
                parsed_llm_json: Any = json.loads(llm_output_str)
                issues_list: List[str] = []

                if isinstance(parsed_llm_json, list):
                    if all(isinstance(item, str) for item in parsed_llm_json):
                        issues_list = parsed_llm_json
                    else:
                        print(f"Warning: Analyzer LLM returned a list, but not all items are strings: {parsed_llm_json}")
                        issues_list = [str(item) for item in parsed_llm_json]
                elif isinstance(parsed_llm_json, dict):
                    print(f"Info: Analyzer LLM returned a JSON object. Will attempt to extract. Object: {parsed_llm_json}")
                    # New logic: If the dict keys seem to be the issues themselves
                    potential_issues_from_keys = list(parsed_llm_json.keys())
                    if all(isinstance(key, str) for key in potential_issues_from_keys):
                        # Check if these keys match the expected issue format (simple heuristic)
                        # This is a simple check; more sophisticated validation could be added.
                        # For now, we assume if keys are strings, they are the issues.
                        issues_list = potential_issues_from_keys
                        print(f"Extracted issues from JSON object keys: {issues_list}")
                        if issues_list: # If we got issues from keys, prioritize this
                            return issues_list

                    # If LLM still wraps, try to find a list within common keys (less ideal for this new prompt)
                    found_key = None
                    for key in ["issues", "slees", "analysis", "results"]:
                        if key in parsed_llm_json:
                            found_key = key
                            break
                        elif key.lower() in (k.lower() for k in parsed_llm_json.keys()):
                            actual_key = next((k for k in parsed_llm_json.keys() if k.lower() == key.lower()), None)
                            if actual_key:
                                found_key = actual_key
                                break
                    if found_key:
                        potential_issues = parsed_llm_json[found_key]
                        if isinstance(potential_issues, list):
                            if potential_issues and isinstance(potential_issues[0], list) and all(isinstance(i,str) for i in potential_issues[0]):
                                issues_list = potential_issues[0]
                            elif all(isinstance(item, str) for item in potential_issues):
                                issues_list = potential_issues
                            else:
                                issues_list = [str(item) for item in potential_issues if isinstance(potential_issues, list)]
                else:
                    print(f"Error: Analyzer LLM output was not a recognized JSON list/dict. Output: {parsed_llm_json}")
                    return ["Error: Analyzer LLM output was not a recognized JSON structure."]

                print(f"Extracted issues by Analyzer LLM: {issues_list}")
                return issues_list

            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse Analyzer LLM's response string as JSON. Error: {e}. LLM String: {llm_output_str}")
                return [f"Error: Could not parse Analyzer LLM JSON output - {llm_output_str}"]

        except Exception as e:
            error_message = f"Sleep analysis by LLM failed: {str(e)}"
            print(error_message)
            return [error_message] 