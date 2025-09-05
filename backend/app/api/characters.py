from typing import List
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# Configuration du logging
logger = logging.getLogger(__name__)

from app.api.schemas import CharacterBase, CharacterCreate, CharacterResponse
from app.models import database as db_models
from app.models.database import get_async_session

router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=CharacterResponse)
async def create_character(
    character: CharacterCreate, session: AsyncSession = Depends(get_async_session)
):
    """Create a new character"""
    try:
        db_character = db_models.Character(
            name=character.name,
            description=character.description,
            personality=character.personality or {}
        )

        session.add(db_character)
        await session.flush()  # Flush to get the ID without committing
        
        # Vérification explicite de la persistance
        result = await session.execute(
            select(db_models.Character).filter(db_models.Character.id == db_character.id)
        )
        persisted_character = result.scalar_one_or_none()
        
        if persisted_character is None:
            logger.error(f"Échec de la persistance du personnage : {db_character.__dict__}")
            raise HTTPException(status_code=500, detail="Erreur de persistance du personnage")
        
        return db_character
    except Exception as e:
        logger.error(f"Erreur lors de la création du personnage : {e}")
        await session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[CharacterResponse])
async def list_characters(
    session: AsyncSession = Depends(get_async_session), skip: int = 0, limit: int = 10
):
    """List characters with optional pagination"""
    result = await session.execute(
        select(db_models.Character).offset(skip).limit(limit)
    )
    characters = result.scalars().all()
    return characters

@router.delete("/purge", status_code=204)
async def purge_characters(
    session: AsyncSession = Depends(get_async_session)
):
    """Purge all characters from the database"""
    await session.execute(delete(db_models.Character))
    await session.commit()
    return None


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    character_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Get a specific character by ID"""
    logger.debug(f"Tentative de récupération du personnage avec l'ID : {character_id}")
    
    try:
        result = await session.execute(
            select(db_models.Character).where(db_models.Character.id == character_id)
        )
        character = result.scalar_one_or_none()

        if not character:
            logger.warning(f"Personnage non trouvé pour l'ID : {character_id}")
            raise HTTPException(status_code=404, detail="Personnage non trouvé")

        return character

    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la récupération du personnage : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character(
    character_id: int,
    character_update: CharacterBase,
    session: AsyncSession = Depends(get_async_session),
):
    """Update an existing character"""
    logger.debug(f"Tentative de mise à jour du personnage avec l'ID : {character_id}")
    
    try:
        # First, verify the character exists
        result = await session.execute(
            select(db_models.Character).where(db_models.Character.id == character_id)
        )
        existing_character = result.scalar_one_or_none()

        if not existing_character:
            logger.warning(f"Personnage non trouvé pour l'ID : {character_id}")
            raise HTTPException(status_code=404, detail="Personnage non trouvé")

        # Update character attributes using SQLAlchemy methods
        stmt = (
            update(db_models.Character)
            .where(db_models.Character.id == character_id)
            .values(
                name=character_update.name,
                description=character_update.description,
                personality=character_update.personality or {},
                updated_at=datetime.now(timezone.utc)
            )
        )
        
        await session.execute(stmt)
        await session.commit()
        
        # Retrieve the updated character
        result = await session.execute(
            select(db_models.Character).where(db_models.Character.id == character_id)
        )
        updated_character = result.scalar_one_or_none()
        
        if not updated_character:
            logger.error(f"Impossible de récupérer le personnage mis à jour : {character_id}")
            raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du personnage")
        
        logger.info(f"Personnage mis à jour avec succès : {character_id}")
        return updated_character
    
    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la mise à jour du personnage : {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Delete a character"""
    logger.debug(f"Tentative de suppression du personnage avec l'ID : {character_id}")
    
    try:
        # First, verify the character exists
        result = await session.execute(
            select(db_models.Character).where(db_models.Character.id == character_id)
        )
        existing_character = result.scalar_one_or_none()

        if not existing_character:
            logger.warning(f"Personnage non trouvé pour l'ID : {character_id}")
            raise HTTPException(status_code=404, detail="Personnage non trouvé")

        await session.delete(existing_character)
        await session.commit()

        logger.info(f"Personnage supprimé avec succès : {character_id}")
        return None

    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la suppression du personnage : {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
