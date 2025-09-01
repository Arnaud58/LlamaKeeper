# Ollama Model Plugin Example

## Sample Llama2 Model Plugin Implementation

```python
from typing import Dict, Any, Optional
from app.core.plugin_system import OllamaModelPlugin, ModelGenerationContext

class Llama2ModelPlugin(OllamaModelPlugin):
    """
    Specialized Ollama plugin for Llama2 model
    Demonstrates advanced model-specific configuration and generation
    """
    
    def __init__(self):
        """
        Initialize Llama2 model plugin with specific metadata
        """
        self._model_details = {
            "name": "llama2:7b",
            "version": "7b",
            "capabilities": {
                "text_generation": True,
                "instruction_following": True,
                "multilingual": False
            },
            "recommended_use_cases": [
                "storytelling",
                "creative writing",
                "general conversation"
            ]
        }
    
    async def generate_text(
        self, 
        prompt: str, 
        context: Optional[ModelGenerationContext] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text using Llama2 model with advanced configuration
        
        Args:
            prompt (str): Input prompt for text generation
            context (ModelGenerationContext, optional): Generation context
            parameters (Dict, optional): Model-specific generation parameters
        
        Returns:
            str: Generated text response
        """
        # Merge default and user-provided parameters
        default_params = {
            "temperature": 0.7,
            "top_p": 0.9,
            "max_tokens": 500,
            "stop_sequences": ["\n\n"]
        }
        generation_params = {**default_params, **(parameters or {})}
        
        # Prepare enhanced prompt with context
        enhanced_prompt = self._prepare_prompt(prompt, context)
        
        try:
            # Use Ollama client to generate text
            response = await self._ollama_client.generate_text(
                prompt=enhanced_prompt,
                model=self._model_details['name'],
                **generation_params
            )
            
            # Post-process generated text
            processed_response = self._post_process_response(response)
            
            return processed_response
        
        except Exception as e:
            # Advanced error handling
            self._log_generation_error(e, prompt, context)
            return self._generate_fallback_response(prompt)
    
    def get_ollama_model_details(self) -> Dict[str, Any]:
        """
        Retrieve detailed Llama2 model specifications
        
        Returns:
            Dict: Comprehensive model details
        """
        return self._model_details
    
    def validate_ollama_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate Llama2-specific model configuration
        
        Args:
            config (Dict): Model configuration to validate
        
        Returns:
            bool: Configuration validity
        """
        # Implement Llama2-specific configuration validation
        valid_keys = {
            "temperature": (float, 0.0, 1.0),
            "top_p": (float, 0.0, 1.0),
            "max_tokens": (int, 1, 2048)
        }
        
        for key, (type_, min_val, max_val) in valid_keys.items():
            if key in config:
                value = config[key]
                if not isinstance(value, type_):
                    return False
                if not (min_val <= value <= max_val):
                    return False
        
        return True
    
    def _prepare_prompt(
        self, 
        prompt: str, 
        context: Optional[ModelGenerationContext] = None
    ) -> str:
        """
        Enhance prompt with additional context and instructions
        
        Args:
            prompt (str): Original input prompt
            context (ModelGenerationContext, optional): Generation context
        
        Returns:
            str: Enhanced prompt
        """
        # Add Llama2-specific prompt engineering
        system_prompt = (
            "You are an advanced AI assistant. "
            "Provide creative, coherent, and contextually appropriate responses. "
        )
        
        if context and context.get('character_personality'):
            personality = context['character_personality']
            system_prompt += (
                f"Adopt the personality of a character with these traits: {personality}. "
            )
        
        return f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
    
    def _post_process_response(self, response: str) -> str:
        """
        Post-process generated text to improve quality
        
        Args:
            response (str): Raw generated text
        
        Returns:
            str: Cleaned and refined text
        """
        # Remove excessive whitespace
        cleaned_response = ' '.join(response.split())
        
        # Truncate to reasonable length
        max_length = 1000
        return cleaned_response[:max_length]
    
    def _log_generation_error(
        self, 
        error: Exception, 
        prompt: str, 
        context: Optional[ModelGenerationContext]
    ):
        """
        Log detailed error information for generation failures
        
        Args:
            error (Exception): Generation error
            prompt (str): Original input prompt
            context (ModelGenerationContext, optional): Generation context
        """
        error_log = {
            "model": self._model_details['name'],
            "error_type": type(error).__name__,
            "error_message": str(error),
            "prompt": prompt,
            "context": context
        }
        # Use a centralized logging system
        logging.error(f"Llama2 Model Generation Error: {error_log}")
    
    def _generate_fallback_response(self, prompt: str) -> str:
        """
        Generate a fallback response in case of generation failure
        
        Args:
            prompt (str): Original input prompt
        
        Returns:
            str: Fallback response
        """
        return (
            "I apologize, but I'm currently unable to generate a response. "
            "Please try again or rephrase your request."
        )
```

## Key Features of the Plugin

1. **Model-Specific Configuration**
   - Detailed model metadata
   - Custom configuration validation
   - Flexible parameter handling

2. **Advanced Prompt Engineering**
   - Context-aware prompt preparation
   - Character personality integration
   - System instruction injection

3. **Robust Error Handling**
   - Comprehensive error logging
   - Fallback response generation
   - Graceful error management

4. **Post-Processing**
   - Response cleaning
   - Length management
   - Quality improvement

## Usage Example

```python
# Plugin discovery and loading
model_manager = OllamaModelManager()
llama2_plugin = await model_manager.load_model("llama2:7b")

# Generation with context
context = {
    "character_personality": {
        "traits": ["brave", "curious", "compassionate"],
        "background": "A young adventurer exploring magical lands"
    }
}

response = await llama2_plugin.generate_text(
    prompt="Describe your most exciting adventure",
    context=context,
    parameters={"temperature": 0.8}
)
```

## Benefits

- **Modularity**: Easy to add or replace AI models
- **Flexibility**: Customizable generation parameters
- **Extensibility**: Support for advanced prompt engineering
- **Reliability**: Robust error handling and fallback mechanisms