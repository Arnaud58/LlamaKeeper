from typing import Any, Dict

from app.plugins.ai_models.ollama_model_plugin import OllamaModelPlugin
from app.utils.dependency_container import DependencyContainer
from app.utils.plugin_discovery import PluginDiscoveryManager


class AIPluginConfigurator:
    """
    Centralized configuration and management of AI plugins
    """

    @staticmethod
    def configure_ollama_plugin(config: Dict[str, Any] = None):
        """
        Configure and register the Ollama AI plugin

        Args:
            config (Dict, optional): Custom configuration for the Ollama plugin
        """
        # Default Ollama plugin configuration
        default_config = {
            "model_name": "llama2",
            "base_url": "http://localhost:11434/api",
            "timeout": 60.0,
            "max_tokens": 500,
            "temperature": 0.7,
            "top_p": 0.9,
        }

        # Merge default and provided configuration
        merged_config = {**default_config, **(config or {})}

        # Initialize dependency container
        container = DependencyContainer()

        # Register Ollama plugin with configuration
        container.register_service(
            OllamaModelPlugin,
            implementation=lambda: OllamaModelPlugin(**merged_config),
            lifecycle="factory",
        )

        # Optional: Configure plugin with additional settings
        container.configure_service(OllamaModelPlugin, config=merged_config)

        # Optional: Add lifecycle hooks
        container.add_lifecycle_hook(
            OllamaModelPlugin,
            "after_create",
            lambda plugin: plugin._logger.info("Ollama plugin initialized"),
        )

    @staticmethod
    def discover_ai_plugins():
        """
        Discover and load available AI plugins
        """
        discovery_manager = PluginDiscoveryManager(
            base_package="app.plugins.ai_models",
            plugin_base_classes=[OllamaModelPlugin],
        )

        discovered_plugins = discovery_manager.discover_plugins()
        return discovered_plugins


# Example usage
def setup_ai_plugins():
    """
    Setup and configure AI plugins for the application
    """
    # Configure Ollama plugin with custom settings
    AIPluginConfigurator.configure_ollama_plugin(
        {"model_name": "mistral", "temperature": 0.5}
    )

    # Discover available AI plugins
    discovered_plugins = AIPluginConfigurator.discover_ai_plugins()
    print("Discovered AI Plugins:", discovered_plugins)
