from typing import List
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.schemas import CharacterBase, CharacterCreate, CharacterResponse
from app.models import database as db_models
from app.models.database import get_async_session

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=CharacterResponse)
async def create_character(
    character: CharacterCreate, session: AsyncSession = Depends(get_async_session)
):
    """Create a new character"""
    db_character = db_models.Character(
        name=character.name,
        description=character.description,
        personality=character.personality or {}
    )

    session.add(db_character)
    await session.commit()
    await session.refresh(db_character)

    return db_character


@router.get("/", response_model=List[CharacterResponse])
async def list_characters(
    session: AsyncSession = Depends(get_async_session), skip: int = 0, limit: int = 100
):
    """List characters with optional pagination"""
    result = await session.execute(
        select(db_models.Character).offset(skip).limit(limit)
    )
    characters = result.scalars().all()
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Get a specific character by ID"""
    result = await session.execute(
        select(db_models.Character).where(db_models.Character.id == character_id)
    )
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    return character


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_update: CharacterBase,
    session: AsyncSession = Depends(get_async_session),
):
    """Update an existing character"""
    # First, verify the character exists
    result = await session.execute(
        select(db_models.Character).where(db_models.Character.id == character_id)
    )
    existing_character = result.scalar_one_or_none()

    if not existing_character:
        raise HTTPException(status_code=404, detail="Character not found")

    # Update character attributes
    existing_character.name = character_update.name
    existing_character.description = character_update.description
    existing_character.personality = character_update.personality or {}

    session.add(existing_character)
    await session.commit()
    await session.refresh(existing_character)

    return existing_character


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Delete a character"""
    # First, verify the character exists
    result = await session.execute(
        select(db_models.Character).where(db_models.Character.id == character_id)
    )
    existing_character = result.scalar_one_or_none()

    if not existing_character:
        raise HTTPException(status_code=404, detail="Character not found")

    await session.delete(existing_character)
    await session.commit()

    return None
