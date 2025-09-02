import pytest
import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.utils.character_autonomy import CharacterAutonomySystem
from app.utils.ollama_client import OllamaClient
from app.models import database
from app.models import schemas as db_models

@pytest.mark.asyncio
async def test_generate_action(async_session, mocker):
    """Test generating an autonomous character action"""
    # Mock Ollama client to return a predictable response
    mock_ollama_client = mocker.AsyncMock(spec=OllamaClient)
    mock_ollama_client.generate_text.return_value = asyncio.Future()
    mock_ollama_client.generate_text.return_value.set_result(json.dumps({
        "action_type": "dialogue",
        "content": "I'm feeling brave and ready for adventure!",
        "emotional_state": "excited",
        "motivation": "Desire to explore and prove myself"
    }))

    # Create a test character
    character = database.Character(
        name="Test Autonomous Character",
        description="A brave adventurer",
        personality={
            "trait1": "brave",
            "trait2": "curious",
            "background": "Aspiring hero"
        }
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    # Initialize character autonomy system
    autonomy_system = CharacterAutonomySystem(async_session, mock_ollama_client)

    # Generate action
    story_context = {
        "setting": "medieval fantasy world",
        "current_situation": "preparing for a quest"
    }
    recent_actions = []

    # Utiliser le bon modèle pour les requêtes
    action = await autonomy_system.generate_action(
        character_id=character.id,
        story_context=story_context,
        recent_actions=recent_actions
    )

    # Assertions
    assert action is not None
    assert 'action_type' in action
    assert 'content' in action
    assert 'emotional_state' in action
    assert 'motivation' in action
    assert action['character_id'] == character.id

    # Verify Ollama was called
    mock_ollama_client.generate_text.assert_called_once()

@pytest.mark.asyncio
async def test_generate_action_error_handling(async_session, mocker):
    """Test error handling in action generation"""
    # Mock Ollama client to raise an exception
    mock_ollama_client = mocker.AsyncMock(spec=OllamaClient)
    future = asyncio.Future()
    future.set_exception(Exception("Ollama generation failed"))
    mock_ollama_client.generate_text.return_value = future

    # Create a test character
    character = database.Character(
        name="Error Handling Character",
        description="A character for testing error scenarios"
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    # Initialize character autonomy system
    autonomy_system = CharacterAutonomySystem(async_session, mock_ollama_client)

    # Generate action
    story_context = {"setting": "test environment"}
    recent_actions = []

    action = await autonomy_system.generate_action(
        character_id=character.id,
        story_context=story_context,
        recent_actions=recent_actions
    )

    # Assertions for fallback action
    assert action is not None
    assert action['action_type'] == 'internal_thought'
    assert 'I\'m unsure what to do next' in action['content']
    assert action['character_id'] == character.id

@pytest.mark.asyncio
async def test_action_memory_creation(async_session, mocker):
    """Test that actions are converted to memories"""
    # Mock Ollama client with a predictable response
    mock_ollama_client = mocker.AsyncMock(spec=OllamaClient)
    mock_ollama_client.generate_text.return_value = asyncio.Future()
    mock_ollama_client.generate_text.return_value.set_result(json.dumps({
        "action_type": "dialogue",
        "content": "We must work together to overcome this challenge!",
        "emotional_state": "determined",
        "motivation": "Team spirit and shared goal"
    }))

    # Create a test character
    character = database.Character(
        name="Memory Test Character",
        description="A character for testing memory creation"
    )
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    # Initialize character autonomy system
    autonomy_system = CharacterAutonomySystem(async_session, mock_ollama_client)

    # Generate action
    story_context = {"setting": "critical mission"}
    recent_actions = []

    action = await autonomy_system.generate_action(
        character_id=character.id,
        story_context=story_context,
        recent_actions=recent_actions
    )

    # Verify memory was created
    result = await async_session.execute(
        select(database.Memory).where(
            database.Memory.character_id == character.id
        )
    )
    memories = result.scalars().all()

    assert len(memories) > 0
    memory = memories[-1]  # Get the most recent memory
    
    memory_content = json.loads(memory.content)
    assert memory_content['action_type'] == action['action_type']
    assert memory_content['content'] == action['content']
    assert memory.importance > 0