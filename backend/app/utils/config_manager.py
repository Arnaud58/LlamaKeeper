import json
import logging
import os
from functools import wraps
from typing import Any, Dict, Optional, Type

import jsonschema
import yaml


class ConfigurationManager:
    """
    Advanced configuration management system for LlamaKeeper

    Supports:
    - Environment-specific configurations
    - Runtime configuration updates
    - Configuration schema validation
    - Multiple configuration sources
    """

    _instance = None

    def __new__(cls):
        """
        Singleton pattern implementation

        Returns:
            ConfigurationManager: Singleton instance
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """
        Initialize the configuration manager
        """
        self._configs: Dict[str, Dict[str, Any]] = {}
        self._schemas: Dict[str, Dict] = {}
        self._logger = logging.getLogger("ConfigurationManager")
        self._logger.setLevel(logging.INFO)

        # Load default configurations
        self._load_default_configs()

    def _load_default_configs(self):
        """
        Load default configurations from environment and files
        """
        # Environment-based configuration
        env_config_path = os.environ.get(
            "LLAMAKEEPER_CONFIG_PATH",
            os.path.join(os.path.dirname(__file__), "..", "config"),
        )

        # Try loading JSON and YAML configurations
        for config_type in ["json", "yaml", "yml"]:
            for env in ["development", "production", "testing"]:
                config_file = os.path.join(
                    env_config_path, f"{env}_config.{config_type}"
                )
                if os.path.exists(config_file):
                    self.load_config_file(config_file, env)

    def load_config_file(self, file_path: str, env: Optional[str] = None):
        """
        Load configuration from a file

        Args:
            file_path (str): Path to the configuration file
            env (str, optional): Environment name
        """
        try:
            with open(file_path, "r") as f:
                if file_path.endswith((".yaml", ".yml")):
                    config = yaml.safe_load(f)
                else:
                    config = json.load(f)

                # Use filename or provided env as key
                env = env or os.path.splitext(os.path.basename(file_path))[0]
                self._configs[env] = config
                self._logger.info(f"Loaded configuration for {env} from {file_path}")

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            self._logger.error(f"Error parsing configuration file {file_path}: {e}")
        except IOError as e:
            self._logger.error(f"Error reading configuration file {file_path}: {e}")

    def register_config_schema(self, config_type: str, schema: Dict[str, Any]):
        """
        Register a JSON schema for configuration validation

        Args:
            config_type (str): Type of configuration
            schema (Dict): JSON schema for validation
        """
        self._schemas[config_type] = schema
        self._logger.info(f"Registered schema for {config_type}")

    def get_config(self, config_type: str, env: Optional[str] = None) -> Dict[str, Any]:
        """
        Retrieve configuration

        Args:
            config_type (str): Type of configuration
            env (str, optional): Environment name (defaults to current)

        Returns:
            Dict: Configuration dictionary
        """
        env = env or os.environ.get("LLAMAKEEPER_ENV", "development")

        try:
            config = self._configs.get(env, {}).get(config_type, {})

            # Validate against schema if exists
            if config_type in self._schemas:
                self.validate_config(config, config_type)

            return config

        except Exception as e:
            self._logger.error(f"Error retrieving {config_type} config: {e}")
            return {}

    def update_config(
        self, config_type: str, updates: Dict[str, Any], env: Optional[str] = None
    ):
        """
        Update configuration at runtime

        Args:
            config_type (str): Type of configuration
            updates (Dict): Configuration updates
            env (str, optional): Environment name
        """
        env = env or os.environ.get("LLAMAKEEPER_ENV", "development")

        try:
            # Ensure configuration exists
            if env not in self._configs:
                self._configs[env] = {}

            # Update configuration
            if config_type not in self._configs[env]:
                self._configs[env][config_type] = {}

            self._configs[env][config_type].update(updates)

            # Validate updated configuration
            if config_type in self._schemas:
                self.validate_config(self._configs[env][config_type], config_type)

            self._logger.info(f"Updated {config_type} configuration for {env}")

        except Exception as e:
            self._logger.error(f"Error updating {config_type} config: {e}")
            raise

    def validate_config(self, config: Dict[str, Any], config_type: str):
        """
        Validate configuration against registered schema

        Args:
            config (Dict): Configuration to validate
            config_type (str): Type of configuration

        Raises:
            jsonschema.ValidationError: If configuration is invalid
        """
        if config_type not in self._schemas:
            self._logger.warning(f"No schema registered for {config_type}")
            return

        try:
            jsonschema.validate(instance=config, schema=self._schemas[config_type])
            self._logger.info(f"Configuration validated for {config_type}")
        except jsonschema.ValidationError as e:
            self._logger.error(
                f"Configuration validation failed for {config_type}: {e}"
            )
            raise


def config_injectable(config_type: str, env: Optional[str] = None):
    """
    Decorator to inject configuration

    Args:
        config_type (str): Type of configuration to inject
        env (str, optional): Environment name
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Resolve configuration
            config_manager = ConfigurationManager()
            config = config_manager.get_config(config_type, env)

            # Add resolved config to kwargs
            kwargs[f"{config_type}_config"] = config

            return func(*args, **kwargs)

        return wrapper

    return decorator
