"""
LLM Service module for the Life To Do application.

This module handles communication with the Ollama LLM service,
including sending prompts and processing responses.
"""
import json
import logging
from typing import Dict, List, Any
import ollama
import requests


logger = logging.getLogger(__name__)


class LLMServiceError(Exception):
    """Custom exception for LLM service-related errors."""
    pass


class LLMService:
    """
    Service class for interacting with the Ollama LLM.
    """
    
    def __init__(self, model_name: str = "llama2"):
        """
        Initialize the LLM service with a specific model.
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self._validate_connection()
    
    def _validate_connection(self) -> bool:
        """
        Validate connection to the Ollama service.
        
        Returns:
            bool: True if connection is successful
            
        Raises:
            LLMServiceError: If connection to Ollama fails
        """
        try:
            ollama.list()
            return True
        except (ollama.ResponseError, requests.exceptions.ConnectionError) as e:
            raise LLMServiceError(f"Could not connect to Ollama server: {e}")
    
    def _create_goal_extraction_prompt(self, text: str) -> str:
        """
        Creates a prompt for extracting goals from text.
        
        Args:
            text: Input text to analyze for goals
            
        Returns:
            str: Formatted prompt for goal extraction
        """
        return f"""You are a goal planning assistant. Your task is to analyze the provided text. If the text describes goals, tasks, or plans, extract them into a JSON object. Each goal should have a 'name' (string), 'description' (string), 'priority' (string, e.g., 'High', 'Medium', 'Low'), and an optional 'depends_on' (list of strings, names of goals this goal depends on). If the text is a general question or statement not related to defining goals, respond conversationally in plain text.

Example JSON structure for goals:
{{"goals": [
    {{"name": "Learn Python", "description": "Master Python programming", "priority": "High", "depends_on": []}},
    {{"name": "Build Web App", "description": "Develop a full-stack web application", "priority": "Medium", "depends_on": ["Learn Python"]}}
]}}

Text to analyze: {text}
"""
    
    def extract_goals_from_text(self, text: str, model_name: str = None) -> List[Dict[str, Any]]:
        """
        Extract goals from the provided text using the LLM.

        Args:
            text: Input text to analyze for goals
            model_name: Specific model to use (defaults to instance model if not provided)

        Returns:
            List of dictionaries representing goals

        Raises:
            ValueError: If text is invalid
            LLMServiceError: If there's an error with the LLM service
        """
        if not text or not isinstance(text, str):
            raise ValueError("Text must be a non-empty string")

        text = text.strip()
        if not text:
            raise ValueError("Text cannot be empty after stripping whitespace")

        try:
            prompt = self._create_goal_extraction_prompt(text)
            messages = [{'role': 'user', 'content': prompt}]

            # Use provided model name or fall back to instance model
            model_to_use = model_name if model_name else self.model_name

            # Validate model exists before calling
            available_models = self.list_available_models()
            if model_to_use not in available_models:
                raise LLMServiceError(f"Model '{model_to_use}' is not available. Available models: {available_models}")

            response = ollama.chat(model=model_to_use, messages=messages)
            llm_response_content = response['message']['content']

            # Find JSON in response
            json_start = llm_response_content.find('{')
            json_end = llm_response_content.rfind('}')

            if json_start != -1 and json_end != -1 and json_end > json_start:
                json_string = llm_response_content[json_start:json_end + 1]
                parsed_json = json.loads(json_string)

                if "goals" in parsed_json and isinstance(parsed_json["goals"], list):
                    # Validate the goals structure
                    validated_goals = []
                    for goal in parsed_json["goals"]:
                        if isinstance(goal, dict):
                            # Ensure required fields exist
                            name = goal.get('name', '').strip()
                            if name:  # Only add goals with valid names
                                validated_goals.append(goal)

                    return validated_goals

            # If no valid JSON found, return empty list
            return []

        except json.JSONDecodeError as e:
            logger.warning(f"Could not parse JSON from LLM response: {e}")
            return []
        except Exception as e:
            logger.error(f"Error extracting goals from text: {e}")
            raise LLMServiceError(f"Error extracting goals: {e}")

    def get_conversational_response(self, message: str, model_name: str = None) -> str:
        """
        Get a conversational response from the LLM.

        Args:
            message: User's message
            model_name: Specific model to use (defaults to instance model if not provided)

        Returns:
            str: LLM's response

        Raises:
            ValueError: If message is invalid
            LLMServiceError: If there's an error with the LLM service
        """
        if not message or not isinstance(message, str):
            raise ValueError("Message must be a non-empty string")

        message = message.strip()
        if not message:
            raise ValueError("Message cannot be empty after stripping whitespace")

        try:
            messages = [{'role': 'user', 'content': message}]
            # Use provided model name or fall back to instance model
            model_to_use = model_name if model_name else self.model_name

            # Validate model exists before calling
            available_models = self.list_available_models()
            if model_to_use not in available_models:
                raise LLMServiceError(f"Model '{model_to_use}' is not available. Available models: {available_models}")

            response = ollama.chat(model=model_to_use, messages=messages)
            return response['message']['content']
        except Exception as e:
            logger.error(f"Error getting conversational response: {e}")
            raise LLMServiceError(f"Error getting response: {e}")
    
    def list_available_models(self) -> List[str]:
        """
        Get a list of available models from Ollama.
        
        Returns:
            List of model names
        """
        try:
            response = ollama.list()
            models = response.get('models', [])
            return [model.get('model', '') for model in models if model.get('model')]
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise LLMServiceError(f"Error listing models: {e}")