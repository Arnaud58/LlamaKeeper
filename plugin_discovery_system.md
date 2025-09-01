# Plugin Discovery and Loading System for LlamaKeeper

## Overview
A flexible, extensible plugin management system that enables dynamic discovery, loading, and configuration of modular components.

## Core Plugin Discovery Mechanism

```python
import os
import importlib
import inspect
from typing import Type, List, Dict, Any, Optional
from abc import ABC

class PluginDiscoveryManager:
    """
    Advanced plugin discovery and management system
    Supports dynamic loading of modular components
    """
    
    def __init__(
        self, 
        base_package: str = 'app.plugins',
        plugin_base_classes: Optional[List[Type[ABC]]] = None
    ):
        """
        Initialize plugin discovery manager
        
        Args:
            base_package (str): Base package to search for plugins
            plugin_base_classes (List[Type], optional): Base classes for plugin validation
        """
        self.base_package = base_package
        self.plugin_base_classes = plugin_base_classes or []
        self.discovered_plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_configurations: Dict[str, Dict[str, Any]] = {}
    
    def discover_plugins(self) -> Dict[str, List[Type]]:
        """
        Discover and load plugins across different categories
        
        Returns:
            Dict: Discovered plugins categorized by base class
        """
        discovered_plugins = {}
        
        # Recursively search for plugin modules
        for root, dirs, files in os.walk(
            self._get_package_path(self.base_package)
        ):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_path = os.path.join(root, file)
                    relative_path = os.path.relpath(
                        module_path, 
                        self._get_package_path(self.base_package)
                    )
                    module_name = (
                        self.base_package + '.' + 
                        relative_path.replace(os.path.sep, '.')[:-3]
                    )
                    
                    try:
                        module = importlib.import_module(module_name)
                        self._process_module_plugins(module, discovered_plugins)
                    except ImportError as e:
                        print(f"Error importing module {module_name}: {e}")
        
        return discovered_plugins
    
    def _process_module_plugins(
        self, 
        module: Any, 
        discovered_plugins: Dict[str, List[Type]]
    ):
        """
        Process plugins within a module
        
        Args:
            module (Any): Imported module
            discovered_plugins (Dict): Accumulator for discovered plugins
        """
        for name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj) and 
                not inspect.isabstract(obj)
            ):
                # Check against base plugin classes
                for base_class in self.plugin_base_classes:
                    if issubclass(obj, base_class) and obj is not base_class:
                        category = base_class.__name__
                        if category not in discovered_plugins:
                            discovered_plugins[category] = []
                        discovered_plugins[category].append(obj)
    
    def load_plugin(
        self, 
        plugin_class: Type, 
        config: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Load and configure a specific plugin
        
        Args:
            plugin_class (Type): Plugin class to instantiate
            config (Dict, optional): Plugin-specific configuration
        
        Returns:
            Any: Instantiated plugin
        """
        try:
            # Merge default and provided configuration
            default_config = self.plugin_configurations.get(
                plugin_class.__name__, 
                {}
            )
            merged_config = {**default_config, **(config or {})}
            
            # Instantiate plugin with configuration
            plugin_instance = plugin_class(**merged_config)
            
            # Validate plugin
            self._validate_plugin(plugin_instance)
            
            return plugin_instance
        
        except Exception as e:
            print(f"Plugin loading error for {plugin_class.__name__}: {e}")
            raise
    
    def _validate_plugin(self, plugin: Any):
        """
        Validate a loaded plugin
        
        Args:
            plugin (Any): Plugin instance to validate
        
        Raises:
            ValueError: If plugin fails validation
        """
        # Implement plugin-specific validation logic
        # Example: Check required methods, configuration, etc.
        pass
    
    def register_plugin_configuration(
        self, 
        plugin_class: Type, 
        config: Dict[str, Any]
    ):
        """
        Register configuration for a plugin type
        
        Args:
            plugin_class (Type): Plugin class
            config (Dict): Configuration parameters
        """
        self.plugin_configurations[plugin_class.__name__] = config
    
    def _get_package_path(self, package_name: str) -> str:
        """
        Get the filesystem path for a package
        
        Args:
            package_name (str): Fully qualified package name
        
        Returns:
            str: Filesystem path to the package
        """
        try:
            package = importlib.import_module(package_name)
            return os.path.dirname(package.__file__)
        except ImportError:
            raise ValueError(f"Cannot find package: {package_name}")

# Plugin Discovery Decorator
def plugin_discoverable(base_class: Optional[Type[ABC]] = None):
    """
    Decorator to mark classes as discoverable plugins
    
    Args:
        base_class (Type, optional): Base class for plugin categorization
    """
    def decorator(cls):
        if base_class:
            # Ensure the class is a subclass of the base class
            if not issubclass(cls, base_class):
                raise TypeError(f"{cls.__name__} must inherit from {base_class.__name__}")
        return cls
    return decorator
```

## Plugin Discovery Workflow

```python
# Example Usage

# Define base plugin classes
class AIModelPlugin(ABC):
    """Base class for AI model plugins"""
    pass

class CharacterModelPlugin(ABC):
    """Base class for character model plugins"""
    pass

# Initialize plugin discovery
plugin_manager = PluginDiscoveryManager(
    base_package='app.plugins',
    plugin_base_classes=[AIModelPlugin, CharacterModelPlugin]
)

# Register default configurations
plugin_manager.register_plugin_configuration(
    OllamaAIModelPlugin,
    {
        'default_model': 'llama2:7b',
        'temperature': 0.7
    }
)

# Discover plugins
discovered_plugins = plugin_manager.discover_plugins()

# Load a specific plugin
ollama_plugin = plugin_manager.load_plugin(
    OllamaAIModelPlugin, 
    config={'temperature': 0.8}
)
```

## Key Features

1. **Dynamic Plugin Discovery**
   - Recursive module scanning
   - Supports multiple plugin base classes
   - Flexible package configuration

2. **Configurable Plugin Loading**
   - Default and runtime configuration
   - Mergeable configuration parameters
   - Plugin-specific validation

3. **Extensibility**
   - Easy to add new plugin types
   - Supports custom base classes
   - Decorator-based plugin marking

4. **Error Handling**
   - Comprehensive import error management
   - Plugin validation
   - Configurable logging

## Plugin Directory Structure

```
app/
└── plugins/
    ├── ai_models/
    │   ├── ollama_plugin.py
    │   └── openai_plugin.py
    ├── character_models/
    │   ├── base_character_plugin.py
    │   └── advanced_character_plugin.py
    └── memory_managers/
        ├── sqlite_memory_plugin.py
        └── redis_memory_plugin.py
```

## Benefits

- **Modularity**: Easy component replacement
- **Flexibility**: Runtime plugin configuration
- **Scalability**: Support for multiple plugin types
- **Maintainability**: Centralized plugin management

## Recommended Next Steps

1. Implement plugin validation mechanisms
2. Add comprehensive logging
3. Create plugin compatibility checks
4. Develop advanced configuration management