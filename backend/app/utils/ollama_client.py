import asyncio
import json
from typing import Dict, List, Optional

import httpx


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434/api",
        timeout: float = 60.0,
        default_model: str = "llama2",
    ):
        """
        Initialize Ollama API client

        Args:
            base_url (str): Base URL for Ollama API
            timeout (float): Request timeout in seconds
            default_model (str): Default language model to use
        """
        self.base_url = base_url
        self.timeout = timeout
        self.default_model = default_model
        self.client = httpx.AsyncClient(timeout=self.timeout)

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ) -> str:
        """
        Generate text using Ollama API

        Args:
            prompt (str): Input prompt for text generation
            model (str, optional): Specific model to use
            max_tokens (int): Maximum number of tokens to generate
            temperature (float): Sampling temperature for randomness
            top_p (float): Nucleus sampling parameter

        Returns:
            str: Generated text response
        """
        endpoint = f"{self.base_url}/generate"

        payload = {
            "model": model or self.default_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            },
        }

        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()

            result = response.json()
            return result.get("response", "")

        except httpx.HTTPError as e:
            # Log error and provide fallback
            print(f"Ollama API Error: {e}")
            return f"Error generating text: {str(e)}"

    async def list_models(self) -> List[str]:
        """
        List available Ollama models

        Returns:
            List[str]: Available model names
        """
        endpoint = f"{self.base_url}/tags"

        try:
            response = await self.client.get(endpoint)
            response.raise_for_status()

            models = response.json().get("models", [])
            return [model["name"] for model in models]

        except httpx.HTTPError as e:
            print(f"Error listing Ollama models: {e}")
            return []

    async def pull_model(self, model_name: str) -> bool:
        """
        Pull a model from Ollama repository

        Args:
            model_name (str): Name of the model to pull

        Returns:
            bool: True if model pull was successful, False otherwise
        """
        endpoint = f"{self.base_url}/pull"

        payload = {"name": model_name}

        try:
            response = await self.client.post(endpoint, json=payload)
            response.raise_for_status()

            # Check pull status
            while True:
                status_response = await self.client.get(endpoint)
                status = status_response.json()

                if status.get("status") == "complete":
                    return True

                if status.get("error"):
                    print(f"Model pull error: {status['error']}")
                    return False

                await asyncio.sleep(1)

        except httpx.HTTPError as e:
            print(f"Error pulling Ollama model: {e}")
            return False

    async def close(self):
        """
        Close the HTTP client
        """
        await self.client.aclose()

    def __del__(self):
        """
        Ensure client is closed when object is deleted
        """
        asyncio.create_task(self.close())
