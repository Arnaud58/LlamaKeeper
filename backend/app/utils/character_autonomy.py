import json
from typing import Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import schemas as db_models
from app.utils.memory_manager import MemoryManager
from app.utils.ollama_client import OllamaClient


class CharacterAutonomySystem:
    def __init__(self, session: AsyncSession, ollama_client: OllamaClient):
        self.session = session
        self.ollama_client = ollama_client
        self.memory_manager = MemoryManager(session)

    async def generate_action(
        self, character_id: str, story_context: Dict, recent_actions: List[Dict]
    ) -> Dict:
        """
        Generate an autonomous action for a character

        Args:
            character_id (str): ID of the character
            story_context (Dict): Current story state and context
            recent_actions (List[Dict]): Recent actions in the story

        Returns:
            Dict: Generated character action
        """
        # Retrieve character details
        character = await self._get_character(character_id)

        # Retrieve relevant memories
        relevant_memories = await self.memory_manager.retrieve_relevant_memories(
            character_id, story_context
        )

        # Prepare prompt for action generation
        prompt = self._construct_action_prompt(
            character, story_context, recent_actions, relevant_memories
        )

        # Generate action using Ollama
        action_response = await self.ollama_client.generate_text(
            model="character-action-model", prompt=prompt
        )

        # Parse and validate action
        parsed_action = self._parse_action(action_response, character)

        # Create and store memory of the action
        await self._create_action_memory(character, parsed_action)

        return parsed_action

    async def _get_character(self, character_id: str) -> db_models.Character:
        """Retrieve character details from database"""
        result = await self.session.execute(
            select(db_models.Character).where(db_models.Character.id == character_id)
        )
        character = result.scalar_one_or_none()

        if not character:
            raise ValueError(f"Character with ID {character_id} not found")

        return character

    def _construct_action_prompt(
        self,
        character: db_models.Character,
        story_context: Dict,
        recent_actions: List[Dict],
        relevant_memories: List[Dict],
    ) -> str:
        """
        Construct a detailed prompt for action generation

        Includes:
        - Character personality and background
        - Current story context
        - Recent story actions
        - Relevant memories
        """
        prompt_template = """
        Character Profile:
        Name: {name}
        Personality: {personality}
        Background: {description}

        Current Story Context:
        {story_context}

        Recent Story Actions:
        {recent_actions}

        Relevant Memories:
        {relevant_memories}

        Based on the above context, generate a thoughtful and contextually appropriate action 
        for the character. The action should reflect the character's personality, 
        current situation, and past experiences. Provide the action in JSON format with 
        the following structure:
        {{
            "action_type": "dialogue/movement/internal_thought/interaction",
            "content": "Detailed description of the action",
            "emotional_state": "character's emotional response",
            "motivation": "underlying reason for the action"
        }}
        """

        return prompt_template.format(
            name=character.name,
            personality=json.dumps(character.personality),
            description=character.description or "No background available",
            story_context=json.dumps(story_context),
            recent_actions=json.dumps(recent_actions),
            relevant_memories=json.dumps(relevant_memories),
        )

    def _parse_action(
        self, action_response: str, character: db_models.Character
    ) -> Dict:
        """
        Parse and validate the generated action

        Ensures the action meets basic structural and semantic requirements
        """
        try:
            parsed_action = json.loads(action_response)

            # Validate action structure
            required_keys = ["action_type", "content", "emotional_state", "motivation"]
            for key in required_keys:
                if key not in parsed_action:
                    raise ValueError(f"Missing required key: {key}")

            # Additional validation
            valid_action_types = [
                "dialogue",
                "movement",
                "internal_thought",
                "interaction",
            ]
            if parsed_action["action_type"] not in valid_action_types:
                raise ValueError(f"Invalid action type: {parsed_action['action_type']}")

            # Add character ID to the action
            parsed_action["character_id"] = character.id

            return parsed_action

        except (json.JSONDecodeError, ValueError) as e:
            # Fallback to a default action if parsing fails
            return {
                "action_type": "internal_thought",
                "content": f"I'm unsure what to do next. {str(e)}",
                "emotional_state": "confused",
                "motivation": "processing complex situation",
                "character_id": character.id,
            }

    async def _create_action_memory(self, character: db_models.Character, action: Dict):
        """
        Create a memory from the generated action

        Stores the action as a memory with importance based on its emotional intensity
        """
        # Calculate memory importance based on emotional state
        emotion_importance_map = {
            "excited": 0.8,
            "happy": 0.7,
            "neutral": 0.5,
            "sad": 0.6,
            "angry": 0.7,
            "fearful": 0.7,
            "confused": 0.6,
        }

        importance = emotion_importance_map.get(
            action.get("emotional_state", "neutral"), 0.5
        )

        memory = db_models.Memory(
            character_id=character.id,
            content=json.dumps(action),
            importance=importance,
            context={
                "action_type": action["action_type"],
                "emotional_state": action["emotional_state"],
            },
        )

        self.session.add(memory)
        await self.session.commit()
