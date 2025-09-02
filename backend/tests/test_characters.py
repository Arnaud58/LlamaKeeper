import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.api.schemas import CharacterCreate, CharacterResponse

@pytest.fixture(scope="module")
def test_client_app():
    return app

@pytest.mark.asyncio
async def test_create_character(async_session: AsyncSession, test_client_app):
    """Test creating a new character"""
    async with AsyncClient(base_url="http://test", app=test_client_app) as client:
        character_data = {
            "name": "Test Character",
            "description": "A test character for unit testing",
            "personality": {"trait1": "brave", "trait2": "curious"}
        }
        
        response = await client.post("/api/v1/characters/", json=character_data)
        
        assert response.status_code == 200
        
        character = CharacterResponse(**response.json())
        assert character.name == "Test Character"
        assert character.description == "A test character for unit testing"
        assert character.personality == {"trait1": "brave", "trait2": "curious"}
        assert character.id is not None

@pytest.mark.asyncio
async def test_list_characters(async_session: AsyncSession, test_client_app):
    """Test listing characters with pagination"""
    async with AsyncClient(base_url="http://test", app=test_client_app) as client:
        # Create a few test characters first
        for i in range(3):
            character_data = {
                "name": f"Test Character {i}",
                "description": f"Test description {i}"
            }
            await client.post("/api/v1/characters/", json=character_data)
        
        response = await client.get("/api/v1/characters/")
        
        print(f"DEBUG: Response status code: {response.status_code}")
        print(f"DEBUG: Response content: {response.text}")
        
        assert response.status_code == 200
        
        characters = response.json()
        assert len(characters) >= 3
        
        # Verify response schema
        for character in characters:
            character_model = CharacterResponse(**character)
            assert character_model.name.startswith("Test Character")

@pytest.mark.asyncio
async def test_get_character(async_session: AsyncSession, test_client_app):
    """Test retrieving a specific character"""
    async with AsyncClient(base_url="http://test", app=test_client_app) as client:
        # First, create a character
        character_data = {
            "name": "Unique Character",
            "description": "A character to be retrieved"
        }
        create_response = await client.post("/api/v1/characters/", json=character_data)
        created_character = create_response.json()
        
        # Then, retrieve the character
        response = await client.get(f"/api/v1/characters/{created_character['id']}")
        
        assert response.status_code == 200
        
        character = CharacterResponse(**response.json())
        assert character.name == "Unique Character"
        assert character.description == "A character to be retrieved"

@pytest.mark.asyncio
async def test_update_character(async_session: AsyncSession, test_client_app):
    """Test updating an existing character"""
    async with AsyncClient(base_url="http://test", app=test_client_app) as client:
        # First, create a character
        character_data = {
            "name": "Original Character",
            "description": "To be updated"
        }
        create_response = await client.post("/api/v1/characters/", json=character_data)
        created_character = create_response.json()
        
        # Update the character
        update_data = {
            "name": "Updated Character",
            "description": "Updated description"
        }
        response = await client.put(f"/api/v1/characters/{created_character['id']}", json=update_data)
        
        assert response.status_code == 200
        
        updated_character = CharacterResponse(**response.json())
        assert updated_character.name == "Updated Character"
        assert updated_character.description == "Updated description"

@pytest.mark.asyncio
async def test_delete_character(async_session: AsyncSession, test_client_app):
    """Test deleting a character"""
    async with AsyncClient(base_url="http://test", app=test_client_app) as client:
        # First, create a character
        character_data = {
            "name": "Character to Delete",
            "description": "Will be deleted soon"
        }
        create_response = await client.post("/api/v1/characters/", json=character_data)
        created_character = create_response.json()
        
        # Delete the character
        response = await client.delete(f"/api/v1/characters/{created_character['id']}")
        
        assert response.status_code == 204
        
        # Verify the character is no longer retrievable
        get_response = await client.get(f"/api/v1/characters/{created_character['id']}")
        assert get_response.status_code == 404