import json
import logging
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import schemas as db_models
from app.utils.character_autonomy import CharacterAutonomySystem
from app.utils.memory_manager import MemoryManager
from app.utils.ollama_client import OllamaClient
from app.utils.prompt_templates import PromptTemplateManager


class GenerationPipeline:
    """
    Manages the end-to-end generation of narrative content
    Coordinates between prompt templates, Ollama, and character autonomy
    """

    def __init__(
        self,
        session: AsyncSession,
        ollama_client: OllamaClient,
        template_manager: Optional[PromptTemplateManager] = None,
    ):
        """
        Initialize the generation pipeline

        Args:
            session (AsyncSession): Database session
            ollama_client (OllamaClient): Ollama AI client
            template_manager (PromptTemplateManager, optional): Prompt template manager
        """
        self.session = session
        self.ollama_client = ollama_client
        self.template_manager = template_manager or PromptTemplateManager()
        self.character_autonomy = CharacterAutonomySystem(session, ollama_client)
        self.memory_manager = MemoryManager(session)
        self.logger = logging.getLogger(__name__)

    async def generate_dialogue(
        self,
        character: db_models.Character,
        context: Dict,
        recent_dialogue: Optional[List[str]] = None,
    ) -> Dict:
        """
        Generate dialogue for a specific character

        Args:
            character (db_models.Character): Character generating dialogue
            context (Dict): Current story context
            recent_dialogue (List[str], optional): Recent dialogue history

        Returns:
            Dict: Generated dialogue with metadata
        """
        try:
            # Retrieve character personality
            personality = character.personality or {}

            # Generate dialogue prompt
            dialogue_prompt = self.template_manager.get_template(
                "dialogue",
                character_name=character.name,
                character_personality=personality,
                context=context,
                recent_dialogue=recent_dialogue,
            )

            # Generate dialogue using Ollama
            dialogue_response = await self.ollama_client.generate_text(
                prompt=dialogue_prompt, model="dialogue-generation-model"
            )

            # Parse dialogue response
            try:
                parsed_dialogue = json.loads(dialogue_response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                parsed_dialogue = {
                    "dialogue": dialogue_response,
                    "emotional_tone": "neutral",
                    "subtext": "Unable to parse detailed dialogue",
                }

            # Create memory of the dialogue
            await self.memory_manager.create_memory(
                character_id=character.id,
                content=json.dumps(parsed_dialogue),
                importance=0.6,  # Moderate importance for dialogue
                context={
                    "type": "dialogue",
                    "emotional_tone": parsed_dialogue.get("emotional_tone", "neutral"),
                },
            )

            return parsed_dialogue

        except Exception as e:
            self.logger.error(f"Dialogue generation error: {e}")
            return {
                "dialogue": f"I'm feeling uncertain about what to say. {str(e)}",
                "emotional_tone": "confused",
                "subtext": "Generation error occurred",
            }

    async def generate_story_progression(
        self,
        current_story: db_models.Story,
        characters: List[db_models.Character],
        narrative_goals: List[str],
    ) -> Dict:
        """
        Generate progression for an ongoing story

        Args:
            current_story (db_models.Story): Current story state
            characters (List[db_models.Character]): Characters in the story
            narrative_goals (List[str]): Desired narrative directions

        Returns:
            Dict: Story progression details
        """
        try:
            # Prepare character data for prompt
            character_data = [
                {
                    "name": character.name,
                    "personality": character.personality or {},
                    "description": character.description,
                }
                for character in characters
            ]

            # Generate story progression prompt
            progression_prompt = self.template_manager.get_template(
                "story_progression",
                current_state=current_story.current_state or {},
                characters=character_data,
                narrative_goals=narrative_goals,
            )

            # Generate story progression using Ollama
            progression_response = await self.ollama_client.generate_text(
                prompt=progression_prompt, model="story-progression-model"
            )

            # Parse progression response
            try:
                parsed_progression = json.loads(progression_response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                parsed_progression = {
                    "new_story_state": current_story.current_state,
                    "key_events": ["Unable to generate progression"],
                    "character_developments": {},
                }

            # Update story state
            current_story.current_state = parsed_progression.get(
                "new_story_state", current_story.current_state
            )

            await self.session.commit()

            return parsed_progression

        except Exception as e:
            self.logger.error(f"Story progression generation error: {e}")
            return {
                "new_story_state": current_story.current_state,
                "key_events": [f"Generation error: {str(e)}"],
                "character_developments": {},
            }

    async def generate_character_interaction(
        self,
        initiating_character: db_models.Character,
        target_character: db_models.Character,
        interaction_context: Dict,
    ) -> Dict:
        """
        Generate an interaction between two characters

        Args:
            initiating_character (db_models.Character): Character starting the interaction
            target_character (db_models.Character): Character being interacted with
            interaction_context (Dict): Context of the interaction

        Returns:
            Dict: Character interaction details
        """
        try:
            # Prepare character data
            initiator_data = {
                "name": initiating_character.name,
                "personality": initiating_character.personality or {},
                "description": initiating_character.description,
            }

            target_data = {
                "name": target_character.name,
                "personality": target_character.personality or {},
                "description": target_character.description,
            }

            # Generate character interaction prompt
            interaction_prompt = self.template_manager.get_template(
                "character_interaction",
                initiating_character=initiator_data,
                target_character=target_data,
                interaction_context=interaction_context,
            )

            # Generate interaction using Ollama
            interaction_response = await self.ollama_client.generate_text(
                prompt=interaction_prompt, model="character-interaction-model"
            )

            # Parse interaction response
            try:
                parsed_interaction = json.loads(interaction_response)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                parsed_interaction = {
                    "dialogue": {
                        initiating_character.name: "...",
                        target_character.name: "...",
                    },
                    "interaction_type": "neutral",
                    "underlying_dynamics": "Unable to generate interaction",
                }

            # Create memories for both characters
            for character_name, dialogue in parsed_interaction["dialogue"].items():
                character = (
                    initiating_character
                    if character_name == initiating_character.name
                    else target_character
                )

                await self.memory_manager.create_memory(
                    character_id=character.id,
                    content=json.dumps(
                        {
                            "dialogue": dialogue,
                            "interaction_type": parsed_interaction["interaction_type"],
                        }
                    ),
                    importance=0.7,  # High importance for interactions
                    context={
                        "type": "character_interaction",
                        "interaction_type": parsed_interaction["interaction_type"],
                    },
                )

            return parsed_interaction

        except Exception as e:
            self.logger.error(f"Character interaction generation error: {e}")
            return {
                "dialogue": {
                    initiating_character.name: "I'm not sure what to say.",
                    target_character.name: "...",
                },
                "interaction_type": "error",
                "underlying_dynamics": str(e),
            }
