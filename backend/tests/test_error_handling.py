import pytest
from httpx import AsyncClient, HTTPStatusError
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.api.schemas import CharacterCreate, StoryCreate

@pytest.mark.asyncio
async def test_create_character_validation_errors(async_session: AsyncSession):
    """Test validation errors when creating a character"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test empty name
        invalid_character_data = {
            "name": "",
            "description": "Invalid character"
        }
        response = await client.post("/api/v1/characters/", json=invalid_character_data)
        assert response.status_code == 422  # Unprocessable Entity
        
        # Test name too long
        long_name_data = {
            "name": "A" * 200,  # Exceeding max length
            "description": "Invalid character"
        }
        response = await client.post("/api/v1/characters/", json=long_name_data)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_story_validation_errors(async_session: AsyncSession):
    """Test validation errors when creating a story"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test empty title
        invalid_story_data = {
            "title": "",
            "description": "Invalid story"
        }
        response = await client.post("/api/v1/stories/", json=invalid_story_data)
        assert response.status_code == 422  # Unprocessable Entity
        
        # Test title too long
        long_title_data = {
            "title": "A" * 300,  # Exceeding max length
            "description": "Invalid story"
        }
        response = await client.post("/api/v1/stories/", json=long_title_data)
        assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_nonexistent_character(async_session: AsyncSession):
    """Test retrieving a non-existent character"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Use a very large ID that is unlikely to exist
        response = await client.get("/api/v1/characters/99999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_nonexistent_story(async_session: AsyncSession):
    """Test retrieving a non-existent story"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Use a very large ID that is unlikely to exist
        response = await client.get("/api/v1/stories/99999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_character(async_session: AsyncSession):
    """Test updating a non-existent character"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        update_data = {
            "name": "Updated Character",
            "description": "Trying to update non-existent character"
        }
        response = await client.put("/api/v1/characters/99999", json=update_data)
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_story(async_session: AsyncSession):
    """Test updating a non-existent story"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        update_data = {
            "title": "Updated Story",
            "description": "Trying to update non-existent story"
        }
        response = await client.put("/api/v1/stories/99999", json=update_data)
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_character(async_session: AsyncSession):
    """Test deleting a non-existent character"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/characters/99999")
        assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_story(async_session: AsyncSession):
    """Test deleting a non-existent story"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.delete("/api/v1/stories/99999")
        assert response.status_code == 404