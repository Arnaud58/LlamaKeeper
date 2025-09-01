# Modular Architecture Implementation Example

## Abstract Base Classes and Plugin Interfaces

### 1. AbstractAIModelPlugin

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AbstractAIModelPlugin(ABC):
    """
    Abstract base class for AI model plugins
    Defines a standard interface for text generation across different AI backends
    """
    
    @abstractmethod
    async def generate_text(
        self, 
        prompt: str, 
        context: Dict[str, Any] = None,
        parameters: Dict[str, Any] = None
    ) -> str:
        """
        Generate text using the AI model
        
        Args:
            prompt (str): Input prompt for text generation
            context (Dict, optional): Contextual information for generation
            parameters (Dict, optional): Model-specific generation parameters
        
        Returns:
            str: Generated text
        """
        pass
    
    @abstractmethod
    def validate_model_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate the configuration for the AI model
        
        Args:
            config (Dict): Model configuration parameters
        
        Returns:
            bool: Whether the configuration is valid
        """
        pass
    
    @abstractmethod
    def get_model_metadata(self) -> Dict[str, Any]:
        """
        Retrieve metadata about the AI model
        
        Returns:
            Dict: Model metadata (version, capabilities, etc.)
        """
        pass
```

### 2. AbstractCharacterModel

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from uuid import UUID

class AbstractCharacterModel(ABC):
    """
    Abstract base class for character representation
    Supports dynamic trait and personality management
    """
    
    @abstractmethod
    def __init__(
        self, 
        name: str, 
        personality: Dict[str, Any],
        background: str = None
    ):
        """
        Initialize a character with core attributes
        
        Args:
            name (str): Character name
            personality (Dict): Character personality traits
            background (str, optional): Character's backstory
        """
        pass
    
    @abstractmethod
    def update_personality_trait(
        self, 
        trait_name: str, 
        trait_value: Any
    ) -> None:
        """
        Update or add a personality trait
        
        Args:
            trait_name (str): Name of the trait
            trait_value (Any): Value of the trait
        """
        pass
    
    @abstractmethod
    def generate_action(
        self, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an autonomous action based on character traits and context
        
        Args:
            context (Dict): Current story/interaction context
        
        Returns:
            Dict: Generated character action
        """
        pass
```

### 3. AbstractMemoryManager

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from uuid import UUID

class AbstractMemoryManager(ABC):
    """
    Abstract base class for memory management
    Supports flexible memory storage, retrieval, and relevance scoring
    """
    
    @abstractmethod
    async def store_memory(
        self, 
        character_id: UUID, 
        memory_content: str, 
        context: Dict[str, Any] = None,
        importance: float = 0.5
    ) -> UUID:
        """
        Store a memory for a character
        
        Args:
            character_id (UUID): ID of the character
            memory_content (str): Content of the memory
            context (Dict, optional): Contextual metadata
            importance (float, optional): Memory importance score
        
        Returns:
            UUID: Unique identifier for the stored memory
        """
        pass
    
    @abstractmethod
    async def retrieve_relevant_memories(
        self, 
        character_id: UUID, 
        context: Dict[str, Any],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant memories for a character
        
        Args:
            character_id (UUID): ID of the character
            context (Dict): Context for relevance matching
            top_k (int, optional): Number of top memories to retrieve
        
        Returns:
            List[Dict]: Most relevant memories
        """
        pass
```

### 4. Plugin Discovery and Loading

```python
import importlib
import pkgutil
import inspect
from typing import List, Type, Any

class PluginManager:
    """
    Manages discovery, loading, and registration of plugins
    """
    
    @staticmethod
    def discover_plugins(
        base_class: Type[ABC], 
        plugin_package: str
    ) -> List[Type[ABC]]:
        """
        Discover and load plugins inheriting from a base class
        
        Args:
            base_class (Type[ABC]): Base abstract class for plugins
            plugin_package (str): Package to search for plugins
        
        Returns:
            List[Type[ABC]]: Discovered plugin classes
        """
        plugins = []
        
        for _, name, _ in pkgutil.iter_modules([plugin_package]):
            module = importlib.import_module(f"{plugin_package}.{name}")
            
            for _, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj) and 
                    issubclass(obj, base_class) and 
                    obj is not base_class
                ):
                    plugins.append(obj)
        
        return plugins
```

## Example Plugin Implementation

```python
class OllamaAIModelPlugin(AbstractAIModelPlugin):
    """
    Example implementation of an AI model plugin for Ollama
    """
    
    def generate_text(self, prompt, context=None, parameters=None):
        # Ollama-specific text generation implementation
        pass
    
    def validate_model_configuration(self, config):
        # Validate Ollama-specific configuration
        pass
    
    def get_model_metadata(self):
        # Return Ollama model metadata
        pass
```

## Benefits of This Approach

1. **Flexibility**: Easy to add new AI models or character generation strategies
2. **Extensibility**: Plugins can be dynamically discovered and loaded
3. **Standardization**: Consistent interface across different implementations
4. **Modularity**: Components can be easily replaced or extended