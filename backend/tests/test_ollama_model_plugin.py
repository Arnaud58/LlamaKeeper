import pytest
from app.plugins.ai_models.ollama_model_plugin import OllamaModelPlugin

class TestOllamaModelPlugin:
    def test_default_configuration(self):
        """
        Test default configuration of OllamaModelPlugin
        """
        plugin = OllamaModelPlugin()
        
        # Vérifier les valeurs par défaut
        assert plugin._config['base_url'] == "http://localhost:11434/api"
        assert plugin._config['timeout'] == 60.0
        assert plugin._config['max_tokens'] == 500
        assert plugin._config['temperature'] == 0.7
        assert plugin._config['top_p'] == 0.9
    
    def test_configuration_validation(self):
        """
        Test configuration validation method
        """
        plugin = OllamaModelPlugin()
        
        # Configuration valide
        valid_config = {
            "temperature": 0.5,
            "top_p": 0.8,
            "max_tokens": 300
        }
        assert plugin.validate_configuration(valid_config) is True
        
        # Configurations invalides
        invalid_configs = [
            {"temperature": -0.1},  # Température < 0
            {"temperature": 1.1},   # Température > 1
            {"top_p": -0.1},        # Top_p < 0
            {"top_p": 1.1},         # Top_p > 1
            {"max_tokens": 0},      # Max tokens <= 0
            {"max_tokens": -10}     # Max tokens négatif
        ]
        
        for invalid_config in invalid_configs:
            assert plugin.validate_configuration(invalid_config) is False
    
    def test_model_metadata(self):
        """
        Test model metadata retrieval
        """
        plugin = OllamaModelPlugin("custom_model")
        metadata = plugin.get_model_metadata()
        
        assert metadata['model_name'] == "custom_model"
        assert metadata['provider'] == "Ollama"
        assert 'base_url' in metadata
        assert 'max_tokens' in metadata
        assert 'generation_params' in metadata
    
    @pytest.mark.asyncio
    async def test_text_generation(self):
        """
        Test basic text generation
        Requires Ollama service to be running
        """
        plugin = OllamaModelPlugin()
        prompt = "Write a short story about a brave robot."
        
        # Test generation with default parameters
        response = await plugin.generate_text(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_text_generation_with_custom_params(self):
        """
        Test text generation with custom parameters
        Requires Ollama service to be running
        """
        plugin = OllamaModelPlugin()
        prompt = "Explain quantum computing in simple terms."
        
        custom_params = {
            "max_tokens": 200,
            "temperature": 0.5,
            "top_p": 0.8
        }
        
        response = await plugin.generate_text(
            prompt, 
            parameters=custom_params
        )
        
        assert isinstance(response, str)
        assert len(response) > 0