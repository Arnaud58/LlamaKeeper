from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Table, func
from sqlalchemy.orm import relationship, declarative_base, mapped_column, Mapped
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, AsyncGenerator

from app.core.config import settings

# Configuration de l'engine asynchrone
async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    future=True
)

# Création du sessionmaker asynchrone
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

# Table d'association pour la relation many-to-many entre Story et Character
story_characters = Table(
    'story_characters', Base.metadata,
    Column('story_id', Integer, ForeignKey('stories.id'), primary_key=True),
    Column('character_id', Integer, ForeignKey('characters.id'), primary_key=True)
)

class Character(Base):
    """Modèle SQLAlchemy pour les personnages"""
    __tablename__ = 'characters'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    personality: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True, default=func.now())

    # Relations
    stories: Mapped[List['Story']] = relationship(
        'Story', 
        secondary=story_characters, 
        back_populates='characters'
    )
    actions: Mapped[List['Action']] = relationship('Action', back_populates='character')
    memories: Mapped[List['Memory']] = relationship('Memory', back_populates='character')

    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}')>"


class Story(Base):
    """Modèle SQLAlchemy pour les histoires"""
    __tablename__ = 'stories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True, default=func.now())
    current_state: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    is_completed: Mapped[bool] = mapped_column(default=False)

    # Relations
    characters: Mapped[List[Character]] = relationship(
        'Character', 
        secondary=story_characters, 
        back_populates='stories'
    )
    actions: Mapped[List['Action']] = relationship('Action', back_populates='story')

    def __repr__(self):
        return f"<Story(id={self.id}, title='{self.title}')>"


class Action(Base):
    """Modèle SQLAlchemy pour les actions des personnages"""
    __tablename__ = 'actions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    story_id: Mapped[int] = mapped_column(ForeignKey('stories.id'), nullable=False)
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'), nullable=False)
    content: Mapped[str] = mapped_column(String(1000), nullable=False)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reaction: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True, default=func.now())

    # Relations
    story: Mapped[Story] = relationship('Story', back_populates='actions')
    character: Mapped[Character] = relationship('Character', back_populates='actions')

    def __repr__(self):
        return f"<Action(id={self.id}, action_type='{self.action_type}')>"


class Memory(Base):
    """Modèle SQLAlchemy pour les mémoires des personnages"""
    __tablename__ = 'memories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(ForeignKey('characters.id'), nullable=False)
    content: Mapped[str] = mapped_column(String(2000), nullable=False)
    importance: Mapped[float] = mapped_column(default=0.5)
    context: Mapped[Dict[str, Any]] = mapped_column(JSON, default={})
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=True, default=func.now())

    # Relations
    character: Mapped[Character] = relationship('Character', back_populates='memories')

    def __repr__(self):
        return f"<Memory(id={self.id}, importance={self.importance})>"


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Générateur de sessions asynchrones pour les dépendances FastAPI
    
    Yields:
        AsyncSession: Une session de base de données asynchrone
    """
    try:
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        await session.close()


async def init_models():
    """
    Initialise les modèles de base de données.
    Crée toutes les tables définies dans les modèles Base.
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
