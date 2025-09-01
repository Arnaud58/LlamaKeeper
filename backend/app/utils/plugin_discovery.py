import importlib
import inspect
import logging
import os
from abc import ABC
from typing import Any, Dict, List, Optional, Type


class PluginDiscoveryManager:
    """
    Advanced plugin discovery and management system
    Supports dynamic loading of modular components
    """

    def __init__(
        self,
        base_package: str = "app.plugins",
        plugin_base_classes: Optional[List[Type[ABC]]] = None,
        logger_name: str = "PluginDiscoveryManager",
    ):
        """
        Initialize plugin discovery manager

        Args:
            base_package (str): Base package to search for plugins
            plugin_base_classes (List[Type], optional): Base classes for plugin validation
            logger_name (str, optional): Name for the logger
        """
        self.base_package = base_package
        self.plugin_base_classes = plugin_base_classes or []
        self.discovered_plugins: Dict[str, Dict[str, Any]] = {}
        self.plugin_configurations: Dict[str, Dict[str, Any]] = {}

        # Setup logging
        self._logger = logging.getLogger(logger_name)
        self._logger.setLevel(logging.INFO)

    def discover_plugins(self) -> Dict[str, List[Type]]:
        """
        Discover and load plugins across different categories

        Returns:
            Dict: Discovered plugins categorized by base class
        """
        discovered_plugins = {}

        try:
            # Recursively search for plugin modules
            for root, _, files in os.walk(self._get_package_path(self.base_package)):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        module_path = os.path.join(root, file)
                        relative_path = os.path.relpath(
                            module_path, self._get_package_path(self.base_package)
                        )
                        module_name = (
                            self.base_package
                            + "."
                            + relative_path.replace(os.path.sep, ".")[:-3]
                        )

                        try:
                            module = importlib.import_module(module_name)
                            self._process_module_plugins(module, discovered_plugins)
                        except ImportError as e:
                            self._logger.error(
                                f"Error importing module {module_name}: {e}"
                            )

            self._logger.info(f"Discovered plugins: {list(discovered_plugins.keys())}")
            return discovered_plugins

        except Exception as e:
            self._logger.error(f"Plugin discovery failed: {e}")
            return {}

    def _process_module_plugins(
        self, module: Any, discovered_plugins: Dict[str, List[Type]]
    ):
        """
        Process plugins within a module

        Args:
            module (Any): Imported module
            discovered_plugins (Dict): Accumulator for discovered plugins
        """
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and not inspect.isabstract(obj):
                # Check against base plugin classes
                for base_class in self.plugin_base_classes:
                    if issubclass(obj, base_class) and obj is not base_class:
                        category = base_class.__name__
                        if category not in discovered_plugins:
                            discovered_plugins[category] = []
                        discovered_plugins[category].append(obj)
                        self._logger.info(
                            f"Discovered plugin: {obj.__name__} in category {category}"
                        )

    def load_plugin(
        self, plugin_class: Type, config: Optional[Dict[str, Any]] = None
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
            default_config = self.plugin_configurations.get(plugin_class.__name__, {})
            merged_config = {**default_config, **(config or {})}

            # Instantiate plugin with configuration
            plugin_instance = plugin_class(**merged_config)

            # Validate plugin
            self._validate_plugin(plugin_instance)

            self._logger.info(f"Loaded plugin: {plugin_class.__name__}")
            return plugin_instance

        except Exception as e:
            self._logger.error(f"Plugin loading error for {plugin_class.__name__}: {e}")
            raise

    def _validate_plugin(self, plugin: Any):
        """
        Validate a loaded plugin

        Args:
            plugin (Any): Plugin instance to validate

        Raises:
            ValueError: If plugin fails validation
        """
        # Basic validation checks
        required_methods = [
            "generate_text",  # Common method for AI plugins
            "get_model_metadata",  # Common method for model plugins
        ]

        for method in required_methods:
            if not hasattr(plugin, method):
                raise ValueError(f"Plugin missing required method: {method}")

        self._logger.info(f"Plugin {plugin.__class__.__name__} validated successfully")

    def register_plugin_configuration(self, plugin_class: Type, config: Dict[str, Any]):
        """
        Register configuration for a plugin type

        Args:
            plugin_class (Type): Plugin class
            config (Dict): Configuration parameters
        """
        self.plugin_configurations[plugin_class.__name__] = config
        self._logger.info(f"Registered configuration for {plugin_class.__name__}")

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
                raise TypeError(
                    f"{cls.__name__} must inherit from {base_class.__name__}"
                )
        return cls

    return decorator
