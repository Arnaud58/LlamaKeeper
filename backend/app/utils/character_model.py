import json
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseCharacterModel(ABC):
    """
    Base implementation of AbstractCharacterModel
    Provides a flexible framework for character representation and autonomous behavior
    """

    def __init__(
        self, name: str, personality: Dict[str, Any], background: Optional[str] = None
    ):
        """
        Initialize a character with core attributes

        Args:
            name (str): Character name
            personality (Dict): Character personality traits
            background (str, optional): Character's backstory
        """
        self._id = str(uuid.uuid4())
        self._name = name
        self._personality = personality
        self._background = background
        self._memory_context: Dict[str, Any] = {}

        # Setup logging
        self._logger = logging.getLogger(f"CharacterModel.{name}")

        # Log character initialization
        self._logger.info(f"Character '{name}' initialized")

    def update_personality_trait(self, trait_name: str, trait_value: Any) -> None:
        """
        Update or add a personality trait

        Args:
            trait_name (str): Name of the trait
            trait_value (Any): Value of the trait
        """
        if not isinstance(trait_name, str):
            raise ValueError("Trait name must be a string")

        self._personality[trait_name] = trait_value
        self._logger.info(f"Updated personality trait: {trait_name}")

    @abstractmethod
    def generate_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an autonomous action based on character traits and context

        Args:
            context (Dict): Current story/interaction context

        Returns:
            Dict: Generated character action
        """
        pass

    def get_memory_context(self) -> Dict[str, Any]:
        """
        Retrieve the character's current memory context

        Returns:
            Dict: Character's memory and contextual information
        """
        return {
            "character_id": self._id,
            "name": self._name,
            "personality": self._personality,
            "background": self._background,
            **self._memory_context,
        }

    def _update_memory_context(self, new_context: Dict[str, Any]) -> None:
        """
        Update the character's memory context

        Args:
            new_context (Dict): New contextual information to merge
        """
        self._memory_context.update(new_context)
        self._logger.debug(f"Updated memory context: {list(new_context.keys())}")

    def serialize(self) -> str:
        """
        Serialize character information to a JSON string

        Returns:
            str: JSON representation of the character
        """
        return json.dumps(
            {
                "id": self._id,
                "name": self._name,
                "personality": self._personality,
                "background": self._background,
            }
        )

    @classmethod
    def deserialize(cls, serialized_data: str) -> "BaseCharacterModel":
        """
        Deserialize a character from a JSON string

        Args:
            serialized_data (str): JSON string representing a character

        Returns:
            BaseCharacterModel: Reconstructed character instance
        """
        data = json.loads(serialized_data)
        character = cls(
            name=data["name"],
            personality=data["personality"],
            background=data.get("background"),
        )
        # Restore the original ID if present
        character._id = data.get("id", character._id)
        return character

    def __repr__(self) -> str:
        """
        String representation of the character

        Returns:
            str: Descriptive string of the character
        """
        return f"Character(id={self._id}, name={self._name})"
