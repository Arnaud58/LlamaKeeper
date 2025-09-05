import pytest
import logging
from httpx import AsyncClient, ASGITransport
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.models import database as db_models
from app.api.schemas import CharacterCreate, CharacterResponse
from app.models.database import AsyncSessionLocal

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(scope="module")
def test_client_app():
    return app

@pytest.mark.asyncio
async def test_create_character(async_test_client):
    """Test creating a new character"""
    async with AsyncSessionLocal() as async_session:
        # Nettoyer les personnages existants
        await async_session.execute(db_models.Character.__table__.delete())
        await async_session.commit()

        character_data = {
            "name": "Test Character",
            "description": "A test character for unit testing",
            "personality": {"trait1": "brave", "trait2": "curious"}
        }
        
        response = await async_test_client.post("/api/v1/characters/", json=character_data)
        
        assert response.status_code == 200, f"Échec de création du personnage. Réponse : {response.text}"
        
        character = CharacterResponse(**response.json())
        assert character.name == "Test Character"
        assert character.description == "A test character for unit testing"
        assert character.personality == {"trait1": "brave", "trait2": "curious"}
        assert character.id is not None

        # Vérifier la persistance en base de données
        result = await async_session.execute(
            select(db_models.Character).filter(db_models.Character.id == character.id)
        )
        db_character = result.scalar_one_or_none()
        
        assert db_character is not None, "Le personnage n'a pas été persisté correctement"
        
        # Comparaison explicite des valeurs
        logger.debug(f"Comparaison du personnage - Base de données vs Réponse")
        
        # Extraction manuelle des valeurs
        def safe_extract(obj, attr, default=''):
            try:
                # Utiliser une méthode de récupération qui contourne les problèmes SQLAlchemy
                if hasattr(obj, attr):
                    value = getattr(obj, attr)
                    # Si c'est un objet SQLAlchemy, essayer de récupérer sa valeur
                    if hasattr(value, '_sa_instance_state'):
                        return str(value)
                    return str(value) if value is not None else default
                return default
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction de {attr}: {e}")
                return default
        
        # Comparaison des attributs de base
        db_name = safe_extract(db_character, 'name')
        db_description = safe_extract(db_character, 'description')
        
        logger.debug(f"Nom (DB): {db_name}, Nom (Réponse): {character.name}")
        logger.debug(f"Description (DB): {db_description}, Description (Réponse): {character.description}")
        
        # Vérification des attributs de base
        assert db_name == str(character.name), f"Nom du personnage incorrect. Attendu : {character.name}, Reçu : {db_name}"
        assert db_description == str(character.description), f"Description du personnage incorrecte. Attendu : {character.description}, Reçu : {db_description}"
        
        # Gestion de la personnalité
        def extract_personality(personality):
            if personality is None:
                return {}
            
            # Méthode de conversion qui gère différents types
            def convert_value(value):
                if isinstance(value, (int, str, bool, float)):
                    return value
                return str(value)
            
            try:
                # Gérer différents types de personnalité
                if isinstance(personality, dict):
                    return {k: convert_value(v) for k, v in personality.items()}
                
                # Si c'est un objet SQLAlchemy ou autre
                if hasattr(personality, '__dict__'):
                    return {
                        k: convert_value(v)
                        for k, v in personality.__dict__.items()
                        if not k.startswith('_') and not callable(v)
                    }
                
                # Dernière tentative de conversion
                return dict(personality)
            
            except Exception as e:
                logger.error(f"Erreur lors de l'extraction de la personnalité : {e}")
                return {}
        
        # Extraction et comparaison de la personnalité
        try:
            db_personality = extract_personality(db_character.personality)
            character_personality = extract_personality(character.personality)
            
            logger.debug(f"Personnalité extraite (DB): {db_personality}")
            logger.debug(f"Personnalité extraite (Réponse): {character_personality}")
            
            # Comparaison des personnalités
            assert db_personality == character_personality, f"Personnalité du personnage incorrecte. Attendu : {character_personality}, Reçu : {db_personality}"
        
        except Exception as e:
            logger.error(f"Erreur lors de la comparaison de la personnalité : {e}")
            raise

