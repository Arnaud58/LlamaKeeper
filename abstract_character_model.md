# Abstract Character Model Specification

## Overview
A comprehensive abstract base class for character models in the LlamaKeeper system, designed to provide a flexible and extensible foundation for character representation.

## Implementation

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from enum import Enum, auto
from datetime import datetime

class PersonalityTraitCategory(Enum):
    """
    Categorization of personality traits
    Provides a structured approach to trait classification
    """
    EMOTIONAL = auto()
    SOCIAL = auto()
    COGNITIVE = auto()
    MOTIVATIONAL = auto()
    BEHAVIORAL = auto()

class AbstractCharacterModel(ABC):
    """
    Abstract base class for character representation
    Supports dynamic trait and personality management
    """
    
    def __init__(
        self, 
        name: str,
        background: Optional[str] = None,
        initial_traits: Optional[List[Dict[str, Any]]] = None
    ):
        """
        Initialize a character with core attributes
        
        Args:
            name (str): Character name
            background (str, optional): Character's backstory
            initial_traits (List[Dict], optional): Initial personality traits
        """
        self.id: UUID = uuid4()
        self.name: str = name
        self.background: Optional[str] = background
        
        # Trait management
        self._traits: Dict[str, Dict[str, Any]] = {}
        self._trait_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize traits
        if initial_traits:
            for trait in initial_traits:
                self.add_or_update_trait(trait)
        
        # Memory and context tracking
        self._memory_context: List[Dict[str, Any]] = []
        self._goals: List[Dict[str, Any]] = []
    
    @abstractmethod
    def add_or_update_trait(
        self, 
        trait: Dict[str, Any], 
        reason: Optional[str] = None
    ):
        """
        Add or update a personality trait
        
        Args:
            trait (Dict): Trait information
            reason (str, optional): Reason for trait modification
        """
        pass
    
    @abstractmethod
    def get_trait(self, trait_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific trait
        
        Args:
            trait_name (str): Name of the trait
        
        Returns:
            Optional[Dict]: Trait information if found
        """
        pass
    
    @abstractmethod
    def get_traits_by_category(
        self, 
        category: PersonalityTraitCategory
    ) -> List[Dict[str, Any]]:
        """
        Retrieve traits by category
        
        Args:
            category (PersonalityTraitCategory): Trait category
        
        Returns:
            List[Dict]: Traits in the specified category
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
    def add_memory_context(
        self, 
        memory: Dict[str, Any], 
        importance: float = 0.5
    ):
        """
        Add a memory to the character's context
        
        Args:
            memory (Dict): Memory details
            importance (float, optional): Memory importance
        """
        pass
    
    @abstractmethod
    def get_memory_context(
        self, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant memory contexts
        
        Args:
            top_k (int, optional): Number of memories to retrieve
        
        Returns:
            List[Dict]: Most relevant memory contexts
        """
        pass
    
    @abstractmethod
    def update_goals(
        self, 
        new_goals: List[Dict[str, Any]]
    ):
        """
        Update character's goals
        
        Args:
            new_goals (List[Dict]): New goals to set
        """
        pass
    
    @abstractmethod
    def get_current_goals(self) -> List[Dict[str, Any]]:
        """
        Retrieve current character goals
        
        Returns:
            List[Dict]: Current active goals
        """
        pass
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of the character's personality
        
        Returns:
            Dict: Personality summary
        """
        return {
            'name': self.name,
            'background': self.background,
            'traits_by_category': {
                category.name: self.get_traits_by_category(category)
                for category in PersonalityTraitCategory
            },
            'goal_summary': self.get_current_goals()
        }

# Example Trait Structure
EXAMPLE_TRAIT = {
    'name': 'bravery',
    'category': PersonalityTraitCategory.EMOTIONAL,
    'value': 0.8,
    'description': 'Courageous and willing to take risks'
}

# Example Usage
def create_character_example():
    """
    Demonstrate abstract character model usage
    """
    class ConcreteCharacterModel(AbstractCharacterModel):
        def add_or_update_trait(
            self, 
            trait: Dict[str, Any], 
            reason: Optional[str] = None
        ):
            # Implement trait addition logic
            pass
        
        def get_trait(self, trait_name: str) -> Optional[Dict[str, Any]]:
            # Implement trait retrieval
            pass
        
        def get_traits_by_category(
            self, 
            category: PersonalityTraitCategory
        ) -> List[Dict[str, Any]]:
            # Implement category-based trait retrieval
            pass
        
        def generate_action(
            self, 
            context: Dict[str, Any]
        ) -> Dict[str, Any]:
            # Implement action generation
            pass
        
        def add_memory_context(
            self, 
            memory: Dict[str, Any], 
            importance: float = 0.5
        ):
            # Implement memory context addition
            pass
        
        def get_memory_context(
            self, 
            top_k: int = 5
        ) -> List[Dict[str, Any]]:
            # Implement memory context retrieval
            pass
        
        def update_goals(
            self, 
            new_goals: List[Dict[str, Any]]
        ):
            # Implement goal update
            pass
        
        def get_current_goals(self) -> List[Dict[str, Any]]:
            # Implement goal retrieval
            pass
    
    # Create a character instance
    character = ConcreteCharacterModel(
        name="Aria the Explorer",
        background="A young adventurer from a remote mountain village",
        initial_traits=[EXAMPLE_TRAIT]
    )
    
    return character
```

## Key Features

1. **Dynamic Trait Management**
   - Categorized personality traits
   - Flexible trait addition and modification
   - Trait history tracking

2. **Autonomous Action Generation**
   - Context-aware action generation
   - Trait-based decision making
   - Flexible action type support

3. **Memory and Context Tracking**
   - Comprehensive memory context storage
   - Importance-based memory management
   - Goal tracking

4. **Extensibility**
   - Abstract base class design
   - Easy to implement custom character models
   - Support for complex personality modeling

## Trait Categories

- **Emotional**: Mood, sensitivity, reactivity
- **Social**: Interaction style, communication
- **Cognitive**: Learning, problem-solving
- **Motivational**: Goals, drives
- **Behavioral**: Action tendencies

## Benefits

- **Flexibility**: Easily create diverse character models
- **Depth**: Complex personality representation
- **Modularity**: Standardized character interface
- **Extensibility**: Support for advanced character modeling

## Recommended Next Steps

1. Implement concrete character model implementations
2. Develop advanced trait interaction logic
3. Create machine learning-based trait prediction
4. Add more sophisticated action generation mechanisms