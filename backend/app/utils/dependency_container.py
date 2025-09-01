import inspect
import logging
from functools import wraps
from typing import Any, Callable, Dict, Optional, Type


class DependencyContainer:
    """
    Advanced dependency injection container for LlamaKeeper

    Supports:
    - Dynamic component registration
    - Lazy loading
    - Lifecycle management
    - Configuration-driven instantiation
    """

    _instance = None

    def __new__(cls):
        """
        Singleton pattern implementation

        Returns:
            DependencyContainer: Singleton instance
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initialize the dependency container
        """
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._configurations: Dict[str, Dict[str, Any]] = {}
        self._lifecycle_hooks: Dict[str, Dict[str, Callable]] = {
            "before_create": {},
            "after_create": {},
            "before_destroy": {},
            "after_destroy": {},
        }
        self._logger = logging.getLogger("DependencyContainer")
        self._logger.setLevel(logging.INFO)

    def register_service(
        self,
        service_type: Type,
        implementation: Any = None,
        name: Optional[str] = None,
        lifecycle: str = "singleton",
    ):
        """
        Register a service with optional custom implementation

        Args:
            service_type (Type): Base/interface type
            implementation (Any, optional): Concrete implementation
            name (str, optional): Named service registration
            lifecycle (str): Service lifecycle ('singleton', 'transient', 'factory')
        """
        key = name or service_type.__name__

        if implementation is None:
            implementation = service_type

        try:
            if lifecycle == "singleton":
                # Create single instance
                instance = implementation()
                self._services[key] = instance
                self._logger.info(f"Registered singleton service: {key}")
            elif lifecycle == "factory":
                # Store factory method
                self._factories[key] = implementation
                self._logger.info(f"Registered factory service: {key}")
            else:
                # Store type for dynamic instantiation
                self._services[key] = implementation
                self._logger.info(f"Registered transient service: {key}")
        except Exception as e:
            self._logger.error(f"Error registering service {key}: {e}")
            raise

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

        try:
            if key in self._factories:
                # Call factory method
                service = self._factories[key]()
                self._logger.info(f"Created service via factory: {key}")
                return service

            service = self._services[key]

            # If service is a type, instantiate it
            if isinstance(service, type):
                resolved_service = self._create_instance(service)
                self._logger.info(f"Created service instance: {key}")
                return resolved_service

            return service
        except Exception as e:
            self._logger.error(f"Error resolving service {key}: {e}")
            raise

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
            if param_name != "self":
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
        self, service_type: Type, config: Dict[str, Any], name: Optional[str] = None
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
        self._logger.info(f"Configured service: {key}")

    def add_lifecycle_hook(
        self,
        service_type: Type,
        hook_type: str,
        hook: Callable,
        name: Optional[str] = None,
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
        self._logger.info(f"Added {hook_type} lifecycle hook for {key}")


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
