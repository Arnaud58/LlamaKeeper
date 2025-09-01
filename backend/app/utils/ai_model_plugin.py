import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseAIModelPlugin(ABC):
    """
    Base implementation of AbstractAIModelPlugin
    Provides default implementations and logging for AI model plugins
    """

    def __init__(self, model_name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the AI model plugin

        Args:
            model_name (str): Name of the AI model
            config (Dict, optional): Configuration parameters for the model
        """
        self._model_name = model_name
        self._config = config or {}
        self._logger = logging.getLogger(f"AIModelPlugin.{model_name}")

        # Validate configuration during initialization
        if not self.validate_configuration(self._config):
            self._logger.warning(f"Invalid configuration for model {model_name}")

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate text using the AI model

        Args:
            prompt (str): Input prompt for text generation
            context (Dict, optional): Contextual information for generation
            parameters (Dict, optional): Model-specific generation parameters

        Returns:
            str: Generated text
        """
        pass

    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive metadata about the AI model

        Returns:
            Dict: Model metadata (capabilities, version, etc.)
        """
        return {
            "model_name": self._model_name,
            "config": self._config,
            "plugin_type": self.__class__.__name__,
        }

    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration for the AI model

        Default implementation checks for basic configuration requirements
        Can be overridden by specific model plugins for more complex validation

        Args:
            config (Dict): Model configuration parameters

        Returns:
            bool: Whether the configuration is valid
        """
        # Basic validation: config should be a dictionary
        if not isinstance(config, dict):
            self._logger.error("Configuration must be a dictionary")
            return False

        return True

    async def __aenter__(self):
        """
        Async context manager entry method
        Can be used for resource initialization
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit method
        Can be used for resource cleanup
        """
        pass
