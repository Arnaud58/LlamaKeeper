from typing import List, Optional
from datetime import datetime, timezone
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

# Configuration du logging
logger = logging.getLogger(__name__)

from app.api.schemas import StoryBase, StoryCreate, StoryResponse
from app.models import database as db_models
from app.models.database import get_async_session

router = APIRouter(prefix="/stories", tags=["stories"])


@router.post("/", response_model=StoryResponse)
async def create_story(
    story: StoryCreate, session: AsyncSession = Depends(get_async_session)
):
    """Créer une nouvelle histoire"""
    logger.debug(f"Création d'une histoire : {story}")

    try:
        # Validation des données d'entrée
        if not story.title or len(story.title.strip()) < 2:
            logger.error("Titre de l'histoire invalide")
            raise HTTPException(status_code=400, detail="Le titre doit contenir au moins 2 caractères")

        # Valider les IDs de personnages
        existing_characters = []
        if story.character_ids:
            character_result = await session.execute(
                select(db_models.Character).where(
                    db_models.Character.id.in_(story.character_ids)
                )
            )
            existing_characters = list(character_result.scalars().all())

            if len(existing_characters) != len(story.character_ids):
                existing_character_ids = {c.id for c in existing_characters}
                missing_ids = [cid for cid in story.character_ids if cid not in existing_character_ids]
                logger.error(f"Personnages non trouvés : {missing_ids}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Personnages non trouvés : {missing_ids}"
                )

        # Créer l'histoire avec les personnages
        db_story = db_models.Story(
            title=story.title,
            description=story.description or "",
            current_state=story.current_state or {},
            is_completed=False,
            characters=existing_characters
        )

        # Ajout de logs supplémentaires
        logger.debug(f"Objet histoire avant ajout : {db_story.__dict__}")

        session.add(db_story)
        
        try:
            await session.flush()
            logger.debug(f"Histoire ajoutée avec l'ID : {db_story.id}")
        except Exception as flush_error:
            logger.error(f"Erreur lors du flush : {flush_error}")
            raise HTTPException(status_code=500, detail="Erreur lors de l'ajout de l'histoire")

        # Vérification explicite de la persistance
        try:
            result = await session.execute(
                select(db_models.Story)
                .options(selectinload(db_models.Story.characters))
                .filter(db_models.Story.id == db_story.id)
            )
            persisted_story = result.unique().scalar_one_or_none()

            if persisted_story is None:
                logger.error(f"Échec de la persistance de l'histoire : {db_story.__dict__}")
                await session.rollback()
                raise HTTPException(status_code=500, detail="Erreur de persistance de l'histoire")

            # Commit explicite
            await session.commit()
            logger.info(f"Histoire créée avec succès : {db_story.id}")

        except Exception as persist_error:
            logger.error(f"Erreur de persistance : {persist_error}")
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(persist_error))

        # Convertir l'objet SQLAlchemy en dictionnaire pour la réponse
        story_dict = {
            "id": db_story.id,
            "title": db_story.title,
            "description": db_story.description,
            "current_state": db_story.current_state,
            "is_completed": db_story.is_completed,
            "created_at": db_story.created_at,
            "updated_at": db_story.updated_at,
            "characters": [{"id": c.id, "name": c.name} for c in db_story.characters]
        }

        return story_dict

    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la création de l'histoire : {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Erreur interne lors de la création de l'histoire")


