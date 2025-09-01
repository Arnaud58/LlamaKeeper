# Base Generation Pipeline Implementation

## Overview
A concrete implementation of the AbstractGenerationPipeline that demonstrates the core narrative generation capabilities of LlamaKeeper.

## Implementation

```python
from typing import Dict, List, Any, Optional
from uuid import UUID
import json
import logging

from app.core.abstract_base_classes import AbstractGenerationPipeline
from app.core.abstract_base_classes import AbstractCharacterModel
from app.core.abstract_base_classes import AbstractAIModelPlugin
from app.core.abstract_base_classes import AbstractMemoryManager

class BaseGenerationPipeline(AbstractGenerationPipeline):
    """
    Base implementation of the generation pipeline
    Coordinates AI models, characters, and memory systems
    """
    
    def __init__(
        self, 
        ai_model_plugin: AbstractAIModelPlugin,
        memory_manager: AbstractMemoryManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the generation pipeline
        
        Args:
            ai_model_plugin (AbstractAIModelPlugin): AI model for text generation
            memory_manager (AbstractMemoryManager): Memory management system
            logger (Logger, optional): Logging instance
        """
        self._ai_model = ai_model_plugin
        self._memory_manager = memory_manager
        self._logger = logger or logging.getLogger(__name__)
    
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
        try:
            # Prepare context for story progression
            context = self._prepare_story_context(
                current_story, 
                characters, 
                narrative_goals
            )
            
            # Generate story progression prompt
            progression_prompt = self._construct_progression_prompt(context)
            
            # Generate text using AI model
            progression_text = await self._ai_model.generate_text(
                prompt=progression_prompt,
                context=context
            )
            
            # Parse and validate progression
            parsed_progression = self._parse_story_progression(
                progression_text, 
                current_story
            )
            
            # Update character memories
            await self._update_character_memories(
                characters, 
                parsed_progression
            )
            
            return parsed_progression
        
        except Exception as e:
            self._logger.error(f"Story progression generation error: {e}")
            return self._generate_fallback_progression(current_story)
    
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
        try:
            # Retrieve relevant memories for both characters
            initiator_memories = await self._memory_manager.retrieve_relevant_memories(
                initiating_character.id, 
                interaction_context
            )
            target_memories = await self._memory_manager.retrieve_relevant_memories(
                target_character.id, 
                interaction_context
            )
            
            # Prepare interaction context
            context = {
                **interaction_context,
                'initiator_memories': initiator_memories,
                'target_memories': target_memories
            }
            
            # Generate interaction prompt
            interaction_prompt = self._construct_interaction_prompt(
                initiating_character, 
                target_character, 
                context
            )
            
            # Generate interaction text
            interaction_text = await self._ai_model.generate_text(
                prompt=interaction_prompt,
                context=context
            )
            
            # Parse interaction
            parsed_interaction = self._parse_character_interaction(
                interaction_text, 
                initiating_character, 
                target_character
            )
            
            # Store interaction memories
            await self._store_interaction_memories(
                initiating_character, 
                target_character, 
                parsed_interaction
            )
            
            return parsed_interaction
        
        except Exception as e:
            self._logger.error(f"Character interaction generation error: {e}")
            return self._generate_fallback_interaction(
                initiating_character, 
                target_character
            )
    
    def _prepare_story_context(
        self, 
        current_story: Dict[str, Any],
        characters: List[AbstractCharacterModel],
        narrative_goals: List[str]
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive context for story progression
        
        Args:
            current_story (Dict): Current story state
            characters (List[AbstractCharacterModel]): Story characters
            narrative_goals (List[str]): Desired narrative directions
        
        Returns:
            Dict: Prepared story context
        """
        return {
            'story_state': current_story,
            'characters': [
                {
                    'name': char.name,
                    'personality': char.get_personality(),
                    'recent_memories': char.get_recent_memories()
                } for char in characters
            ],
            'narrative_goals': narrative_goals
        }
    
    def _construct_progression_prompt(
        self, 
        context: Dict[str, Any]
    ) -> str:
        """
        Construct a detailed prompt for story progression
        
        Args:
            context (Dict): Story context
        
        Returns:
            str: Generated progression prompt
        """
        prompt_template = """
        Story Progression Context:
        Current State: {story_state}
        Characters: {characters}
        Narrative Goals: {narrative_goals}
        
        Generate the next progression of the story, 
        considering character personalities, 
        recent memories, and narrative objectives.
        Provide a JSON response with:
        - new_story_state
        - key_events
        - character_developments
        """
        
        return prompt_template.format(
            story_state=json.dumps(context['story_state']),
            characters=json.dumps(context['characters']),
            narrative_goals=json.dumps(context['narrative_goals'])
        )
    
    def _parse_story_progression(
        self, 
        progression_text: str, 
        current_story: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse and validate story progression
        
        Args:
            progression_text (str): Generated progression text
            current_story (Dict): Current story state
        
        Returns:
            Dict: Parsed and validated progression
        """
        try:
            parsed_progression = json.loads(progression_text)
            
            # Validate progression structure
            required_keys = [
                'new_story_state', 
                'key_events', 
                'character_developments'
            ]
            
            for key in required_keys:
                if key not in parsed_progression:
                    raise ValueError(f"Missing required key: {key}")
            
            return parsed_progression
        
        except (json.JSONDecodeError, ValueError) as e:
            self._logger.warning(f"Progression parsing error: {e}")
            return {
                'new_story_state': current_story,
                'key_events': ['Unable to generate progression'],
                'character_developments': {}
            }
    
    async def _update_character_memories(
        self, 
        characters: List[AbstractCharacterModel],
        progression: Dict[str, Any]
    ):
        """
        Update character memories based on story progression
        
        Args:
            characters (List[AbstractCharacterModel]): Story characters
            progression (Dict): Story progression details
        """
        for character in characters:
            if character.name in progression['character_developments']:
                development = progression['character_developments'][character.name]
                await self._memory_manager.store_memory(
                    character_id=character.id,
                    memory_content=json.dumps(development),
                    importance=0.7,
                    context={'type': 'character_development'}
                )
    
    def _generate_fallback_progression(
        self, 
        current_story: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a fallback story progression
        
        Args:
            current_story (Dict): Current story state
        
        Returns:
            Dict: Fallback progression
        """
        return {
            'new_story_state': current_story,
            'key_events': ['Narrative progression encountered an issue'],
            'character_developments': {}
        }
    
    # Additional helper methods for interaction generation would be implemented similarly
```

