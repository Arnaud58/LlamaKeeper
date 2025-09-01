import json
from typing import Dict, List, Optional


class PromptTemplateManager:
    """
    Manages prompt templates for different storytelling scenarios
    Provides structured templates for character interactions, story generation,
    and narrative progression
    """

    def __init__(self):
        self.templates = {
            "dialogue": self._dialogue_template,
            "action": self._action_template,
            "internal_thought": self._internal_thought_template,
            "story_progression": self._story_progression_template,
            "character_interaction": self._character_interaction_template,
        }

    def get_template(self, template_type: str, **kwargs) -> str:
        """
        Retrieve a specific prompt template

        Args:
            template_type (str): Type of template to retrieve
            **kwargs: Context-specific parameters for template generation

        Returns:
            str: Formatted prompt template
        """
        if template_type not in self.templates:
            raise ValueError(f"Template type '{template_type}' not found")

        return self.templates[template_type](**kwargs)

    def _dialogue_template(
        self,
        character_name: str,
        character_personality: Dict,
        context: Dict,
        recent_dialogue: List[str] = None,
    ) -> str:
        """
        Generate a dialogue prompt template

        Args:
            character_name (str): Name of the speaking character
            character_personality (Dict): Character's personality traits
            context (Dict): Current story context
            recent_dialogue (List[str], optional): Recent dialogue history

        Returns:
            str: Dialogue generation prompt
        """
        personality_str = ", ".join(
            f"{k}: {v}" for k, v in character_personality.items()
        )

        recent_dialogue_str = "\n".join(recent_dialogue or [])

        return f"""
        You are {character_name}, a character with the following personality traits:
        {personality_str}
        
        Current Story Context:
        {json.dumps(context, indent=2)}
        
        Recent Dialogue History:
        {recent_dialogue_str}
        
        Generate a dialogue response that:
        1. Reflects {character_name}'s personality
        2. Is contextually appropriate
        3. Advances the story
        4. Shows emotional depth
        
        Provide the response in this JSON format:
        {{
            "dialogue": "Spoken text",
            "emotional_tone": "excited/sad/neutral/angry",
            "subtext": "Underlying meaning or motivation"
        }}
        """

    def _action_template(
        self,
        character_name: str,
        character_traits: Dict,
        story_context: Dict,
        recent_actions: List[Dict] = None,
    ) -> str:
        """
        Generate an action generation prompt template

        Args:
            character_name (str): Name of the character
            character_traits (Dict): Character's traits and background
            story_context (Dict): Current story context
            recent_actions (List[Dict], optional): Recent character actions

        Returns:
            str: Action generation prompt
        """
        traits_str = ", ".join(f"{k}: {v}" for k, v in character_traits.items())

        recent_actions_str = json.dumps(recent_actions or [], indent=2)

        return f"""
        Character Profile for {character_name}:
        Traits: {traits_str}
        
        Current Story Context:
        {json.dumps(story_context, indent=2)}
        
        Recent Actions:
        {recent_actions_str}
        
        Generate a nuanced character action that:
        1. Aligns with {character_name}'s personality
        2. Responds to the current story context
        3. Shows character depth and motivation
        4. Potentially creates narrative tension
        
        Provide the response in this JSON format:
        {{
            "action_type": "physical/verbal/internal",
            "description": "Detailed action description",
            "motivation": "Underlying reason for the action",
            "potential_consequences": "Possible story implications"
        }}
        """

    def _internal_thought_template(
        self, character_name: str, emotional_state: str, context: Dict
    ) -> str:
        """
        Generate an internal thought prompt template

        Args:
            character_name (str): Name of the character
            emotional_state (str): Current emotional state
            context (Dict): Current story context

        Returns:
            str: Internal thought generation prompt
        """
        return f"""
        Character: {character_name}
        Current Emotional State: {emotional_state}
        
        Story Context:
        {json.dumps(context, indent=2)}
        
        Generate an introspective internal monologue that:
        1. Reveals {character_name}'s inner emotional landscape
        2. Provides insight into their current mental state
        3. Connects to the broader narrative
        4. Shows psychological complexity
        
        Provide the response in this JSON format:
        {{
            "thought": "Internal monologue text",
            "emotional_depth": "Description of underlying emotions",
            "hidden_motivation": "Unspoken desire or fear"
        }}
        """

    def _story_progression_template(
        self, current_state: Dict, characters: List[Dict], narrative_goals: List[str]
    ) -> str:
        """
        Generate a story progression prompt template

        Args:
            current_state (Dict): Current story state
            characters (List[Dict]): List of characters and their key traits
            narrative_goals (List[str]): Desired narrative directions

        Returns:
            str: Story progression generation prompt
        """
        characters_str = "\n".join(
            [
                f"{char['name']}: {', '.join(f'{k}: {v}' for k, v in char.items() if k != 'name')}"
                for char in characters
            ]
        )

        narrative_goals_str = "\n".join(narrative_goals)

        return f"""
        Current Story State:
        {json.dumps(current_state, indent=2)}
        
        Characters:
        {characters_str}
        
        Narrative Goals:
        {narrative_goals_str}
        
        Generate a story progression that:
        1. Advances the narrative logically
        2. Creates interesting character interactions
        3. Introduces unexpected but believable developments
        4. Moves towards the specified narrative goals
        
        Provide the response in this JSON format:
        {{
            "new_story_state": "Updated story context",
            "key_events": ["List of significant events"],
            "character_developments": {{
                "character_name": "Character arc progression"
            }}
        }}
        """

    def _character_interaction_template(
        self,
        initiating_character: Dict,
        target_character: Dict,
        interaction_context: Dict,
    ) -> str:
        """
        Generate a character interaction prompt template

        Args:
            initiating_character (Dict): Character initiating the interaction
            target_character (Dict): Character being interacted with
            interaction_context (Dict): Context of the interaction

        Returns:
            str: Character interaction generation prompt
        """
        return f"""
        Interaction Dynamics:
        Initiating Character: {initiating_character['name']}
        - Traits: {', '.join(f'{k}: {v}' for k, v in initiating_character.items() if k != 'name')}
        
        Target Character: {target_character['name']}
        - Traits: {', '.join(f'{k}: {v}' for k, v in target_character.items() if k != 'name')}
        
        Interaction Context:
        {json.dumps(interaction_context, indent=2)}
        
        Generate a character interaction that:
        1. Reveals character personalities
        2. Creates narrative tension
        3. Shows potential for future story development
        4. Feels authentic and nuanced
        
        Provide the response in this JSON format:
        {{
            "dialogue": {{
                "{initiating_character['name']}": "Dialogue text",
                "{target_character['name']}": "Response dialogue"
            }},
            "interaction_type": "confrontational/supportive/neutral",
            "underlying_dynamics": "Subtext and relationship progression"
        }}
        """
