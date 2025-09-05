import pytest
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_character_validation_errors(async_session: AsyncSession, async_test_client):
    """Test validation errors when creating a character"""
    # Test empty name
    invalid_character_data = {
        "name": "",
        "description": "Invalid character"
    }
    response = await async_test_client.post("/api/v1/characters/", json=invalid_character_data)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test name too long
    long_name_data = {
        "name": "A" * 200,  # Exceeding max length
        "description": "Invalid character"
    }
    response = await async_test_client.post("/api/v1/characters/", json=long_name_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_create_story_validation_errors(async_session: AsyncSession, async_test_client):
    """Test validation errors when creating a story"""
    # Test empty title
    invalid_story_data = {
        "title": "",
        "description": "Invalid story"
    }
    response = await async_test_client.post("/api/v1/stories/", json=invalid_story_data)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Test title too long
    long_title_data = {
        "title": "A" * 300,  # Exceeding max length
        "description": "Invalid story"
    }
    response = await async_test_client.post("/api/v1/stories/", json=long_title_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_nonexistent_character(async_session: AsyncSession, async_test_client):
    """Test retrieving a non-existent character"""
    # Use a very large ID that is unlikely to exist
    response = await async_test_client.get("/api/v1/characters/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_get_nonexistent_story(async_session: AsyncSession, async_test_client):
    """Test retrieving a non-existent story"""
    # Use a very large ID that is unlikely to exist
    response = await async_test_client.get("/api/v1/stories/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_character(async_session: AsyncSession, async_test_client):
    """Test updating a non-existent character"""
    update_data = {
        "name": "Updated Character",
        "description": "Trying to update non-existent character"
    }
    response = await async_test_client.put("/api/v1/characters/99999", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_update_nonexistent_story(async_session: AsyncSession, async_test_client):
    """Test updating a non-existent story"""
    update_data = {
        "title": "Updated Story",
        "description": "Trying to update non-existent story"
    }
    response = await async_test_client.put("/api/v1/stories/99999", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_character(async_session: AsyncSession, async_test_client):
    """Test deleting a non-existent character"""
    response = await async_test_client.delete("/api/v1/characters/99999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_story(async_session: AsyncSession, async_test_client):
    """Test deleting a non-existent story"""
    response = await async_test_client.delete("/api/v1/stories/99999")
    assert response.status_code == 404