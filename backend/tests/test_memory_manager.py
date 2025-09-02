import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import select

from app.utils.memory_manager import MemoryManager
from app.models import database as db_models

@pytest.mark.asyncio
async def test_create_memory(async_session):
    """Test creating a memory"""
    character = db_models.Character(
        name="Memory Test Character",
        description="Character for memory management testing"
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    memory_manager = MemoryManager(async_session)
    
    memory = await memory_manager.create_memory(
        character_id=character.id,
        content="A significant test memory",
        importance=0.7,
        context={"type": "test", "source": "unit_test"}
    )
    
    assert memory.id is not None
    assert memory.character_id == character.id
    assert memory.content == "A significant test memory"
    assert memory.importance == 0.7
    assert memory.context == {"type": "test", "source": "unit_test"}

@pytest.mark.asyncio
async def test_retrieve_relevant_memories(async_session):
    """Test retrieving relevant memories"""
    character = db_models.Character(
        name="Relevance Test Character",
        description="Character for memory relevance testing"
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    memory_manager = MemoryManager(async_session)
    
    # Create multiple memories with different contexts and importances
    memories = [
        await memory_manager.create_memory(
            character_id=character.id,
            content=f"Memory {i}",
            importance=0.1 * (i + 1),
            context={"type": "test", "index": i}
        ) for i in range(5)
    ]
    
    # Retrieve relevant memories
    context = {"type": "test", "index": 2}
    print(f"DEBUG: Context for memory retrieval: {context}")
    print(f"DEBUG: Created memories: {[{'id': m.id, 'importance': m.importance, 'context': m.context} for m in memories]}")
    
    relevant_memories = await memory_manager.retrieve_relevant_memories(
        character_id=character.id,
        context=context,
        top_k=3
    )
    
    print(f"DEBUG: Retrieved relevant memories: {relevant_memories}")
    
    assert len(relevant_memories) > 0, "No relevant memories retrieved"
    assert len(relevant_memories) <= 3, f"Retrieved more than 3 memories: {len(relevant_memories)}"
    
    # Check that memories are sorted by relevance
    importances = [memory['importance'] for memory in relevant_memories]
    print(f"DEBUG: Importances of retrieved memories: {importances}")
    
    sorted_importances = sorted(importances, reverse=True)
    print(f"DEBUG: Sorted importances: {sorted_importances}")
    
    assert importances == sorted_importances, f"Memories not sorted by importance. Got {importances}, expected {sorted_importances}"

@pytest.mark.asyncio
async def test_update_memory_importance(async_session):
    """Test updating memory importance"""
    character = db_models.Character(
        name="Importance Test Character",
        description="Character for memory importance testing"
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    memory_manager = MemoryManager(async_session)
    
    memory = await memory_manager.create_memory(
        character_id=character.id,
        content="Original memory",
        importance=0.5
    )
    
    # Update memory importance
    await memory_manager.update_memory_importance(memory.id, 0.9)
    
    # Retrieve the updated memory
    result = await async_session.execute(
        select(db_models.Memory).where(db_models.Memory.id == memory.id)
    )
    updated_memory = result.scalar_one()
    
    assert updated_memory.importance == 0.9

@pytest.mark.asyncio
async def test_forget_old_memories(async_session):
    """Test forgetting less important memories"""
    character = db_models.Character(
        name="Forget Test Character",
        description="Character for memory forgetting testing"
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    memory_manager = MemoryManager(async_session)
    
    # Create multiple memories with varying importances
    memories = [
        await memory_manager.create_memory(
            character_id=character.id,
            content=f"Memory {i}",
            importance=0.1 * i,
            context={"batch": "forget_test"}
        ) for i in range(10)
    ]
    
    # Forget memories
    await memory_manager.forget_old_memories(
        character_id=character.id, 
        max_memories=5, 
        forget_threshold=0.3
    )
    
    # Count remaining memories
    result = await async_session.execute(
        select(db_models.Memory).where(
            db_models.Memory.character_id == character.id
        )
    )
    remaining_memories = result.scalars().all()
    
    assert len(remaining_memories) <= 5
    
    # Check that only high-importance memories remain
    importances = [memory.importance for memory in remaining_memories]
    assert all(importance >= 0.3 for importance in importances)