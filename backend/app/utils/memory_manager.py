import json
from typing import Dict, List

from sqlalchemy import desc, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import database as db_models


class MemoryManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def retrieve_relevant_memories(
        self, character_id: str, context: Dict, top_k: int = 5
    ) -> List[Dict]:
        """
        Retrieve the most relevant memories for a character based on context

        Args:
            character_id (str): ID of the character
            context (Dict): Current context to match memories against
            top_k (int): Number of top memories to retrieve

        Returns:
            List[Dict]: Most relevant memories
        """
        # Base query for character's memories
        query = select(db_models.Memory).where(
            db_models.Memory.character_id == character_id
        )

        # Calculate relevance score based on context similarity
        # This is a simplified relevance calculation and can be enhanced
        def calculate_relevance(memory):
            # Compare memory context with current context
            memory_context = memory.context or {}

            relevance_score = 0
            for key, value in context.items():
                if key in memory_context and memory_context[key] == value:
                    relevance_score += 0.5

                # Additional text-based similarity could be added here

            # Incorporate memory importance
            relevance_score += memory.importance

            return relevance_score

        # Execute query and calculate relevance
        result = await self.session.execute(query)
        memories = result.scalars().all()

        # Sort memories by relevance
        relevant_memories = sorted(memories, key=calculate_relevance, reverse=True)[
            :top_k
        ]

        # Convert to dictionary for easier serialization
        return [
            {
                "id": memory.id,
                "content": memory.content,
                "importance": memory.importance,
                "context": memory.context,
                "created_at": memory.created_at.isoformat(),
            }
            for memory in relevant_memories
        ]

    async def create_memory(
        self,
        character_id: str,
        content: str,
        importance: float = 0.5,
        context: Dict = None,
    ) -> db_models.Memory:
        """
        Create a new memory for a character

        Args:
            character_id (str): ID of the character
            content (str): Memory content
            importance (float): Memory importance (0-1)
            context (Dict): Additional context for the memory

        Returns:
            db_models.Memory: Created memory
        """
        memory = db_models.Memory(
            character_id=character_id,
            content=content,
            importance=max(0, min(1, importance)),  # Clamp between 0 and 1
            context=context or {},
        )

        self.session.add(memory)
        await self.session.commit()
        await self.session.refresh(memory)

        return memory

    async def update_memory_importance(self, memory_id: str, new_importance: float):
        """
        Update the importance of a specific memory

        Args:
            memory_id (str): ID of the memory
            new_importance (float): New importance value (0-1)
        """
        memory = await self.session.get(db_models.Memory, memory_id)

        if not memory:
            raise ValueError(f"Memory with ID {memory_id} not found")

        memory.importance = max(0, min(1, new_importance))
        await self.session.commit()

    async def forget_old_memories(
        self, character_id: str, max_memories: int = 100, forget_threshold: float = 0.2
    ):
        """
        Manage memory capacity by forgetting less important memories

        Args:
            character_id (str): ID of the character
            max_memories (int): Maximum number of memories to keep
            forget_threshold (float): Importance threshold for forgetting
        """
        # Query memories sorted by importance
        query = (
            select(db_models.Memory)
            .where(db_models.Memory.character_id == character_id)
            .order_by(
                db_models.Memory.importance.asc(), db_models.Memory.created_at.asc()
            )
        )

        result = await self.session.execute(query)
        memories = result.scalars().all()

        # Identify memories to forget
        memories_to_forget = [
            memory
            for memory in memories
            if (memory.importance < forget_threshold or len(memories) > max_memories)
        ]

        # Remove identified memories
        for memory in memories_to_forget:
            await self.session.delete(memory)

        await self.session.commit()
