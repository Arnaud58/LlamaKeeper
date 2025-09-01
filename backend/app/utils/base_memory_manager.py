import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from uuid import UUID


class BaseMemoryManager(ABC):
    """
    Base implementation of AbstractMemoryManager
    Provides a flexible framework for memory storage and retrieval
    """

    def __init__(self, logger_name: str = "MemoryManager"):
        """
        Initialize the memory manager

        Args:
            logger_name (str, optional): Name for the logger
        """
        self._logger = logging.getLogger(logger_name)
        self._memories: Dict[UUID, Dict[str, Any]] = {}

    @abstractmethod
    async def store_memory(
        self,
        character_id: UUID,
        memory_content: str,
        context: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> UUID:
        """
        Store a memory for a character

        Args:
            character_id (UUID): ID of the character
            memory_content (str): Content of the memory
            context (Dict, optional): Contextual metadata
            importance (float, optional): Memory importance score

        Returns:
            UUID: Unique identifier for the stored memory
        """
        pass

    @abstractmethod
    async def retrieve_relevant_memories(
        self, character_id: UUID, context: Dict[str, Any], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant memories for a character

        Args:
            character_id (UUID): ID of the character
            context (Dict): Context for relevance matching
            top_k (int, optional): Number of top memories to retrieve

        Returns:
            List[Dict]: Most relevant memories
        """
        pass

    @abstractmethod
    async def forget_memories(
        self, character_id: UUID, forget_threshold: float = 0.2, max_memories: int = 100
    ) -> None:
        """
        Manage memory capacity by forgetting less important memories

        Args:
            character_id (UUID): ID of the character
            forget_threshold (float, optional): Importance threshold for forgetting
            max_memories (int, optional): Maximum number of memories to keep
        """
        pass

    def _calculate_memory_relevance(
        self, memory: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """
        Calculate the relevance of a memory to a given context

        Args:
            memory (Dict): Memory to evaluate
            context (Dict): Context to match against

        Returns:
            float: Relevance score (0-1)
        """
        relevance_score = 0.0
        memory_context = memory.get("context", {})

        # Contextual similarity
        for key, value in context.items():
            if key in memory_context:
                # Simple exact match scoring
                if memory_context[key] == value:
                    relevance_score += 0.5

        # Importance weighting
        importance = memory.get("importance", 0.5)
        relevance_score += importance

        # Time decay factor
        created_at = memory.get("created_at")
        if created_at:
            memory_age = datetime.now() - datetime.fromisoformat(created_at)
            # Exponential decay of relevance over time
            time_decay = max(
                0, 1 - (memory_age.total_seconds() / (30 * 24 * 3600))
            )  # 30 days half-life
            relevance_score *= time_decay

        return min(max(relevance_score, 0), 1)

    def _validate_memory_content(self, memory_content: str) -> bool:
        """
        Validate the content of a memory

        Args:
            memory_content (str): Memory content to validate

        Returns:
            bool: Whether the memory content is valid
        """
        if not isinstance(memory_content, str):
            self._logger.warning("Memory content must be a string")
            return False

        if len(memory_content.strip()) == 0:
            self._logger.warning("Memory content cannot be empty")
            return False

        return True

    def serialize_memory(self, memory: Dict[str, Any]) -> str:
        """
        Serialize a memory to a JSON string

        Args:
            memory (Dict): Memory to serialize

        Returns:
            str: JSON representation of the memory
        """
        try:
            return json.dumps(memory, default=str)
        except TypeError as e:
            self._logger.error(f"Failed to serialize memory: {e}")
            raise

    def deserialize_memory(self, serialized_memory: str) -> Dict[str, Any]:
        """
        Deserialize a memory from a JSON string

        Args:
            serialized_memory (str): JSON string representing a memory

        Returns:
            Dict: Deserialized memory
        """
        try:
            return json.loads(serialized_memory)
        except json.JSONDecodeError as e:
            self._logger.error(f"Failed to deserialize memory: {e}")
            raise
