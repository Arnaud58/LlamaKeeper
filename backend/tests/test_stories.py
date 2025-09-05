import pytest
import logging
import traceback
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import database as db_models
from app.api.schemas import StoryCreate, StoryResponse
from app.models.database import AsyncSessionLocal

# Configuration du logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_exception(e):
    """Utilitaire pour logger les exceptions avec la trace complète"""
    logger.error(f"Exception: {e}")
    logger.error(traceback.format_exc())

@pytest.mark.asyncio
async def test_create_story(async_test_client):
    """Test creating a new story"""
    async with async_test_client as client:
        try:
            # Nettoyer les données existantes
            async with AsyncSessionLocal() as session:
                await session.execute(db_models.Story.__table__.delete())
                await session.execute(db_models.Character.__table__.delete())
                await session.commit()
                logger.debug("Tables Story et Character nettoyées")

            # First, create a character to associate with the story
            character_response = await client.post("/api/v1/characters/", json={
                "name": "Story Character",
                "description": "Character for story testing"
            })
            assert character_response.status_code == 200, f"Échec de création du personnage. Réponse : {character_response.text}"
            character = character_response.json()
            logger.debug(f"Personnage créé : {character}")
        
            # Vérifier que le personnage a bien été créé
            async with AsyncSessionLocal() as session:
                character_check = await session.get(db_models.Character, character['id'])
                assert character_check is not None, "Le personnage n'a pas été persisté correctement"
                logger.debug(f"Vérification du personnage : {character_check}")
        
            story_data = {
                "title": "Test Story",
                "description": "A story for unit testing",
                "current_state": {"scene": "introduction"},
                "character_ids": [character['id']]
            }
        
            # Logs détaillés avant la création de l'histoire
            logger.debug(f"Données de l'histoire à créer : {story_data}")
        
            response = await client.post("/api/v1/stories/", json=story_data)
        
            # Log de la réponse complète en cas d'erreur
            if response.status_code != 200:
                logger.error(f"Détails de la réponse : {response.text}")
                logger.error(f"En-têtes de la réponse : {response.headers}")
        
            assert response.status_code == 200, f"Échec de création de l'histoire. Réponse : {response.text}"
        
            story_json = response.json()
            logger.debug(f"Story JSON: {story_json}")
        
            # Validation plus robuste du modèle
            try:
                story = StoryResponse(**story_json)
            except Exception as validation_error:
                logger.error(f"Erreur de validation du modèle : {validation_error}")
                logger.error(f"Données JSON reçues : {story_json}")
                raise
        
            assert story.title == "Test Story"
            assert story.description == "A story for unit testing"
            assert story.current_state == {"scene": "introduction"}
            assert story.id is not None
        
            # Vérifier que l'histoire est bien associée au personnage
            logger.debug(f"Recherche de l'histoire avec l'ID : {story.id}")
        
            # Utiliser la même session pour vérifier la persistance
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(db_models.Story)
                    .options(selectinload(db_models.Story.characters))
                    .filter(db_models.Story.id == story.id)
                )
                db_story = result.unique().scalar_one_or_none()
        
                # Log supplémentaires pour le débogage
                if db_story is None:
                    logger.error("L'histoire n'a pas été trouvée dans la base de données")
                    # Récupérer toutes les histoires pour vérification
                    all_stories_result = await session.execute(
                        select(db_models.Story).options(selectinload(db_models.Story.characters))
                    )
                    all_stories = all_stories_result.unique().scalars().all()
                    logger.error(f"Histoires existantes : {[s.id for s in all_stories]}")
                    
                    # Vérifier l'état de la session
                    logger.debug(f"Session active : {session.is_active}")
                
                assert db_story is not None, "L'histoire n'a pas été persistée correctement"
                assert len(db_story.characters) == 1
                assert db_story.characters[0].id == character['id']

        except Exception as e:
            log_exception(e)
            raise

