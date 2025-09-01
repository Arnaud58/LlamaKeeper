import pytest
import httpx
from app.utils.ollama_client import OllamaClient

class TestOllamaClient:
    def test_default_configuration(self):
        """
        Test default configuration of OllamaClient
        """
        client = OllamaClient()
        
        # Test default base URL
        assert client.base_url == "http://localhost:11434/api"
        
        # Test default timeout
        assert client.timeout == 60.0
        
        # Test default model
        assert client.default_model == "llama2"
        
        # Verify async client is created
        assert isinstance(client.client, httpx.AsyncClient)
    
    @pytest.mark.asyncio
    async def test_list_models(self):
        """
        Test listing available Ollama models
        Requires Ollama service to be running
        """
        client = OllamaClient()
        models = await client.list_models()
        
        # At least verify it returns a list
        assert isinstance(models, list)
    
    @pytest.mark.asyncio
    async def test_generate_text(self):
        """
        Test basic text generation
        Requires Ollama service to be running
        """
        client = OllamaClient()
        prompt = "Write a short story about a brave robot."
        
        # Test generation with default parameters
        response = await client.generate_text(prompt)
        
        assert isinstance(response, str)
        assert len(response) > 0
    
    @pytest.mark.asyncio
    async def test_generate_text_with_custom_params(self):
        """
        Test text generation with custom parameters
        Requires Ollama service to be running
        """
        client = OllamaClient()
        prompt = "Explain quantum computing in simple terms."
        
        response = await client.generate_text(
            prompt, 
            max_tokens=200, 
            temperature=0.5, 
            top_p=0.8
        )
        
        assert isinstance(response, str)
        assert len(response) > 0