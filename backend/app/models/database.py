from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime, timezone

Base = declarative_base()

# Configuration de la base de données
DATABASE_URL = "sqlite+aiosqlite:///./ai_dungeon.db"

# Création de l'engine asynchrone
async_engine = create_async_engine(
    DATABASE_URL, 
    echo=False,
    future=True
)

# Création du générateur de session asynchrone
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

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
        cascade="save-update, merge"
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
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_models():
    """
    Initialise les modèles de base de données
    Crée les tables si elles n'existent pas
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
