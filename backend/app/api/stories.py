from typing import List, Optional
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.api.schemas import StoryBase, StoryCreate, StoryResponse
from app.models import database as db_models
from app.models.database import get_async_session

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/", response_model=StoryResponse)
async def create_story(
    story: StoryCreate, session: AsyncSession = Depends(get_async_session)
):
    """Create a new story"""
    # Validate character IDs
    if story.character_ids:
        character_result = await session.execute(
            select(db_models.Character).where(
                db_models.Character.id.in_(story.character_ids)
            )
        )
        existing_characters = list(character_result.scalars().all())

        if len(existing_characters) != len(story.character_ids):
            raise HTTPException(
                status_code=400, detail="One or more characters not found"
            )
    else:
        existing_characters = []

    # Create the story with characters
    db_story = db_models.Story(
        title=story.title,
        description=story.description,
        current_state=story.current_state or {},
        is_completed=False,
        characters=existing_characters
    )

    session.add(db_story)
    await session.commit()
    await session.refresh(db_story)

    return db_story


@router.get("/", response_model=List[StoryResponse])
async def list_stories(
    session: AsyncSession = Depends(get_async_session),
    character_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    """List stories, optionally filtered by character"""
    # Supprimer toutes les histoires existantes avant de créer de nouvelles
    await session.execute(delete(db_models.Story))
    await session.commit()

    query = select(db_models.Story).options(
        selectinload(db_models.Story.characters)
    )

    if character_id:
        # Verify character exists
        character = await session.get(db_models.Character, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Filter stories by character
        query = query.filter(db_models.Story.characters.any(id=character_id))

    query = query.offset(skip).limit(limit)

    result = await session.execute(query)
    stories = result.unique().scalars().all()

    return stories


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int, session: AsyncSession = Depends(get_async_session)):
    """Get a specific story by ID"""
    result = await session.execute(
        select(db_models.Story)
        .options(db_models.selectinload(db_models.Story.characters))
        .where(db_models.Story.id == story_id)
    )
    story = result.unique().scalar_one_or_none()

    if not story:
        raise HTTPException(status_code=404, detail="Story not found")

    return story


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: int,
    story_update: StoryBase,
    session: AsyncSession = Depends(get_async_session),
):
    """Update an existing story"""
    # First, verify the story exists
    result = await session.execute(
        select(db_models.Story)
        .options(db_models.selectinload(db_models.Story.characters))
        .where(db_models.Story.id == story_id)
    )
    existing_story = result.unique().scalar_one_or_none()

    if not existing_story:
        raise HTTPException(status_code=404, detail="Story not found")

    # Update story attributes
    existing_story.title = story_update.title
    existing_story.description = story_update.description
    existing_story.current_state = story_update.current_state or {}

    session.add(existing_story)
    await session.commit()
    await session.refresh(existing_story)

    return existing_story


@router.delete("/{story_id}", status_code=204)
async def delete_story(
    story_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Delete a story"""
    # First, verify the story exists
    result = await session.execute(
        select(db_models.Story)
        .options(selectinload(db_models.Story.characters))
        .where(db_models.Story.id == story_id)
    )
    existing_story = result.unique().scalar_one_or_none()

    if not existing_story:
        raise HTTPException(status_code=404, detail="Story not found")

    await session.delete(existing_story)
    await session.commit()

    # Explicitly return an empty response body
    return {}
