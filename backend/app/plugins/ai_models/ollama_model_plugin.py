import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from app.utils.ai_model_plugin import BaseAIModelPlugin
from app.utils.ollama_client import OllamaClient
from app.utils.plugin_discovery import plugin_discoverable


@plugin_discoverable(BaseAIModelPlugin)
class OllamaModelPlugin(BaseAIModelPlugin):
    """
    Concrete implementation of Ollama AI Model Plugin
    Provides advanced Ollama model integration with enhanced capabilities
    """

    def __init__(
        self, model_name: str = "llama2", config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize Ollama model plugin

        Args:
            model_name (str): Name of the Ollama model
            config (Dict, optional): Model-specific configuration
        """
        super().__init__(model_name, config or {})

        # Default configuration
        self._default_config = {
            "base_url": "http://localhost:11434/api",
            "timeout": 60.0,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        # Merge default and provided configuration
        self._config = {**self._default_config, **self._config}

        # Initialize Ollama client
        self._ollama_client = OllamaClient(
            base_url=self._config["base_url"],
            timeout=self._config["timeout"],
            default_model=model_name,
        )

        # Setup logging
        self._logger = logging.getLogger(f"OllamaModelPlugin.{model_name}")
        self._logger.setLevel(logging.INFO)

    async def generate_text(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate text using the Ollama model

        Args:
            prompt (str): Input prompt for text generation
            context (Dict, optional): Contextual information for generation
            parameters (Dict, optional): Model-specific generation parameters

        Returns:
            str: Generated text
        """
        try:
            # Merge default and provided parameters
            generation_params = {
                "max_tokens": self._config["max_tokens"],
                "temperature": self._config["temperature"],
                "top_p": self._config["top_p"],
            }

            if parameters:
                generation_params.update(parameters)

            # Generate text using Ollama client
            generated_text = await self._ollama_client.generate_text(
                prompt=prompt, model=self._model_name, **generation_params
            )

            self._logger.info(f"Generated text for prompt: {prompt[:50]}...")
            return generated_text

        except Exception as e:
            self._logger.error(f"Text generation error: {e}")
            raise

    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive metadata about the Ollama model

        Returns:
            Dict: Model metadata (capabilities, version, etc.)
        """
        metadata = super().get_model_metadata()

        # Add Ollama-specific metadata
        metadata.update(
            {
                "provider": "Ollama",
                "base_url": self._config["base_url"],
                "max_tokens": self._config["max_tokens"],
                "generation_params": {
                    "temperature": self._config["temperature"],
                    "top_p": self._config["top_p"],
                },
            }
        )

        return metadata

    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration for the Ollama model

        Args:
            config (Dict): Model configuration parameters

        Returns:
            bool: Whether the configuration is valid
        """
        # Validate base configuration
        if not super().validate_configuration(config):
            return False

        # Ollama-specific validations
        try:
            # Validate temperature
            if "temperature" in config:
                temp = config["temperature"]
                if not (0 <= temp <= 1):
                    self._logger.warning("Temperature must be between 0 and 1")
                    return False

            # Validate top_p
            if "top_p" in config:
                top_p = config["top_p"]
                if not (0 <= top_p <= 1):
                    self._logger.warning("Top_p must be between 0 and 1")
                    return False

            # Validate max_tokens
            if "max_tokens" in config:
                max_tokens = config["max_tokens"]
                if max_tokens <= 0:
                    self._logger.warning("Max tokens must be positive")
                    return False

            return True

        except Exception as e:
            self._logger.error(f"Configuration validation error: {e}")
            return False

    async def __aenter__(self):
        """
        Async context manager entry method
        Ensures Ollama client is ready
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit method
        Closes Ollama client
        """
        await self._ollama_client.close()
