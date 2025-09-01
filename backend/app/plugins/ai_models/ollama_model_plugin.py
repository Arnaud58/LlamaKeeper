import json
import logging
from typing import Dict, Any, Optional
import httpx

from app.core.logging_config import error_tracker
from app.utils.ai_model_plugin import BaseAIModelPlugin

class OllamaModelPlugin(BaseAIModelPlugin):
    def __init__(self, base_url: str = "http://localhost:11434/api", model_name: str = "llama2"):
        """
        Initialize Ollama Model Plugin
        
        :param base_url: Base URL for Ollama API
        :param model_name: Name of the model to use
        """
        self._config = {
            "base_url": base_url,
            "model": model_name,
            "timeout": 60.0,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9
        }
        self._model_name = model_name

    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Retrieve metadata about the current model
        
        :return: Dictionary containing model metadata
        """
        return {
            "model_name": self._model_name,
            "provider": "Ollama",
            "base_url": self._config["base_url"],
            "max_tokens": self._config["max_tokens"],
            "generation_params": {
                "temperature": self._config["temperature"],
                "top_p": self._config["top_p"]
            }
        }

    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration parameters for the Ollama model.
        
        :param config: Configuration dictionary to validate
        :return: True if configuration is valid, False otherwise
        """
        # Merge default config with provided config
        merged_config = {**self._config, **config}
        
        # Validate temperature
        if 'temperature' in merged_config:
            temp = merged_config['temperature']
            if not (0 <= temp <= 1):
                logging.warning("Temperature must be between 0 and 1")
                error_tracker.log_error("Invalid temperature", {"value": temp})
                return False
        
        # Validate top_p
        if 'top_p' in merged_config:
            top_p = merged_config['top_p']
            if not (0 <= top_p <= 1):
                logging.warning("Top_p must be between 0 and 1")
                error_tracker.log_error("Invalid top_p", {"value": top_p})
                return False
        
        # Validate max_tokens
        if 'max_tokens' in merged_config:
            max_tokens = merged_config['max_tokens']
            if max_tokens <= 0:
                logging.warning("Max tokens must be positive")
                error_tracker.log_error("Invalid max tokens", {"value": max_tokens})
                return False
        
        return True

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using the Ollama API.
        
        :param prompt: Input prompt for text generation
        :param kwargs: Optional configuration parameters
        :return: Generated text
        :raises Exception: If text generation fails
        """
        # Extract configuration from kwargs or use default
        config = kwargs.get('config', {})
        
        # Validate configuration
        if config:
            if not self.validate_configuration(config):
                raise ValueError("Invalid configuration parameters")
        
        # Merge default and provided config
        generation_config = {**self._config, **config}
        
        # Validate prompt
        if not prompt or not prompt.strip():
            error_tracker.log_error("Empty prompt provided")
            raise ValueError("Prompt cannot be empty")
        
        try:
            async with httpx.AsyncClient(timeout=generation_config.get('timeout', 60.0)) as client:
                response = await client.post(
                    f"{generation_config['base_url']}/generate", 
                    json={
                        "model": generation_config["model"],
                        "prompt": prompt,
                        "temperature": generation_config["temperature"],
                        "top_p": generation_config["top_p"],
                        "max_tokens": generation_config["max_tokens"]
                    }
                )
                
                # Raise an exception for HTTP errors
                response.raise_for_status()
                
                # Log successful text generation
                logging.info(f"Generated text for prompt: {prompt[:50]}...")
                
                # Parse and return the generated text
                return response.text
        
        except httpx.HTTPStatusError as e:
            error_tracker.log_error(f"HTTP error during text generation: {str(e)}")
            raise
        
        except Exception as e:
            error_tracker.log_error(f"Unexpected error during text generation: {str(e)}")
            raise
