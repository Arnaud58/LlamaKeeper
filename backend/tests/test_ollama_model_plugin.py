import pytest
from unittest.mock import AsyncMock, patch
from app.plugins.ai_models.ollama_model_plugin import OllamaModelPlugin
import httpx

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
        plugin = OllamaModelPlugin(model_name="custom_model")
        metadata = plugin.get_model_metadata()
        
        assert metadata['model_name'] == "custom_model"
        assert metadata['provider'] == "Ollama"
        assert 'base_url' in metadata
        assert 'max_tokens' in metadata
        assert 'generation_params' in metadata
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_text_generation(self, mock_post):
        """
        Test basic text generation with mocked HTTP response
        """
        # Configurer la réponse mock
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.text = "A short story about a brave robot."
        mock_post.return_value = mock_response

        plugin = OllamaModelPlugin()
        prompt = "Write a short story about a brave robot."
        
        # Test generation with default parameters
        response = await plugin.generate_text(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Vérifier que la requête a été faite avec les bons paramètres
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['json']['model'] == 'llama2'
        assert call_args['json']['prompt'] == prompt
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_text_generation_with_custom_params(self, mock_post):
        """
        Test text generation with custom parameters
        """
        # Configurer la réponse mock
        mock_response = AsyncMock()
        mock_response.raise_for_status = AsyncMock()
        mock_response.text = "An explanation of quantum computing in simple terms."
        mock_post.return_value = mock_response

        plugin = OllamaModelPlugin()
        prompt = "Explain quantum computing in simple terms."
        
        custom_config = {
            "max_tokens": 200,
            "temperature": 0.5,
            "top_p": 0.8
        }
        
        response = await plugin.generate_text(
            prompt, 
            config=custom_config
        )
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Vérifier que la requête a été faite avec les paramètres personnalisés
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['json']['max_tokens'] == 200
        assert call_args['json']['temperature'] == 0.5
        assert call_args['json']['top_p'] == 0.8