@pytest.mark.asyncio
async def test_list_stories(async_test_client):
    """Test listing stories with pagination"""
    async with async_test_client as client:
        # Nettoyer les histoires existantes
        async with AsyncSessionLocal() as session:
            await session.execute(db_models.Story.__table__.delete())
            await session.commit()

        # Create a character first
        character_response = await client.post("/api/v1/characters/", json={
            "name": "Story List Character",
            "description": "Character for story list testing"
        })
        assert character_response.status_code == 200
        character = character_response.json()
        
        # Create a few test stories
        test_stories = [
            {
                "title": f"Test Story {i}",
                "description": f"Test description {i}",
                "character_ids": [character['id']]
            } for i in range(3)
        ]

        # Créer et committer chaque histoire
        created_stories = []
        for story_data in test_stories:
            story_response = await client.post("/api/v1/stories/", json=story_data)
            assert story_response.status_code == 200
            created_stories.append(story_response.json())
        
        # Récupérer la liste des histoires
        response = await client.get("/api/v1/stories/")
        
        assert response.status_code == 200
        
        stories = response.json()
        
        # Log supplémentaires pour le débogage
        logger.debug(f"Nombre total d'histoires : {len(stories)}")
        for story in stories:
            logger.debug(f"Histoire : {story['id']} - {story['title']} - Créée le : {story['created_at']}")
        
        # Vérifier la persistance des histoires
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(db_models.Story)
                .options(selectinload(db_models.Story.characters))
            )
            db_stories = result.unique().scalars().all()
            
            logger.debug(f"Nombre d'histoires en base de données : {len(db_stories)}")
            for db_story in db_stories:
                logger.debug(f"Histoire en base : {db_story.id} - {db_story.title}")
            
            # Vérifier l'état de la session
            logger.debug(f"Session état : {session.is_active}")
            
            # Vérifier l'état de la session de manière plus robuste
            try:
                # Vérifier si la session est toujours ouverte
                if not session.is_active:
                    logger.warning("La session n'est plus active, tentative de réouverture")
                    await session.begin()
                
                # Vérifier le nombre d'histoires
                logger.debug(f"Nombre d'histoires avant vérification : {len(db_stories)}")
            except Exception as e:
                logger.error(f"Erreur lors de la vérification de la session : {e}")
                log_exception(e)
            
            assert len(db_stories) == 3, f"Nombre d'histoires incorrect en base de données. Reçu : {len(db_stories)}"
            
            # Vérifier les titres des histoires
            story_titles = {story.title for story in db_stories}
            expected_titles = {f"Test Story {i}" for i in range(3)}
            assert story_titles == expected_titles, f"Titres des histoires incorrects. Reçu : {story_titles}"

@pytest.mark.asyncio
async def test_get_story(async_test_client):
    """Test retrieving a specific story"""
    async with async_test_client as client:
        # First, create a character
        character_response = await client.post("/api/v1/characters/", json={
            "name": "Story Retrieval Character",
            "description": "Character for story retrieval testing"
        })
        character = character_response.json()
        
        # Create a story
        story_data = {
            "title": "Test Story for Retrieval",
            "description": "A story to be retrieved",
            "character_ids": [character['id']]
        }
        create_response = await client.post("/api/v1/stories/", json=story_data)
        created_story = create_response.json()
        
        # Then, get the story
        response = await client.get(f"/api/v1/stories/{created_story['id']}")
        
        assert response.status_code == 200
        
        story = StoryResponse(**response.json())
        assert story.title == "Test Story for Retrieval"
        assert story.description == "A story to be retrieved"

@pytest.mark.asyncio
async def test_update_story(async_test_client):
    """Test updating an existing story"""
    async with async_test_client as client:
        # First, create a character
        character_response = await client.post("/api/v1/characters/", json={
            "name": "Story Modification Character",
            "description": "Character for story modification testing"
        })
        character = character_response.json()
        
        # Create a story
        story_data = {
            "title": "Original Story",
            "description": "To be updated",
            "character_ids": [character['id']]
        }
        create_response = await client.post("/api/v1/stories/", json=story_data)
        created_story = create_response.json()
        
        # Mettre à jour l'histoire
        update_data = {
            "title": "Updated Story",
            "description": "Updated description",
            "current_state": {"scene": "climax"}
        }
        response = await client.put(f"/api/v1/stories/{created_story['id']}", json=update_data)
        
        assert response.status_code == 200
        
        updated_story = StoryResponse(**response.json())
        assert updated_story.title == "Updated Story"
        assert updated_story.description == "Updated description"
        assert updated_story.current_state == {"scene": "climax"}

@pytest.mark.asyncio
async def test_delete_story(async_test_client):
    """Test deleting a story"""
    async with async_test_client as client:
        # First, create a character
        character_response = await client.post("/api/v1/characters/", json={
            "name": "Story Deletion Character",
            "description": "Character for story deletion testing"
        })
        character = character_response.json()
        
        # Create a story
        story_data = {
            "title": "Story to Delete",
            "description": "Will be deleted soon",
            "character_ids": [character['id']]
        }
        create_response = await client.post("/api/v1/stories/", json=story_data)
        created_story = create_response.json()
        
        # Delete the story
        response = await client.delete(f"/api/v1/stories/{created_story['id']}")
        
        assert response.status_code == 204
        
        # Verify the story is no longer retrievable
        get_response = await client.get(f"/api/v1/stories/{created_story['id']}")
        assert get_response.status_code == 404