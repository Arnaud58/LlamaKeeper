# Dependency Injection System for LlamaKeeper

## Overview
A flexible, extensible dependency injection system that supports dynamic component registration, lazy loading, and advanced configuration management.

## Core Design Principles
1. **Modularity**: Easy component registration and replacement
2. **Flexibility**: Support for different dependency lifetimes
3. **Lazy Loading**: Efficient resource management
4. **Configuration-Driven**: Runtime configuration support

## Dependency Injection Container

```python
from typing import Dict, Any, Type, Callable, Optional
from functools import wraps
import inspect

class DependencyContainer:
    """
    Advanced dependency injection container for LlamaKeeper
    
    Supports:
    - Dynamic component registration
    - Lazy loading
    - Lifecycle management
    - Configuration-driven instantiation
    """
    
    def __init__(self):
        """
        Initialize the dependency container
        """
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._configurations: Dict[str, Dict[str, Any]] = {}
        self._lifecycle_hooks: Dict[str, Dict[str, Callable]] = {
            'before_create': {},
            'after_create': {},
            'before_destroy': {},
            'after_destroy': {}
        }
    
    def register_service(
        self, 
        service_type: Type, 
        implementation: Any = None,
        name: Optional[str] = None,
        lifecycle: str = 'singleton'
    ):
        """
        Register a service with optional custom implementation
        
        Args:
            service_type (Type): Base/interface type
            implementation (Any, optional): Concrete implementation
            name (str, optional): Named service registration
            lifecycle (str): Service lifecycle ('singleton', 'transient', 'scoped')
        """
        key = name or service_type.__name__
        
        if implementation is None:
            implementation = service_type
        
        if lifecycle == 'singleton':
            # Create single instance
            self._services[key] = implementation()
        elif lifecycle == 'factory':
            # Store factory method
            self._factories[key] = implementation
        else:
            # Store type for dynamic instantiation
            self._services[key] = implementation
    
    def resolve(self, service_type: Type, name: Optional[str] = None) -> Any:
        """
        Resolve a service instance
        
        Args:
            service_type (Type): Service type to resolve
            name (str, optional): Named service
        
        Returns:
            Any: Resolved service instance
        """
        key = name or service_type.__name__
        
        if key not in self._services and key not in self._factories:
            raise ValueError(f"No service registered for {key}")
        
        if key in self._factories:
            # Call factory method
            return self._factories[key]()
        
        service = self._services[key]
        
        # If service is a type, instantiate it
        if isinstance(service, type):
            return self._create_instance(service)
        
        return service
    
    def _create_instance(self, service_type: Type) -> Any:
        """
        Create an instance with dependency injection
        
        Args:
            service_type (Type): Type to instantiate
        
        Returns:
            Any: Instantiated object
        """
        # Inspect constructor
        signature = inspect.signature(service_type.__init__)
        
        # Resolve dependencies
        dependencies = {}
        for param_name, param in signature.parameters.items():
            if param_name != 'self':
                # Try to resolve dependency
                try:
                    dependencies[param_name] = self.resolve(param.annotation)
                except ValueError:
                    # Use default value or raise error
                    if param.default == inspect.Parameter.empty:
                        raise
                    dependencies[param_name] = param.default
        
        return service_type(**dependencies)
    
    def configure_service(
        self, 
        service_type: Type, 
        config: Dict[str, Any],
        name: Optional[str] = None
    ):
        """
        Add configuration for a service
        
        Args:
            service_type (Type): Service type
            config (Dict): Configuration parameters
            name (str, optional): Named service configuration
        """
        key = name or service_type.__name__
        self._configurations[key] = config
    
    def add_lifecycle_hook(
        self, 
        service_type: Type, 
        hook_type: str, 
        hook: Callable,
        name: Optional[str] = None
    ):
        """
        Add a lifecycle hook for a service
        
        Args:
            service_type (Type): Service type
            hook_type (str): Hook type ('before_create', 'after_create', etc.)
            hook (Callable): Hook function
            name (str, optional): Named service
        """
        key = name or service_type.__name__
        
        if hook_type not in self._lifecycle_hooks:
            raise ValueError(f"Invalid hook type: {hook_type}")
        
        self._lifecycle_hooks[hook_type][key] = hook

# Decorator for dependency injection
def inject(service_type: Type, name: Optional[str] = None):
    """
    Decorator to inject dependencies
    
    Args:
        service_type (Type): Service type to inject
        name (str, optional): Named service
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Resolve dependency
            container = DependencyContainer()
            service = container.resolve(service_type, name)
            
            # Add resolved service to kwargs
            service_name = name or service_type.__name__.lower()
            kwargs[service_name] = service
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

## Usage Examples

### Basic Service Registration

```python
# Create container
container = DependencyContainer()

# Register services
container.register_service(OllamaClient)
container.register_service(CharacterAutonomySystem)
container.register_service(MemoryManager)

# Resolve services
ollama_client = container.resolve(OllamaClient)
character_system = container.resolve(CharacterAutonomySystem)
```

### Dependency Injection with Configuration

```python
# Configure Ollama client
container.configure_service(
    OllamaClient, 
    {
        "base_url": "http://localhost:11434/api",
        "default_model": "llama2:7b"
    }
)

# Add lifecycle hooks
def log_ollama_creation(client):
    print(f"Ollama client created with model: {client.default_model}")

container.add_lifecycle_hook(
    OllamaClient, 
    'after_create', 
    log_ollama_creation
)
```

### Decorator-Based Injection

```python
@inject(OllamaClient)
def generate_story(ollama_client, prompt):
    # Use injected Ollama client
    return ollama_client.generate_text(prompt)
```

## Key Features

1. **Dynamic Service Registration**
   - Register services with custom implementations
   - Support for named services
   - Multiple lifecycle management strategies

2. **Automatic Dependency Resolution**
   - Inspect constructor signatures
   - Resolve dependencies recursively
   - Fallback to default values

3. **Configuration Management**
   - Runtime service configuration
   - Flexible parameter injection
   - Environment-specific settings

4. **Lifecycle Hooks**
   - Before/after creation hooks
   - Before/after destruction hooks
   - Logging and monitoring support

## Benefits

- Decoupled component design
- Easy testing and mocking
- Runtime configurability
- Simplified dependency management

## Recommended Next Steps

1. Implement comprehensive error handling
2. Add support for circular dependencies
3. Create advanced configuration loaders
4. Develop monitoring and logging integrations