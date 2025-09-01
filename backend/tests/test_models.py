import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

from app.models import database as db_models
from app.models import schemas


@pytest.mark.asyncio
async def test_create_character(async_session: AsyncSession):
    """Test creating a character"""
    character_data = schemas.CharacterCreate(
        name="Test Character",
        description="A character for testing"
    )
    
    character = await character_data.to_sqlalchemy(async_session)
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    assert character.id is not None
    assert character.name == "Test Character"
    assert character.description == "A character for testing"


@pytest.mark.asyncio
async def test_create_story(async_session: AsyncSession):
    """Test creating a story"""
    # Create a character first
    character_data = schemas.CharacterCreate(
        name="Story Character",
        description="Character for story testing"
    )
    character = await character_data.to_sqlalchemy(async_session)
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    story_data = schemas.StoryCreate(
        title="Test Story",
        description="A test story for unit testing",
        current_state={"stage": "beginning", "mood": "mysterious"},
        character_ids=[character.id]
    )
    
    story = await story_data.to_sqlalchemy(async_session)
    async_session.add(story)
    await async_session.commit()
    await async_session.refresh(story)

    assert story.id is not None
    assert story.title == "Test Story"
    assert story.current_state == {"stage": "beginning", "mood": "mysterious"}
    assert len(story.characters) == 1
    assert story.characters[0].id == character.id


@pytest.mark.asyncio
async def test_create_action(async_session: AsyncSession):
    """Test creating an action for a story and character"""
    character_data = schemas.CharacterCreate(
        name="Action Character",
        description="Character for action testing"
    )
    character = await character_data.to_sqlalchemy(async_session)
    async_session.add(character)

    story_data = schemas.StoryCreate(
        title="Action Story",
        description="A story for testing actions"
    )
    story = await story_data.to_sqlalchemy(async_session)
    async_session.add(story)

    await async_session.commit()
    await async_session.refresh(character)
    await async_session.refresh(story)

    action_data = schemas.ActionCreate(
        story_id=story.id,
        character_id=character.id,
        content="Performed a heroic deed",
        action_type="physical",
        reaction="The crowd cheered",
        context={"location": "town square", "time_of_day": "afternoon"}
    )

    action = action_data.to_sqlalchemy()
    async_session.add(action)
    await async_session.commit()
    await async_session.refresh(action)

    assert action.id is not None
    assert action.content == "Performed a heroic deed"
    assert action.action_type == "physical"
    assert action.story_id == story.id
    assert action.character_id == character.id


@pytest.mark.asyncio
async def test_character_relationships(async_session: AsyncSession):
    """Test relationships between characters and stories"""
    character1_data = schemas.CharacterCreate(name="Character 1")
    character2_data = schemas.CharacterCreate(name="Character 2")

    character1 = await character1_data.to_sqlalchemy(async_session)
    character2 = await character2_data.to_sqlalchemy(async_session)

    story_data = schemas.StoryCreate(
        title="Relationship Test Story",
        description="A story to test character relationships"
    )
    story = await story_data.to_sqlalchemy(async_session)

    story.characters.extend([character1, character2])

    async_session.add(story)
    async_session.add(character1)
    async_session.add(character2)

    await async_session.commit()
    await async_session.refresh(story)

    assert len(story.characters) == 2
    assert {char.name for char in story.characters} == {"Character 1", "Character 2"}


@pytest.mark.asyncio
async def test_create_memory(async_session: AsyncSession):
    """Test creating a memory for a character"""
    character_data = schemas.CharacterCreate(
        name="Memory Character",
        description="Character for memory testing"
    )
    character = await character_data.to_sqlalchemy(async_session)
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    memory_data = schemas.Memory(
        character_id=character.id,
        content="A significant memory",
        importance=0.8,
        context={"emotion": "joy", "trigger": "success"}
    )

    memory = memory_data.to_sqlalchemy()
    async_session.add(memory)
    await async_session.commit()
    await async_session.refresh(memory)

    assert memory.id is not None
    assert memory.content == "A significant memory"
    assert memory.importance == 0.8
    assert memory.character_id == character.id


def test_character_validation():
    """Test character model validation"""
    with pytest.raises(ValidationError):
        schemas.CharacterCreate(name="")

    with pytest.raises(ValidationError):
        schemas.CharacterCreate(name="A")


def test_story_validation():
    """Test story model validation"""
    with pytest.raises(ValidationError):
        schemas.StoryCreate(title="")

    with pytest.raises(ValidationError):
        schemas.StoryCreate(title="A")


def test_action_validation():
    """Test action model validation"""
    with pytest.raises(ValidationError):
        schemas.ActionCreate(
            story_id=1,
            character_id=1,
            content="",
            action_type="physical"
        )


def test_memory_validation():
    """Test memory model validation"""
    with pytest.raises(ValidationError):
        schemas.Memory(
            character_id=1,
            content="",
            importance=0.5
        )