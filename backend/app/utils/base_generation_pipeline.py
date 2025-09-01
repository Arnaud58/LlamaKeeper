import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseGenerationPipeline(ABC):
    """
    Base implementation of AbstractGenerationPipeline
    Provides a flexible framework for narrative generation
    """

    def __init__(
        self,
        logger_name: str = "GenerationPipeline",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the generation pipeline

        Args:
            logger_name (str, optional): Name for the logger
            config (Dict, optional): Configuration parameters for the pipeline
        """
        self._logger = logging.getLogger(logger_name)
        self._config = config or {}
        self._pipeline_id = str(uuid.uuid4())

        # Log pipeline initialization
        self._logger.info(f"Generation Pipeline {self._pipeline_id} initialized")

    @abstractmethod
    async def generate_story_progression(
        self,
        current_story: Dict[str, Any],
        characters: List[Dict[str, Any]],
        narrative_goals: List[str],
    ) -> Dict[str, Any]:
        """
        Generate progression for an ongoing story

        Args:
            current_story (Dict): Current story state
            characters (List[Dict]): Characters in the story
            narrative_goals (List[str]): Desired narrative directions

        Returns:
            Dict: Story progression details
        """
        pass

    @abstractmethod
    async def generate_character_interaction(
        self,
        initiating_character: Dict[str, Any],
        target_character: Dict[str, Any],
        interaction_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate an interaction between two characters

        Args:
            initiating_character (Dict): Character starting the interaction
            target_character (Dict): Character being interacted with
            interaction_context (Dict): Context of the interaction

        Returns:
            Dict: Character interaction details
        """
        pass

    def _validate_story_context(self, story_context: Dict[str, Any]) -> bool:
        """
        Validate the story context

        Args:
            story_context (Dict): Story context to validate

        Returns:
            bool: Whether the context is valid
        """
        if not isinstance(story_context, dict):
            self._logger.warning("Story context must be a dictionary")
            return False

        # Add more specific validation as needed
        return True

    def _validate_characters(self, characters: List[Dict[str, Any]]) -> bool:
        """
        Validate the characters involved in the story

        Args:
            characters (List[Dict]): Characters to validate

        Returns:
            bool: Whether the characters are valid
        """
        if not isinstance(characters, list):
            self._logger.warning("Characters must be a list")
            return False

        for character in characters:
            if not isinstance(character, dict):
                self._logger.warning("Each character must be a dictionary")
                return False

            if "name" not in character:
                self._logger.warning("Each character must have a name")
                return False

        return True

    def serialize_generation_result(self, result: Dict[str, Any]) -> str:
        """
        Serialize a generation result to a JSON string

        Args:
            result (Dict): Generation result to serialize

        Returns:
            str: JSON representation of the result
        """
        try:
            return json.dumps(result, default=str)
        except TypeError as e:
            self._logger.error(f"Failed to serialize generation result: {e}")
            raise

    def deserialize_generation_result(self, serialized_result: str) -> Dict[str, Any]:
        """
        Deserialize a generation result from a JSON string

        Args:
            serialized_result (str): JSON string representing a generation result

        Returns:
            Dict: Deserialized generation result
        """
        try:
            return json.loads(serialized_result)
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to deserialize generation result: {e}")
            raise

    def update_pipeline_config(self, new_config: Dict[str, Any]) -> None:
        """
        Update the pipeline configuration

        Args:
            new_config (Dict): New configuration parameters
        """
        self._config.update(new_config)
        self._logger.info("Pipeline configuration updated")

    def __repr__(self) -> str:
        """
        String representation of the generation pipeline

        Returns:
            str: Descriptive string of the generation pipeline
        """
        return f"GenerationPipeline(id={self._pipeline_id})"
