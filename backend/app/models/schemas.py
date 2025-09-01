import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .database import Character as SQLCharacter, Story as SQLStory, Action as SQLAction, Memory as SQLMemory


class CharacterBase(BaseModel):
    """Base model for character creation and updates"""

    name: str = Field(..., min_length=2, max_length=100, description="Character name")
    description: Optional[str] = Field(
        None, max_length=500, description="Character description"
    )
    personality: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

    def to_sqlalchemy(self) -> SQLCharacter:
        """Convert Pydantic model to SQLAlchemy model"""
        return SQLCharacter(
            name=self.name,
            description=self.description,
            personality=self.personality or {},
            created_at=datetime.now(timezone.utc)
        )

    @validator('name')
    def validate_name(cls, v):
        """Validate character name"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Character name must be at least 2 characters long")
        return v


class CharacterCreate(CharacterBase):
    """Model for creating a new character"""
    pass


class Character(CharacterBase):
    """Model for returning character details"""

    id: Optional[int] = None
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def from_sqlalchemy(cls, sql_character: SQLCharacter):
        """Convert SQLAlchemy model to Pydantic model"""
        return cls(
            id=sql_character.id,
            name=sql_character.name,
            description=sql_character.description,
            personality=sql_character.personality,
            created_at=sql_character.created_at
        )


class StoryBase(BaseModel):
    """Base model for story creation and updates"""

    title: str = Field(..., min_length=2, max_length=200, description="Story title")
    description: Optional[str] = Field(
        None, max_length=1000, description="Story description"
    )
    character_ids: Optional[List[int]] = None
    current_state: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

    def to_sqlalchemy(self, character_list: Optional[List[SQLCharacter]] = None) -> SQLStory:
        """Convert Pydantic model to SQLAlchemy model"""
        story = SQLStory(
            title=self.title,
            description=self.description,
            current_state=self.current_state or {},
            is_completed=False,
            created_at=datetime.now(timezone.utc)
        )
        
        # Ajouter les personnages si fournis
        if character_list:
            story.characters = character_list
        
        return story

    @validator('title')
    def validate_title(cls, v):
        """Validate story title"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Story title must be at least 2 characters long")
        return v


class StoryCreate(StoryBase):
    """Model for creating a new story"""
    pass


class Story(StoryBase):
    """Model for returning story details"""

    id: Optional[int] = None
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    is_completed: bool = False
    characters: List[Character] = []

    @classmethod
    def from_sqlalchemy(cls, sql_story: SQLStory):
        """Convert SQLAlchemy model to Pydantic model"""
        return cls(
            id=sql_story.id,
            title=sql_story.title,
            description=sql_story.description,
            current_state=sql_story.current_state,
            created_at=sql_story.created_at,
            is_completed=sql_story.is_completed,
            characters=[Character.from_sqlalchemy(char) for char in sql_story.characters]
        )


class ActionBase(BaseModel):
    """Base model for character actions in stories"""

    story_id: int
    character_id: int
    content: str = Field(..., description="Action description")
    action_type: str = Field(..., description="Type of action")
    reaction: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

    def to_sqlalchemy(self, story: Optional[SQLStory] = None, character: Optional[SQLCharacter] = None) -> SQLAction:
        """Convert Pydantic model to SQLAlchemy model"""
        return SQLAction(
            story_id=self.story_id,
            character_id=self.character_id,
            content=self.content,
            action_type=self.action_type,
            reaction=self.reaction,
            context=self.context or {},
            created_at=datetime.now(timezone.utc),
            story=story,
            character=character
        )

    @validator('content')
    def validate_content(cls, v):
        """Validate action content"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Action content must be at least 2 characters long")
        return v


class ActionCreate(ActionBase):
    """Model for creating a new action"""
    pass


class Action(ActionBase):
    """Model for returning action details"""

    id: Optional[int] = None
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    story: Optional[Story] = None
    character: Optional[Character] = None

    @classmethod
    def from_sqlalchemy(cls, sql_action: SQLAction):
        """Convert SQLAlchemy model to Pydantic model"""
        return cls(
            id=sql_action.id,
            story_id=sql_action.story_id,
            character_id=sql_action.character_id,
            content=sql_action.content,
            action_type=sql_action.action_type,
            reaction=sql_action.reaction,
            context=sql_action.context,
            created_at=sql_action.created_at,
            story=Story.from_sqlalchemy(sql_action.story) if sql_action.story else None,
            character=Character.from_sqlalchemy(sql_action.character) if sql_action.character else None
        )


class CharacterWithStories(Character):
    """Model for returning a character with their associated stories"""

    stories: List[Story] = []
    actions: List[Action] = []


class MemoryBase(BaseModel):
    """Base model for character memories"""

    character_id: int
    content: str
    importance: float = Field(default=0.5, ge=0, le=1)
    context: Optional[Dict[str, Any]] = None
    model_config = ConfigDict(from_attributes=True)

    def to_sqlalchemy(self, character: Optional[SQLCharacter] = None) -> SQLMemory:
        """Convert Pydantic model to SQLAlchemy model"""
        return SQLMemory(
            character_id=self.character_id,
            content=self.content,
            importance=self.importance,
            context=self.context or {},
            created_at=datetime.now(timezone.utc),
            character=character
        )

    @validator('content')
    def validate_content(cls, v):
        """Validate memory content"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Memory content must be at least 2 characters long")
        return v


class MemoryCreate(MemoryBase):
    """Model for creating a new memory"""
    pass


class Memory(MemoryBase):
    """Model for returning memory details"""

    id: Optional[int] = None
    created_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def from_sqlalchemy(cls, sql_memory: SQLMemory):
        """Convert SQLAlchemy model to Pydantic model"""
        return cls(
            id=sql_memory.id,
            character_id=sql_memory.character_id,
            content=sql_memory.content,
            importance=sql_memory.importance,
            context=sql_memory.context,
            created_at=sql_memory.created_at
        )
