# Character Model Integration with Generation Pipeline

## Overview
A comprehensive approach to integrating the dynamic character model with the narrative generation pipeline, showcasing advanced autonomous storytelling capabilities.

## Implementation

```python
from typing import List, Dict, Any, Optional
from uuid import UUID

from app.models.dynamic_character_model import (
    DynamicCharacterModel, 
    PersonalityTrait, 
    PersonalityTraitCategory
)
from app.core.generation_pipeline import BaseGenerationPipeline
from app.core.ai_model_plugin import AbstractAIModelPlugin
from app.core.memory_manager import AbstractMemoryManager

class AutonomousCharacterGenerationSystem:
    """
    Advanced system for generating and managing autonomous characters
    Integrates dynamic character model with generation pipeline
    """
    
    def __init__(
        self, 
        ai_model_plugin: AbstractAIModelPlugin,
        memory_manager: AbstractMemoryManager,
        generation_pipeline: BaseGenerationPipeline
    ):
        """
        Initialize autonomous character generation system
        
        Args:
            ai_model_plugin (AbstractAIModelPlugin): AI model for text generation
            memory_manager (AbstractMemoryManager): Memory management system
            generation_pipeline (BaseGenerationPipeline): Story generation pipeline
        """
        self._ai_model = ai_model_plugin
        self._memory_manager = memory_manager
        self._generation_pipeline = generation_pipeline
    
    async def create_character_with_background(
        self, 
        name: str, 
        story_context: Dict[str, Any]
    ) -> DynamicCharacterModel:
        """
        Generate a character with a dynamically created background
        
        Args:
            name (str): Character name
            story_context (Dict): Current story context
        
        Returns:
            DynamicCharacterModel: Dynamically generated character
        """
        # Generate character background using AI
        background_prompt = self._construct_background_prompt(
            name, 
            story_context
        )
        
        background_text = await self._ai_model.generate_text(
            prompt=background_prompt,
            context=story_context
        )
        
        # Parse background and generate personality traits
        parsed_background = self._parse_character_background(background_text)
        
        # Create character with dynamically generated traits
        character_traits = self._generate_personality_traits(
            parsed_background
        )
        
        character = DynamicCharacterModel(
            name=name,
            background=parsed_background['description'],
            initial_traits=character_traits
        )
        
        return character
    
    def _construct_background_prompt(
        self, 
        name: str, 
        story_context: Dict[str, Any]
    ) -> str:
        """
        Construct a prompt for generating character background
        
        Args:
            name (str): Character name
            story_context (Dict): Current story context
        
        Returns:
            str: Generated background prompt
        """
        prompt_template = """
        Generate a detailed background for a character named {name}
        in the context of the following story:
        
        Story Context: {context}
        
        Provide a comprehensive background including:
        - Origin and early life
        - Key life experiences
        - Motivations and goals
        - Personality hints
        
        Format the response as a JSON with:
        {{
            "name": "{name}",
            "description": "Detailed background text",
            "origin": "Place of origin",
            "key_experiences": ["Experience 1", "Experience 2"],
            "motivations": ["Motivation 1", "Motivation 2"]
        }}
        """
        
        return prompt_template.format(
            name=name,
            context=str(story_context)
        )
    
    def _parse_character_background(
        self, 
        background_text: str
    ) -> Dict[str, Any]:
        """
        Parse and validate character background
        
        Args:
            background_text (str): Generated background text
        
        Returns:
            Dict: Parsed background information
        """
        try:
            parsed_background = json.loads(background_text)
            
            # Validate background structure
            required_keys = [
                'name', 'description', 
                'origin', 'key_experiences', 
                'motivations'
            ]
            
            for key in required_keys:
                if key not in parsed_background:
                    raise ValueError(f"Missing required key: {key}")
            
            return parsed_background
        
        except (json.JSONDecodeError, ValueError) as e:
            # Fallback background generation
            return {
                'name': parsed_background.get('name', 'Unnamed Character'),
                'description': background_text,
                'origin': 'Unknown',
                'key_experiences': [],
                'motivations': []
            }
    
    def _generate_personality_traits(
        self, 
        background: Dict[str, Any]
    ) -> List[PersonalityTrait]:
        """
        Generate personality traits based on character background
        
        Args:
            background (Dict): Character background information
        
        Returns:
            List[PersonalityTrait]: Generated personality traits
        """
        traits = []
        
        # Emotional traits
        traits.append(PersonalityTrait(
            name='resilience',
            category=PersonalityTraitCategory.EMOTIONAL,
            value=self._calculate_trait_value(
                background['key_experiences'], 
                'challenging'
            ),
            description='Ability to overcome adversity'
        ))
        
        # Motivational traits
        traits.append(PersonalityTrait(
            name='ambition',
            category=PersonalityTraitCategory.MOTIVATIONAL,
            value=self._calculate_trait_value(
                background['motivations'], 
                'achievement'
            ),
            description='Drive to achieve goals'
        ))
        
        # Social traits
        traits.append(PersonalityTrait(
            name='empathy',
            category=PersonalityTraitCategory.SOCIAL,
            value=self._calculate_trait_value(
                background['key_experiences'], 
                'interpersonal'
            ),
            description='Understanding and connecting with others'
        ))
        
        return traits
    
    def _calculate_trait_value(
        self, 
        experiences: List[str], 
        trait_keyword: str
    ) -> float:
        """
        Calculate trait value based on background experiences
        
        Args:
            experiences (List[str]): Character experiences
            trait_keyword (str): Keyword to match
        
        Returns:
            float: Calculated trait value
        """
        matching_experiences = [
            exp for exp in experiences 
            if trait_keyword.lower() in exp.lower()
        ]
        
        # Normalize trait value
        return min(0.8, len(matching_experiences) * 0.3)
    
    async def integrate_character_with_story(
        self, 
        character: DynamicCharacterModel,
        story_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Integrate character into the story generation pipeline
        
        Args:
            character (DynamicCharacterModel): Character to integrate
            story_context (Dict): Current story context
        
        Returns:
            Dict: Updated story context with character integration
        """
        # Generate character's initial action
        initial_action = character.generate_action(story_context)
        
        # Use generation pipeline to expand on character's action
        story_progression = await self._generation_pipeline.generate_story_progression(
            current_story=story_context,
            characters=[character],
            narrative_goals=[initial_action['motivation']]
        )
        
        # Update character's memory based on story progression
        await self._update_character_memory(
            character, 
            story_progression
        )
        
        return {
            'character': character,
            'initial_action': initial_action,
            'story_progression': story_progression
        }
    
    async def _update_character_memory(
        self, 
        character: DynamicCharacterModel,
        story_progression: Dict[str, Any]
    ):
        """
        Update character's memory based on story progression
        
        Args:
            character (DynamicCharacterModel): Character to update
            story_progression (Dict): Story progression details
        """
        # Store key events as memories
        for event in story_progression.get('key_events', []):
            await self._memory_manager.store_memory(
                character_id=character.id,
                memory_content=event,
                importance=0.7,
                context={'type': 'story_event'}
            )
        
        # Update character traits based on progression
        character_developments = story_progression.get(
            'character_developments', 
            {}
        )
        
        if character.name in character_developments:
            development = character_developments[character.name]
            
            # Potentially update personality traits
            for trait_name, trait_change in development.items():
                existing_trait = character.get_trait(trait_name)
                if existing_trait:
                    character.add_or_update_trait(
                        PersonalityTrait(
                            name=trait_name,
                            category=existing_trait.category,
                            value=trait_change.get('value', existing_trait.value),
                            description=trait_change.get(
                                'description', 
                                existing_trait.description
                            )
                        ),
                        reason='Story progression'
                    )

# Example Usage
async def create_and_integrate_character():
    """
    Demonstrate character creation and story integration
    """
    # Initialize dependencies
    ai_model = OllamaModelPlugin()
    memory_manager = BaseMemoryManager()
    generation_pipeline = BaseGenerationPipeline(
        ai_model_plugin=ai_model,
        memory_manager=memory_manager
    )
    
    # Create autonomous character generation system
    character_system = AutonomousCharacterGenerationSystem(
        ai_model_plugin=ai_model,
        memory_manager=memory_manager,
        generation_pipeline=generation_pipeline
    )
    
    # Initial story context
    story_context = {
        'genre': 'fantasy',
        'setting': 'medieval kingdom',
        'initial_conflict': 'Impending invasion'
    }
    
    # Create character
    character = await character_system.create_character_with_background(
        name='Elena the Strategist',
        story_context=story_context
    )
    
    # Integrate character with story
    story_integration = await character_system.integrate_character_with_story(
        character=character,
        story_context=story_context
    )
    
    return story_integration
```

## Key Features

1. **Dynamic Character Generation**
   - AI-powered background creation
   - Trait generation based on background
   - Contextual personality modeling

2. **Story Integration**
   - Seamless character insertion into narrative
   - Adaptive story progression
   - Memory-driven character development

3. **Autonomous Behavior**
   - Context-aware action generation
   - Trait-based decision making
   - Continuous character evolution

## Benefits

- **Flexibility**: Easily create diverse characters
- **Intelligence**: Context-driven character generation
- **Depth**: Complex personality modeling
- **Adaptability**: Characters grow with the story

## Recommended Next Steps

1. Implement more advanced trait interaction logic
2. Develop machine learning-based trait prediction
3. Create more sophisticated memory integration
4. Enhance story progression algorithms