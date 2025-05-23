import os
import json
from dotenv import load_dotenv
from typing import List, Dict, Any

from models.sleep_entry import SleepEntry
from ollama_client import OllamaClient

# Load .env from the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
if not os.path.exists(dotenv_path):
    dotenv_path_alt = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(dotenv_path_alt):
        dotenv_path = dotenv_path_alt
    else:
        dotenv_path_cwd = os.path.join(os.path.dirname(__file__), '.env')
        if os.path.exists(dotenv_path_cwd):
            dotenv_path = dotenv_path_cwd
        else:
            dotenv_path_parent_of_agents = os.path.join(os.path.dirname(__file__), '..', '.env')
            if os.path.exists(dotenv_path_parent_of_agents):
                dotenv_path = dotenv_path_parent_of_agents
            else:
                print(f"Warning: .env file not found at primary path: {os.path.join(os.path.dirname(__file__), '..', '..', '.env')} or fallbacks.")
load_dotenv(dotenv_path=dotenv_path if os.path.exists(dotenv_path) else None, override=True)

class CoachAgent:
    def __init__(self, ollama_client: OllamaClient):
        self.ollama_client = ollama_client
        self.model_name = os.getenv("OLLAMA_COACH_MODEL_NAME", "llama3")  # Default to llama3 as per original spec
        if ':' not in self.model_name:
            self.model_name += ':latest'
        print(f"CoachAgent initialized with model: {self.model_name}")

    async def _construct_coaching_prompt(self, sleep_entry: SleepEntry, issues: List[str]) -> str:
        issues_str = ", ".join(issues) if issues else "No specific issues identified, but general sleep quality can always be improved."
        
        prompt = f"""SYSTEM: You are a helpful and concise sleep coach.
USER: My recent sleep data is as follows:
- Date: {sleep_entry.date.isoformat()}
- Bedtime: {sleep_entry.bedtime.isoformat()}
- Waketime: {sleep_entry.waketime.isoformat()}
- Total Duration: {sleep_entry.duration_minutes} minutes
- REM Sleep: {sleep_entry.rem_minutes} minutes
- Deep Sleep: {sleep_entry.deep_minutes} minutes
- Core Sleep: {sleep_entry.core_minutes} minutes

Identified issues from my sleep analysis: {issues_str}

Suggest exactly 3 actionable and personalized tips to help me improve my sleep quality, focusing on the identified issues if any. 
Return your response strictly as a JSON array of 3 strings. For example: ["Tip 1 about issue X", "Tip 2 about issue Y", "Tip 3 general advice"].
Do not wrap the array in any other JSON object. The output should be the array itself.
"""
        return prompt

    async def generate_coaching_tips(self, sleep_entry: SleepEntry, issues: List[str]) -> List[str]:
        prompt = await self._construct_coaching_prompt(sleep_entry, issues)
        
        print(f"CoachAgent: Generating coaching tips with model {self.model_name}.")
        print(f"Prompt being sent:\n{prompt}")

        try:
            response_data = await self.ollama_client.generate(
                model_name=self.model_name,
                prompt=prompt,
                stream=False,
                output_format="json"  # Request JSON output
            )
            
            llm_output_str = response_data.get("response")
            if not llm_output_str:
                print("Error: Coach LLM response did not contain a 'response' field.")
                return ["Error: Coach LLM did not provide a response string."]

            print(f"Coach LLM raw output string for tips: {llm_output_str}")
            
            try:
                # Attempt to parse the string as JSON. It might be a JSON object or directly a JSON array string.
                parsed_llm_json: Any = json.loads(llm_output_str)
                tips_list: List[str] = []

                if isinstance(parsed_llm_json, list):
                    if all(isinstance(item, str) for item in parsed_llm_json):
                        tips_list = parsed_llm_json
                    else:
                        print(f"Warning: Coach LLM returned a list, but not all items are strings: {parsed_llm_json}")
                        tips_list = [str(item) for item in parsed_llm_json] # Fallback
                elif isinstance(parsed_llm_json, dict):
                    print(f"Info: Coach LLM returned a JSON object. Attempting to extract tips list. Object: {parsed_llm_json}")
                    # New logic: if the dict values are the tips themselves
                    potential_tips_from_values = list(parsed_llm_json.values())
                    if all(isinstance(value, str) for value in potential_tips_from_values):
                        tips_list = potential_tips_from_values
                        print(f"Extracted tips from JSON object values: {tips_list}")
                    else:
                        # Try to find a list of strings within the dict, similar to SleepAnalyzerAgent
                        found_key = None
                        for key_attempt in ["tips", "suggestions", "response"]:
                            if key_attempt in parsed_llm_json and isinstance(parsed_llm_json[key_attempt], list) and all(isinstance(i,str) for i in parsed_llm_json[key_attempt]):
                                found_key = key_attempt
                                break
                        if found_key:
                            tips_list = parsed_llm_json[found_key]
                        else:
                            print("Warning: Coach LLM returned a JSON object, but no known tips key with a list of strings found, and values were not all strings.")
                else:
                    print(f"Error: Coach LLM output was neither a list nor a dict after JSON parsing. Output: {parsed_llm_json}")
                    return ["Error: Coach LLM output was not a recognized JSON structure."]
                
                # Ensure we return exactly 3 tips if possible, or pad/truncate if LLM misbehaves
                if len(tips_list) > 3:
                    tips_list = tips_list[:3]
                # elif len(tips_list) < 3 and len(tips_list) > 0: # Don't pad if LLM gave specific (but fewer) valid tips
                #    tips_list.extend(["Consider general sleep hygiene."] * (3 - len(tips_list)))
                elif not tips_list: # LLM failed to provide valid tips
                    tips_list = ["Could not generate specific tips at this time. Please review your sleep habits."]

                print(f"Generated tips: {tips_list}")
                return tips_list

            except json.JSONDecodeError as e:
                print(f"Error: Failed to parse Coach LLM's response string as JSON. Error: {e}. LLM String: {llm_output_str}")
                return [f"Error: Could not parse Coach LLM JSON output - {llm_output_str}"]

        except Exception as e:
            error_message = f"Coaching tip generation failed: {str(e)}"
            print(error_message)
            return [error_message] 