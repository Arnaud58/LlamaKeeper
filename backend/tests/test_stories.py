import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import database as db_models
from app.api.schemas import StoryCreate, StoryResponse

@pytest.mark.asyncio
async def test_create_story(test_client, async_session: AsyncSession):
    """Test creating a new story"""
    # First, create a character to associate with the story
    character_response = test_client.post("/api/v1/characters/", json={
        "name": "Story Character",
        "description": "Character for story testing"
    })
    assert character_response.status_code == 200
    character = character_response.json()
    
    story_data = {
        "title": "Test Story",
        "description": "A story for unit testing",
        "current_state": {"scene": "introduction"},
        "character_ids": [character['id']]
    }
    
    response = test_client.post("/api/v1/stories/", json=story_data)
    
    assert response.status_code == 200
    
    story = StoryResponse(**response.json())
    assert story.title == "Test Story"
    assert story.description == "A story for unit testing"
    assert story.current_state == {"scene": "introduction"}
    assert story.id is not None

@pytest.mark.asyncio
async def test_list_stories(test_client, async_session: AsyncSession):
    """Test listing stories with pagination"""
    # Create a character first
    character_response = test_client.post("/api/v1/characters/", json={
        "name": "Story List Character",
        "description": "Character for story list testing"
    })
    character = character_response.json()
    
    # Create a few test stories
    for i in range(3):
        story_data = {
            "title": f"Test Story {i}",
            "description": f"Test description {i}",
            "character_ids": [character['id']]
        }
        test_client.post("/api/v1/stories/", json=story_data)
    
    response = test_client.get("/api/v1/stories/")
    
    assert response.status_code == 200
    
    stories = response.json()
    assert len(stories) >= 3
    
    # Verify response schema
    for story in stories:
        story_model = StoryResponse(**story)
        assert story_model.title.startswith("Test Story")

@pytest.mark.asyncio
async def test_get_story(test_client, async_session: AsyncSession):
    """Test retrieving a specific story"""
    # First, create a character
    character_response = test_client.post("/api/v1/characters/", json={
        "name": "Story Retrieval Character",
        "description": "Character for story retrieval testing"
    })
    character = character_response.json()
    
    # Create a story
    story_data = {
        "title": "Unique Story",
        "description": "A story to be retrieved",
        "character_ids": [character['id']]
    }
    create_response = test_client.post("/api/v1/stories/", json=story_data)
    created_story = create_response.json()
    
    # Then, retrieve the story
    response = test_client.get(f"/api/v1/stories/{created_story['id']}")
    
    assert response.status_code == 200
    
    story = StoryResponse(**response.json())
    assert story.title == "Unique Story"
    assert story.description == "A story to be retrieved"

@pytest.mark.asyncio
async def test_update_story(test_client, async_session: AsyncSession):
    """Test updating an existing story"""
    # First, create a character
    character_response = test_client.post("/api/v1/characters/", json={
        "name": "Story Update Character",
        "description": "Character for story update testing"
    })
    character = character_response.json()
    
    # Create a story
    story_data = {
        "title": "Original Story",
        "description": "To be updated",
        "character_ids": [character['id']]
    }
    create_response = test_client.post("/api/v1/stories/", json=story_data)
    created_story = create_response.json()
    
    # Update the story
    update_data = {
        "title": "Updated Story",
        "description": "Updated description",
        "current_state": {"scene": "climax"}
    }
    response = test_client.put(f"/api/v1/stories/{created_story['id']}", json=update_data)
    
    assert response.status_code == 200
    
    updated_story = StoryResponse(**response.json())
    assert updated_story.title == "Updated Story"
    assert updated_story.description == "Updated description"
    assert updated_story.current_state == {"scene": "climax"}

@pytest.mark.asyncio
async def test_delete_story(test_client, async_session: AsyncSession):
    """Test deleting a story"""
    # First, create a character
    character_response = test_client.post("/api/v1/characters/", json={
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
    create_response = test_client.post("/api/v1/stories/", json=story_data)
    created_story = create_response.json()
    
    # Delete the story
    response = test_client.delete(f"/api/v1/stories/{created_story['id']}")
    
    assert response.status_code == 204
    
    # Verify the story is no longer retrievable
    get_response = test_client.get(f"/api/v1/stories/{created_story['id']}")
    assert get_response.status_code == 404