@router.get("/", response_model=List[StoryResponse])
async def list_stories(
    session: AsyncSession = Depends(get_async_session),
    character_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
):
    """Lister les histoires, optionnellement filtrées par personnage"""
    logger.info(f"Listing stories: character_id={character_id}, skip={skip}, limit={limit}")

    try:
        query = select(db_models.Story).options(
            selectinload(db_models.Story.characters)
        )

        if character_id:
            # Vérifier que le personnage existe
            character = await session.get(db_models.Character, character_id)
            if not character:
                raise HTTPException(status_code=404, detail="Personnage non trouvé")

            # Filtrer les histoires par personnage
            query = query.filter(db_models.Story.characters.any(id=character_id))

        query = query.offset(skip).limit(limit)

        result = await session.execute(query)
        stories = result.unique().scalars().all()

        # Convertir les objets SQLAlchemy en dictionnaires
        story_dicts = [
            {
                "id": story.id,
                "title": story.title,
                "description": story.description,
                "current_state": story.current_state,
                "is_completed": story.is_completed,
                "created_at": story.created_at,
                "updated_at": story.updated_at,
                "characters": [{"id": c.id, "name": c.name} for c in story.characters]
            } for story in stories
        ]

        logger.info(f"Trouvé {len(story_dicts)} histoires")
        for story in story_dicts:
            logger.debug(f"Histoire : {story['id']} - {story['title']}")

        return story_dicts

    except Exception as e:
        logger.error(f"Erreur lors de la récupération des histoires : {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(story_id: int, session: AsyncSession = Depends(get_async_session)):
    """Obtenir une histoire spécifique par ID"""
    logger.debug(f"Tentative de récupération de l'histoire avec l'ID : {story_id}")
    
    try:
        result = await session.execute(
            select(db_models.Story)
            .options(selectinload(db_models.Story.characters))
            .where(db_models.Story.id == story_id)
        )
        story = result.unique().scalar_one_or_none()

        if not story:
            logger.warning(f"Histoire non trouvée pour l'ID : {story_id}")
            raise HTTPException(status_code=404, detail="Histoire non trouvée")

        # Convertir l'objet SQLAlchemy en dictionnaire
        story_dict = {
            "id": story.id,
            "title": story.title,
            "description": story.description,
            "current_state": story.current_state,
            "is_completed": story.is_completed,
            "created_at": story.created_at,
            "updated_at": story.updated_at,
            "characters": [{"id": c.id, "name": c.name} for c in story.characters]
        }

        return story_dict

    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la récupération de l'histoire : {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: int,
    story_update: StoryBase,
    session: AsyncSession = Depends(get_async_session),
):
    """Mettre à jour une histoire existante"""
    logger.debug(f"Tentative de mise à jour de l'histoire avec l'ID : {story_id}")
    
    try:
        # Vérifier d'abord que l'histoire existe
        result = await session.execute(
            select(db_models.Story)
            .options(selectinload(db_models.Story.characters))
            .where(db_models.Story.id == story_id)
        )
        existing_story = result.unique().scalar_one_or_none()

        if not existing_story:
            logger.warning(f"Histoire non trouvée pour l'ID : {story_id}")
            raise HTTPException(status_code=404, detail="Histoire non trouvée")

        # Mettre à jour les attributs de l'histoire
        stmt = (
            update(db_models.Story)
            .where(db_models.Story.id == story_id)
            .values(
                title=story_update.title,
                description=story_update.description,
                current_state=story_update.current_state or {},
                updated_at=datetime.now(timezone.utc)
            )
        )

        await session.execute(stmt)
        await session.commit()

        # Récupérer l'histoire mise à jour
        result = await session.execute(
            select(db_models.Story)
            .options(selectinload(db_models.Story.characters))
            .where(db_models.Story.id == story_id)
        )
        updated_story = result.unique().scalar_one_or_none()

        if not updated_story:
            logger.error(f"Impossible de récupérer l'histoire mise à jour : {story_id}")
            raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour de l'histoire")

        # Convertir l'objet SQLAlchemy en dictionnaire
        story_dict = {
            "id": updated_story.id,
            "title": updated_story.title,
            "description": updated_story.description,
            "current_state": updated_story.current_state,
            "is_completed": updated_story.is_completed,
            "created_at": updated_story.created_at,
            "updated_at": updated_story.updated_at,
            "characters": [{"id": c.id, "name": c.name} for c in updated_story.characters]
        }

        logger.info(f"Histoire mise à jour avec succès : {story_id}")
        return story_dict

    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la mise à jour de l'histoire : {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


@router.delete("/{story_id}", status_code=204)
async def delete_story(
    story_id: int, session: AsyncSession = Depends(get_async_session)
):
    """Supprimer une histoire"""
    logger.debug(f"Tentative de suppression de l'histoire avec l'ID : {story_id}")
    
    try:
        # Vérifier d'abord que l'histoire existe
        result = await session.execute(
            select(db_models.Story)
            .options(selectinload(db_models.Story.characters))
            .where(db_models.Story.id == story_id)
        )
        existing_story = result.unique().scalar_one_or_none()

        if not existing_story:
            logger.warning(f"Histoire non trouvée pour l'ID : {story_id}")
            raise HTTPException(status_code=404, detail="Histoire non trouvée")

        await session.delete(existing_story)
        await session.commit()

        logger.info(f"Histoire supprimée avec succès : {story_id}")
        # Retourner explicitement un corps de réponse vide
        return {}

    except HTTPException:
        # Re-raise HTTPException to preserve the original status code
        raise
    except Exception as e:
        logger.error(f"Erreur inattendue lors de la suppression de l'histoire : {e}", exc_info=True)
        await session.rollback()
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