## Key Features

1. **Flexible AI Model Integration**
   - Uses AbstractAIModelPlugin for text generation
   - Supports different AI backends
   - Configurable generation parameters

2. **Memory-Aware Progression**
   - Retrieves relevant character memories
   - Updates memories based on story progression
   - Supports context-driven narrative development

3. **Robust Error Handling**
   - Comprehensive exception management
   - Fallback generation mechanisms
   - Detailed logging

4. **Structured Output**
   - JSON-based story progression
   - Validates generated content
   - Supports multiple narrative elements

## Usage Example

```python
# Initialize dependencies
ollama_plugin = OllamaModelPlugin()
memory_manager = BaseMemoryManager()

# Create generation pipeline
generation_pipeline = BaseGenerationPipeline(
    ai_model_plugin=ollama_plugin,
    memory_manager=memory_manager
)

# Generate story progression
current_story = {...}
characters = [character1, character2]
narrative_goals = ["Explore character conflicts", "Introduce plot twist"]

progression = await generation_pipeline.generate_story_progression(
    current_story, 
    characters, 
    narrative_goals
)
```

## Benefits

- **Modularity**: Easy to extend and customize
- **Flexibility**: Support for different AI models
- **Intelligence**: Memory-driven narrative generation
- **Robustness**: Comprehensive error handling