@pytest.mark.asyncio
async def test_list_characters(async_test_client):
    """Test listing characters with pagination"""
    async with AsyncSessionLocal() as async_session:
        # Nettoyer TOUS les caractères existants de manière plus agressive
        await async_session.execute(delete(db_models.Character))
        await async_session.commit()

        # Vérification initiale - base de données doit être vide
        result = await async_session.execute(select(db_models.Character))
        initial_characters = result.scalars().all()
        logger.debug(f"DEBUG: Nombre de personnages AVANT le test : {len(initial_characters)}")
        assert len(initial_characters) == 0, "La base de données n'est pas vide avant le test"

        # Créer des personnages de test
        created_characters = []
        for i in range(3):
            character_data = {
                "name": f"Test Character {i}",
                "description": f"Test description {i}"
            }
            response = await async_test_client.post("/api/v1/characters/", json=character_data)
            assert response.status_code == 200, f"Échec de création du personnage {i}"
            created_characters.append(response.json())
        
        # Vérifier la création des personnages en base de données
        result = await async_session.execute(select(db_models.Character))
        db_characters = result.scalars().all()
        logger.debug(f"DEBUG: Nombre de personnages créés : {len(db_characters)}")
        
        # Récupérer la liste des personnages
        response = await async_test_client.get("/api/v1/characters/")
        
        logger.debug(f"DEBUG: Response status code: {response.status_code}")
        logger.debug(f"DEBUG: Response content: {response.text}")
        
        assert response.status_code == 200, "La requête de liste des personnages a échoué"
        
        characters = response.json()
        logger.debug(f"DEBUG: Nombre de personnages retournés : {len(characters)}")
        
        # Afficher les détails des personnages retournés pour investigation
        for i, character in enumerate(characters):
            logger.debug(f"Personnage {i}: {character}")
        
        assert len(characters) == 3, f"Nombre de personnages incorrect. Attendu : 3, Reçu : {len(characters)}"
        
        # Vérifier le schéma de réponse
        for character in characters:
            character_model = CharacterResponse(**character)
            assert character_model.name.startswith("Test Character"), f"Nom de personnage invalide : {character_model.name}"

@pytest.mark.asyncio
async def test_get_character(async_test_client):
    """Test retrieving a specific character"""
    # First, create a character
    character_data = {
        "name": "Unique Character",
        "description": "A character to be retrieved"
    }
    create_response = await async_test_client.post("/api/v1/characters/", json=character_data)
    created_character = create_response.json()
    
    # Then, retrieve the character
    response = await async_test_client.get(f"/api/v1/characters/{created_character['id']}")
    
    assert response.status_code == 200
    
    character = CharacterResponse(**response.json())
    assert character.name == "Unique Character"
    assert character.description == "A character to be retrieved"

@pytest.mark.asyncio
async def test_update_character(async_test_client):
    """Test updating an existing character"""
    # First, create a character
    character_data = {
        "name": "Original Character",
        "description": "To be updated"
    }
    create_response = await async_test_client.post("/api/v1/characters/", json=character_data)
    created_character = create_response.json()
    
    # Update the character
    update_data = {
        "name": "Updated Character",
        "description": "Updated description"
    }
    response = await async_test_client.put(f"/api/v1/characters/{created_character['id']}", json=update_data)
    
    assert response.status_code == 200
    
    updated_character = CharacterResponse(**response.json())
    assert updated_character.name == "Updated Character"
    assert updated_character.description == "Updated description"

@pytest.mark.asyncio
async def test_delete_character(async_test_client):
    """Test deleting a character"""
    # First, create a character
    character_data = {
        "name": "Character to Delete",
        "description": "Will be deleted soon"
    }
    create_response = await async_test_client.post("/api/v1/characters/", json=character_data)
    created_character = create_response.json()
    
    # Delete the character
    response = await async_test_client.delete(f"/api/v1/characters/{created_character['id']}")
    
    assert response.status_code == 204
    
    # Verify the character is no longer retrievable
    get_response = await async_test_client.get(f"/api/v1/characters/{created_character['id']}")
    assert get_response.status_code == 404