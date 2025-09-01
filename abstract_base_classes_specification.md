# Abstract Base Classes Specification for LlamaKeeper

## Overview
These abstract base classes will provide a standardized interface for key components of the LlamaKeeper system, ensuring modularity, extensibility, and consistent behavior across different implementations.

## 1. AbstractAIModelPlugin

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from uuid import UUID

class AbstractAIModelPlugin(ABC):
    """
    Abstract base class for AI model plugins
    Defines a standard interface for text generation across different AI backends
    """
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        context: Optional[Dict[str, Any]] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text using the AI model
        
        Args:
            prompt (str): Input prompt for text generation
            context (Dict, optional): Contextual information for generation
            parameters (Dict, optional): Model-specific generation parameters
        
        Returns:
            str: Generated text
        """
        pass
    
    @abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Retrieve comprehensive metadata about the AI model
        
        Returns:
            Dict: Model metadata (capabilities, version, etc.)
        """
        pass
    
    @abstractmethod
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration for the AI model
        
        Args:
            config (Dict): Model configuration parameters
        
        Returns:
            bool: Whether the configuration is valid
        """
        pass
```

## 2. AbstractCharacterModel

```python
class AbstractCharacterModel(ABC):
    """
    Abstract base class for character representation
    Supports dynamic trait and personality management
    """
    
    @abstractmethod
    def __init__(
        self, 
        name: str, 
        personality: Dict[str, Any],
        background: Optional[str] = None
    ):
        """
        Initialize a character with core attributes
        
        Args:
            name (str): Character name
            personality (Dict): Character personality traits
            background (str, optional): Character's backstory
        """
        pass
    
    @abstractmethod
    def update_personality_trait(
        self, 
        trait_name: str, 
        trait_value: Any
    ) -> None:
        """
        Update or add a personality trait
        
        Args:
            trait_name (str): Name of the trait
            trait_value (Any): Value of the trait
        """
        pass
    
    @abstractmethod
    def generate_action(
        self, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an autonomous action based on character traits and context
        
        Args:
            context (Dict): Current story/interaction context
        
        Returns:
            Dict: Generated character action
        """
        pass
    
    @abstractmethod
    def get_memory_context(self) -> Dict[str, Any]:
        """
        Retrieve the character's current memory context
        
        Returns:
            Dict: Character's memory and contextual information
        """
        pass
```

## 3. AbstractMemoryManager

```python
class AbstractMemoryManager(ABC):
    """
    Abstract base class for memory management
    Supports flexible memory storage, retrieval, and relevance scoring
    """
    
    @abstractmethod
    async def store_memory(
        self, 
        character_id: UUID, 
        memory_content: str, 
        context: Optional[Dict[str, Any]] = None,
        importance: float = 0.5
    ) -> UUID:
        """
        Store a memory for a character
        
        Args:
            character_id (UUID): ID of the character
            memory_content (str): Content of the memory
            context (Dict, optional): Contextual metadata
            importance (float, optional): Memory importance score
        
        Returns:
            UUID: Unique identifier for the stored memory
        """
        pass
    
    @abstractmethod
    async def retrieve_relevant_memories(
        self, 
        character_id: UUID, 
        context: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant memories for a character
        
        Args:
            character_id (UUID): ID of the character
            context (Dict): Context for relevance matching
            top_k (int, optional): Number of top memories to retrieve
        
        Returns:
            List[Dict]: Most relevant memories
        """
        pass
    
    @abstractmethod
    async def forget_memories(
        self, 
        character_id: UUID, 
        forget_threshold: float = 0.2,
        max_memories: int = 100
    ) -> None:
        """
        Manage memory capacity by forgetting less important memories
        
        Args:
            character_id (UUID): ID of the character
            forget_threshold (float, optional): Importance threshold for forgetting
            max_memories (int, optional): Maximum number of memories to keep
        """
        pass
```

## 4. AbstractGenerationPipeline

```python
class AbstractGenerationPipeline(ABC):
    """
    Abstract base class for narrative generation pipeline
    Coordinates between AI models, characters, and memory systems
    """
    
    @abstractmethod
    async def generate_story_progression(
        self, 
        current_story: Dict[str, Any],
        characters: List[AbstractCharacterModel],
        narrative_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Generate progression for an ongoing story
        
        Args:
            current_story (Dict): Current story state
            characters (List[AbstractCharacterModel]): Characters in the story
            narrative_goals (List[str]): Desired narrative directions
        
        Returns:
            Dict: Story progression details
        """
        pass
    
    @abstractmethod
    async def generate_character_interaction(
        self, 
        initiating_character: AbstractCharacterModel,
        target_character: AbstractCharacterModel,
        interaction_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an interaction between two characters
        
        Args:
            initiating_character (AbstractCharacterModel): Character starting the interaction
            target_character (AbstractCharacterModel): Character being interacted with
            interaction_context (Dict): Context of the interaction
        
        Returns:
            Dict: Character interaction details
        """
        pass
```

## Design Principles

1. **Standardization**: Consistent interfaces across different implementations
2. **Flexibility**: Easy to extend and replace components
3. **Abstraction**: Hide implementation details
4. **Modularity**: Components can be developed and tested independently

## Implementation Guidelines

- Each abstract base class defines a clear contract
- Implementations must provide concrete methods for all abstract methods
- Use type hints and docstrings for clear documentation
- Support optional parameters for maximum flexibility

## Next Steps

1. Create base implementations for each abstract class
2. Develop plugin discovery mechanism
3. Implement dependency injection
4. Create test suites for each abstract base class