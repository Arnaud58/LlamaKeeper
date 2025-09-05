import pytest
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import ValidationError

from app.models import database as db_models
from app.models import schemas

# Configuration du logging pour les tests
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@pytest.mark.asyncio
async def test_create_character(async_session: AsyncSession):
    """Test creating a character"""
    logger.debug("Début du test de création de personnage")
    
    character_data = schemas.CharacterCreate(
        name="Test Character",
        description="A character for testing"
    )
    logger.debug(f"Données du personnage : {character_data}")
    
    character = character_data.to_sqlalchemy()
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    # Vérifier les contraintes de base de données
    assert character.id is not None
    assert character.name is not None
    assert len(character.name) >= 2

    logger.debug(f"Personnage créé avec ID : {character.id}")

    assert character.id is not None
    assert character.name == "Test Character"
    assert character.description == "A character for testing"
    
    logger.debug("Test de création de personnage terminé avec succès")


@pytest.mark.asyncio
async def test_create_story(async_session: AsyncSession):
    """Test creating a story"""
    logger.debug("Début du test de création d'histoire")
    
    # Create a character first
    character_data = schemas.CharacterCreate(
        name="Story Character",
        description="Character for story testing"
    )
    logger.debug(f"Données du personnage : {character_data}")
    
    character = character_data.to_sqlalchemy()
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)
    
    logger.debug(f"Personnage créé avec ID : {character.id}")

    story_data = schemas.StoryCreate(
        title="Test Story",
        description="A test story for unit testing",
        current_state={"stage": "beginning", "mood": "mysterious"},
        character_ids=[character.id]
    )
    logger.debug(f"Données de l'histoire : {story_data}")
    
    story = await story_data.to_sqlalchemy(async_session)
    async_session.add(story)
    await async_session.commit()
    await async_session.refresh(story)

    logger.debug(f"Histoire créée avec ID : {story.id}")

    # Vérifications étendues
    assert story.id is not None
    assert story.title == "Test Story"
    assert story.title is not None
    assert len(story.title) >= 2
    assert story.current_state == {"stage": "beginning", "mood": "mysterious"}
    assert len(story.characters) == 1
    assert story.characters[0].id == character.id
    
    logger.debug("Test de création d'histoire terminé avec succès")


@pytest.mark.asyncio
async def test_create_action(async_session: AsyncSession):
    """Test creating an action for a story and character"""
    # Créer un personnage
    character_data = schemas.CharacterCreate(
        name="Action Character",
        description="Character for action testing"
    )
    character = character_data.to_sqlalchemy()
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    # Créer une histoire avec le personnage
    story_data = schemas.StoryCreate(
        title="Action Story",
        description="A story for testing actions",
        character_ids=[character.id]
    )
    story = await story_data.to_sqlalchemy(async_session)
    async_session.add(story)
    await async_session.commit()
    await async_session.refresh(story)

    # Créer une action
    action_data = schemas.ActionCreate(
        story_id=story.id,
        character_id=character.id,
        content="Performed a heroic deed",
        action_type="physical"
    )

    action = await action_data.to_sqlalchemy(async_session, story=story, character=character)
    async_session.add(action)
    await async_session.commit()
    await async_session.refresh(action)

    # Vérifications étendues
    assert action.id is not None
    assert action.content == "Performed a heroic deed"
    assert action.content is not None
    assert len(action.content) >= 2
    assert action.action_type == "physical"
    assert action.action_type is not None
    assert action.story_id == story.id
    assert action.character_id == character.id
    assert action.story is not None
    assert action.character is not None


@pytest.mark.asyncio
async def test_character_relationships(async_session: AsyncSession):
    """Test relationships between characters and stories"""
    character1_data = schemas.CharacterCreate(name="Character 1")
    character2_data = schemas.CharacterCreate(name="Character 2")

    character1 = character1_data.to_sqlalchemy()
    character2 = character2_data.to_sqlalchemy()
    async_session.add(character1)
    async_session.add(character2)
    await async_session.commit()
    await async_session.refresh(character1)
    await async_session.refresh(character2)
    async_session.add(character1)
    async_session.add(character2)
    await async_session.commit()
    await async_session.refresh(character1)
    await async_session.refresh(character2)
    async_session.add(character1)
    async_session.add(character2)
    await async_session.commit()
    await async_session.refresh(character1)
    await async_session.refresh(character2)

    story_data = schemas.StoryCreate(
        title="Relationship Test Story",
        description="A story to test character relationships",
        character_ids=[character1.id, character2.id]
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
    # Créer un personnage
    character_data = schemas.CharacterCreate(
        name="Memory Character",
        description="Character for memory testing"
    )
    character = character_data.to_sqlalchemy()
    async_session.add(character)
    await async_session.commit()
    await async_session.refresh(character)

    # Créer une mémoire pour le personnage
    memory_data = schemas.MemoryCreate(
        character_id=character.id,
        content="A significant memory",
        importance=0.8,
        context={"emotion": "joy", "trigger": "success"}
    )

    memory = await memory_data.to_sqlalchemy(async_session, character=character)
    async_session.add(memory)
    await async_session.commit()
    await async_session.refresh(memory)

    # Vérifications étendues
    assert memory.id is not None
    assert memory.content == "A significant memory"
    assert memory.content is not None
    assert len(memory.content) >= 2
    assert memory.importance == 0.8
    assert 0 <= memory.importance <= 1
    assert memory.character_id == character.id
    assert memory.character is not None


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
        schemas.MemoryCreate(
            character_id=1,
            content="",
            importance=0.5
        )