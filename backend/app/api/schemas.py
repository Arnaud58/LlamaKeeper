import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class BaseModelWithTimestamps(BaseModel):
    """Base model with common timestamp fields"""

    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CharacterBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    personality: Optional[Dict] = None


class CharacterCreate(CharacterBase):
    pass


class CharacterResponse(CharacterBase, BaseModelWithTimestamps):
    id: int  # Changed to match database model


class StoryBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    current_state: Optional[Dict] = None


class StoryCreate(StoryBase):
    character_ids: List[int] = []  # Changed to match database model


class StoryResponse(StoryBase, BaseModelWithTimestamps):
    id: int  # Changed to match database model
    is_completed: bool = False


class ActionBase(BaseModel):
    content: str
    action_type: str
    reaction: Optional[str] = None
    context: Optional[Dict] = None


class ActionCreate(ActionBase):
    story_id: int  # Changed to match database model
    character_id: int  # Changed to match database model


class ActionResponse(ActionBase, BaseModelWithTimestamps):
    id: int


class MemoryBase(BaseModel):
    content: str
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    context: Optional[Dict] = None


class MemoryCreate(MemoryBase):
    character_id: int  # Changed to match database model


class MemoryResponse(MemoryBase, BaseModelWithTimestamps):
    id: int
    last_accessed: Optional[datetime] = None
