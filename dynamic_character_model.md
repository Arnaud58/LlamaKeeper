# Dynamic Character Model Implementation

## Overview
A sophisticated, flexible character model that supports dynamic trait management, autonomous behavior generation, and context-aware interactions.

## Implementation

```python
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from enum import Enum, auto
from dataclasses import dataclass, field
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

@dataclass
class PersonalityTrait:
    """
    Represents a single personality trait with nuanced characteristics
    """
    name: str
    category: PersonalityTraitCategory
    value: float = 0.5  # Normalized value between 0 and 1
    description: Optional[str] = None
    
    def __post_init__(self):
        """
        Validate trait value
        """
        self.value = max(0.0, min(1.0, self.value))

class DynamicCharacterModel:
    """
    Advanced character model with dynamic trait management
    Supports complex personality modeling and autonomous behavior generation
    """
    
    def __init__(
        self, 
        name: str,
        background: Optional[str] = None,
        initial_traits: Optional[List[PersonalityTrait]] = None
    ):
        """
        Initialize a character with dynamic personality traits
        
        Args:
            name (str): Character's name
            background (str, optional): Character's backstory
            initial_traits (List[PersonalityTrait], optional): Initial personality traits
        """
        self.id: UUID = uuid4()
        self.name: str = name
        self.background: Optional[str] = background
        
        # Dynamic trait management
        self._traits: Dict[str, PersonalityTrait] = {}
        self._trait_history: Dict[str, List[Dict[str, Any]]] = {}
        
        # Initialize traits
        if initial_traits:
            for trait in initial_traits:
                self.add_or_update_trait(trait)
        
        # Memory and context tracking
        self._memory_context: List[Dict[str, Any]] = []
        self._goals: List[Dict[str, Any]] = []
    
    def add_or_update_trait(
        self, 
        trait: PersonalityTrait, 
        reason: Optional[str] = None
    ):
        """
        Add or update a personality trait
        
        Args:
            trait (PersonalityTrait): Trait to add or update
            reason (str, optional): Reason for trait modification
        """
        # Track trait history
        if trait.name not in self._trait_history:
            self._trait_history[trait.name] = []
        
        # Record trait modification
        modification_record = {
            'timestamp': datetime.now(),
            'old_value': self._traits.get(trait.name, {}).get('value'),
            'new_value': trait.value,
            'reason': reason
        }
        self._trait_history[trait.name].append(modification_record)
        
        # Update or add trait
        self._traits[trait.name] = trait
    
    def get_trait(self, trait_name: str) -> Optional[PersonalityTrait]:
        """
        Retrieve a specific trait
        
        Args:
            trait_name (str): Name of the trait
        
        Returns:
            Optional[PersonalityTrait]: Trait if found
        """
        return self._traits.get(trait_name)
    
    def get_traits_by_category(
        self, 
        category: PersonalityTraitCategory
    ) -> List[PersonalityTrait]:
        """
        Retrieve traits by category
        
        Args:
            category (PersonalityTraitCategory): Trait category
        
        Returns:
            List[PersonalityTrait]: Traits in the specified category
        """
        return [
            trait for trait in self._traits.values() 
            if trait.category == category
        ]
    
    def generate_action(
        self, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an autonomous action based on personality traits and context
        
        Args:
            context (Dict): Current story/interaction context
        
        Returns:
            Dict: Generated character action
        """
        # Analyze relevant traits
        emotional_traits = self.get_traits_by_category(
            PersonalityTraitCategory.EMOTIONAL
        )
        motivational_traits = self.get_traits_by_category(
            PersonalityTraitCategory.MOTIVATIONAL
        )
        
        # Determine action based on trait analysis
        action_likelihood = sum(
            trait.value for trait in emotional_traits + motivational_traits
        ) / (len(emotional_traits) + len(motivational_traits))
        
        # Generate action with probabilistic approach
        action = {
            'character_id': str(self.id),
            'name': self.name,
            'action_type': self._determine_action_type(action_likelihood),
            'emotional_state': self._analyze_emotional_state(),
            'motivation': self._determine_motivation(context),
            'confidence': action_likelihood
        }
        
        return action
    
    def _determine_action_type(self, likelihood: float) -> str:
        """
        Determine action type based on personality traits
        
        Args:
            likelihood (float): Probability of action
        
        Returns:
            str: Action type
        """
        action_types = [
            'dialogue', 
            'movement', 
            'internal_thought', 
            'interaction', 
            'decision'
        ]
        
        # Use likelihood to select action type
        index = int(likelihood * (len(action_types) - 1))
        return action_types[index]
    
    def _analyze_emotional_state(self) -> str:
        """
        Analyze character's emotional state based on traits
        
        Returns:
            str: Emotional state description
        """
        emotional_traits = self.get_traits_by_category(
            PersonalityTraitCategory.EMOTIONAL
        )
        
        # Aggregate emotional trait values
        avg_emotion = sum(
            trait.value for trait in emotional_traits
        ) / len(emotional_traits) if emotional_traits else 0.5
        
        emotional_states = [
            'calm', 'neutral', 'excited', 
            'anxious', 'confident', 'hesitant'
        ]
        
        # Map average emotion to state
        index = int(avg_emotion * (len(emotional_states) - 1))
        return emotional_states[index]
    
    def _determine_motivation(
        self, 
        context: Dict[str, Any]
    ) -> str:
        """
        Determine character's motivation based on context and traits
        
        Args:
            context (Dict): Current interaction context
        
        Returns:
            str: Motivation description
        """
        motivational_traits = self.get_traits_by_category(
            PersonalityTraitCategory.MOTIVATIONAL
        )
        
        # Analyze context and traits
        motivation_factors = [
            trait.name for trait in motivational_traits 
            if trait.value > 0.6
        ]
        
        return f"Driven by {', '.join(motivation_factors)}"
    
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
        memory_entry = {
            **memory,
            'timestamp': datetime.now(),
            'importance': importance
        }
        
        self._memory_context.append(memory_entry)
        
        # Limit memory context size
        if len(self._memory_context) > 100:
            # Remove least important memories
            self._memory_context.sort(
                key=lambda m: m['importance']
            )
            self._memory_context = self._memory_context[-100:]
    
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
        # Sort by importance and timestamp
        sorted_memories = sorted(
            self._memory_context,
            key=lambda m: (m['importance'], m['timestamp']),
            reverse=True
        )
        
        return sorted_memories[:top_k]

# Example Usage
def create_example_character():
    """
    Create an example character with dynamic traits
    """
    brave_trait = PersonalityTrait(
        name='bravery', 
        category=PersonalityTraitCategory.EMOTIONAL,
        value=0.8,
        description='Courageous and willing to take risks'
    )
    
    curious_trait = PersonalityTrait(
        name='curiosity', 
        category=PersonalityTraitCategory.COGNITIVE,
        value=0.7,
        description='Eager to learn and explore'
    )
    
    character = DynamicCharacterModel(
        name='Aria the Explorer',
        background='A young adventurer from a remote mountain village',
        initial_traits=[brave_trait, curious_trait]
    )
    
    return character
```

## Key Features

1. **Dynamic Trait Management**
   - Categorized personality traits
   - Trait value normalization
   - Trait history tracking

2. **Autonomous Action Generation**
   - Context-aware action generation
   - Probabilistic action selection
   - Emotional state analysis

3. **Memory and Context Tracking**
   - Flexible memory context storage
   - Importance-based memory management
   - Contextual memory retrieval

4. **Extensibility**
   - Easy trait addition and modification
   - Support for complex personality modeling
   - Adaptable action generation

## Trait Categories

- **Emotional**: Mood, sensitivity, reactivity
- **Social**: Interaction style, communication
- **Cognitive**: Learning, problem-solving
- **Motivational**: Goals, drives
- **Behavioral**: Action tendencies

## Benefits

- **Flexibility**: Easily modify character traits
- **Depth**: Complex personality modeling
- **Autonomy**: Self-driven character actions
- **Contextual Awareness**: Adaptive behavior

## Recommended Next Steps

1. Implement advanced trait interaction logic
2. Create more sophisticated action generation
3. Develop trait evolution mechanisms
4. Add machine learning-based trait prediction