import pytest
import uuid
from typing import Dict, Any, List
import json

from app.utils.ai_model_plugin import BaseAIModelPlugin
from app.utils.character_model import BaseCharacterModel
from app.utils.base_memory_manager import BaseMemoryManager
from app.utils.base_generation_pipeline import BaseGenerationPipeline

class TestAbstractBaseClasses:
    """
    Comprehensive test suite for abstract base classes
    Validates core contract requirements and expected behaviors
    """
    
    # AI Model Plugin Tests
    def test_base_ai_model_plugin_initialization(self):
        """
        Test AI model plugin initialization and basic metadata retrieval
        """
        class TestAIModelPlugin(BaseAIModelPlugin):
            async def generate_text(self, prompt: str, context: Dict[str, Any] = None, parameters: Dict[str, Any] = None) -> str:
                return "Test generation"
        
        plugin = TestAIModelPlugin("test_model", {"temperature": 0.7})
        
        assert plugin._model_name == "test_model"
        assert plugin._config == {"temperature": 0.7}
        
        metadata = plugin.get_model_metadata()
        assert metadata["model_name"] == "test_model"
        assert metadata["config"] == {"temperature": 0.7}
    
    @pytest.mark.asyncio
    async def test_base_ai_model_plugin_generate_text(self):
        """
        Test generate_text method contract
        """
        class TestAIModelPlugin(BaseAIModelPlugin):
            async def generate_text(self, prompt: str, context: Dict[str, Any] = None, parameters: Dict[str, Any] = None) -> str:
                return f"Generated: {prompt}"
        
        plugin = TestAIModelPlugin("test_model")
        result = await plugin.generate_text("Test prompt")
        assert result.startswith("Generated: Test prompt")
    
    # Character Model Tests
    def test_base_character_model_initialization(self):
        """
        Test character model initialization and personality trait management
        """
        class TestCharacterModel(BaseCharacterModel):
            def generate_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"action": "test_action"}
        
        character = TestCharacterModel(
            name="TestCharacter", 
            personality={"trait1": "value1", "trait2": "value2"}
        )
        
        assert character._name == "TestCharacter"
        assert character._personality == {"trait1": "value1", "trait2": "value2"}
    
    def test_base_character_model_update_personality(self):
        """
        Test updating character personality traits
        """
        class TestCharacterModel(BaseCharacterModel):
            def generate_action(self, context: Dict[str, Any]) -> Dict[str, Any]:
                return {"action": "test_action"}
        
        character = TestCharacterModel(
            name="TestCharacter", 
            personality={"trait1": "value1"}
        )
        
        character.update_personality_trait("trait2", "new_value")
        assert character._personality["trait2"] == "new_value"
    
    # Memory Manager Tests
    @pytest.mark.asyncio
    async def test_base_memory_manager_store_and_retrieve(self):
        """
        Test memory storage and retrieval contract
        """
        class TestMemoryManager(BaseMemoryManager):
            async def store_memory(
                self, 
                character_id: uuid.UUID, 
                memory_content: str, 
                context: Dict[str, Any] = None,
                importance: float = 0.5
            ) -> uuid.UUID:
                return uuid.uuid4()
            
            async def retrieve_relevant_memories(
                self, 
                character_id: uuid.UUID, 
                context: Dict[str, Any],
                top_k: int = 5
            ) -> List[Dict[str, Any]]:
                return []
            
            async def forget_memories(
                self, 
                character_id: uuid.UUID, 
                forget_threshold: float = 0.2,
                max_memories: int = 100
            ) -> None:
                pass
        
        memory_manager = TestMemoryManager()
        char_id = uuid.uuid4()
        
        memory_id = await memory_manager.store_memory(
            char_id, 
            "Test memory content", 
            {"context": "test"}
        )
        assert isinstance(memory_id, uuid.UUID)
    
    # Generation Pipeline Tests
    @pytest.mark.asyncio
    async def test_base_generation_pipeline_methods(self):
        """
        Test generation pipeline core methods
        """
        class TestGenerationPipeline(BaseGenerationPipeline):
            async def generate_story_progression(
                self, 
                current_story: Dict[str, Any],
                characters: List[Dict[str, Any]],
                narrative_goals: List[str]
            ) -> Dict[str, Any]:
                return {"progression": "test"}
            
            async def generate_character_interaction(
                self, 
                initiating_character: Dict[str, Any],
                target_character: Dict[str, Any],
                interaction_context: Dict[str, Any]
            ) -> Dict[str, Any]:
                return {"interaction": "test"}
        
        pipeline = TestGenerationPipeline()
        
        story_progression = await pipeline.generate_story_progression(
            {"current_state": "initial"}, 
            [{"name": "Character1"}], 
            ["goal1"]
        )
        assert story_progression == {"progression": "test"}
        
        character_interaction = await pipeline.generate_character_interaction(
            {"name": "Character1"}, 
            {"name": "Character2"}, 
            {"context": "interaction"}
        )
        assert character_interaction == {"interaction": "test"}