from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker, selectinload
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime, timezone
import logging

from app.core.config import settings

# Configuration du logging
logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()

# Configuration de la base de données utilisant la configuration centralisée
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI
logger.info(f"Configuration de la base de données : {DATABASE_URL}")

# Création de l'engine asynchrone
try:
    async_engine = create_async_engine(
        DATABASE_URL, 
        echo=settings.DEBUG,
        future=True
    )
    logger.info("Engine asynchrone créé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de la création de l'engine asynchrone : {e}")
    raise

# Création du générateur de session asynchrone
try:
    AsyncSessionLocal = async_sessionmaker(
        async_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    logger.info("Générateur de session asynchrone créé avec succès")
except Exception as e:
    logger.error(f"Erreur lors de la création du générateur de session : {e}")
    raise

# Table d'association pour la relation many-to-many entre Story et Character
story_characters = Table(
    'story_characters', Base.metadata,
    Column('story_id', Integer, ForeignKey('stories.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

class Character(Base):
    """Modèle SQLAlchemy pour les personnages"""
    __tablename__ = 'characters'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    personality = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    stories = relationship(
        "Story", 
        secondary=story_characters, 
        back_populates="characters",
        cascade="save-update, merge"
    )
    memories = relationship("Memory", back_populates="character", cascade="all, delete-orphan")
    actions = relationship("Action", back_populates="character", cascade="all, delete-orphan")


class Story(Base):
    """Modèle SQLAlchemy pour les histoires"""
    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=True)
    current_state = Column(JSON, nullable=True, default={})
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=True, onupdate=lambda: datetime.now(timezone.utc))

    # Relations
    characters = relationship(
        "Character",
        secondary=story_characters,
        back_populates="stories",
        cascade="save-update, merge",
        lazy="joined"  # Forcer le chargement immédiat
    )
    actions = relationship("Action", back_populates="story", cascade="all, delete-orphan")


class Action(Base):
    """Modèle SQLAlchemy pour les actions"""
    __tablename__ = 'actions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    content = Column(String(1000), nullable=False)
    action_type = Column(String(100), nullable=False)
    reaction = Column(String(1000), nullable=True)
    context = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    story = relationship("Story", back_populates="actions")
    character = relationship("Character", back_populates="actions")


class Memory(Base):
    """Modèle SQLAlchemy pour les mémoires"""
    __tablename__ = 'memories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    content = Column(String(1000), nullable=False)
    importance = Column(Float, default=0.5)
    context = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Relations
    character = relationship("Character", back_populates="memories")


async def get_async_session() -> AsyncSession:
    """
    Fonction utilitaire pour obtenir une session asynchrone
    
    :return: Une session asynchrone
    """
    logger.debug("Tentative d'obtention d'une session asynchrone")
    async with AsyncSessionLocal() as session:
        try:
            yield session
            logger.debug("Session asynchrone obtenue avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'obtention de la session : {e}")
            raise
        finally:
            await session.close()
            logger.debug("Session asynchrone fermée")


async def init_models():
    """
    Initialise les modèles de base de données
    Crée les tables si elles n'existent pas
    """
    logger.info("Initialisation des modèles de base de données")
    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Création des tables réussie")
    except Exception as e:
        logger.error(f"Erreur lors de la création des tables : {e}")
        raise

# Exporter explicitement les modèles
__all__ = ['Character', 'Story', 'Action', 'Memory', 'get_async_session', 'init_models']
