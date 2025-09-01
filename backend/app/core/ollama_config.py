import os
import platform
import shutil
import subprocess
import sys
from typing import Dict, Optional


class OllamaSetup:
    """
    Manages Ollama installation, configuration, and model management
    """

    DEFAULT_MODELS = [
        "llama2:7b",  # Base language model
        "mistral:7b",  # Alternative language model
        "nomic-embed-text",  # Embedding model for semantic search
    ]

    @classmethod
    def check_ollama_installed(cls) -> bool:
        """
        Check if Ollama is installed on the system

        Returns:
            bool: True if Ollama is installed, False otherwise
        """
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    @classmethod
    def install_ollama(cls) -> bool:
        """
        Install Ollama based on the current operating system

        Returns:
            bool: True if installation was successful, False otherwise
        """
        os_name = platform.system().lower()

        try:
            if os_name == "darwin":  # macOS
                return cls._install_ollama_macos()
            elif os_name == "linux":
                return cls._install_ollama_linux()
            elif os_name == "windows":
                return cls._install_ollama_windows()
            else:
                print(f"Unsupported OS: {os_name}")
                return False
        except Exception as e:
            print(f"Ollama installation error: {e}")
            return False

    @classmethod
    def _install_ollama_macos(cls) -> bool:
        """Install Ollama on macOS"""
        install_cmd = ["/bin/bash", "-c", "curl https://ollama.ai/install.sh | sh"]

        result = subprocess.run(install_cmd, capture_output=True, text=True)
        return result.returncode == 0

    @classmethod
    def _install_ollama_linux(cls) -> bool:
        """Install Ollama on Linux"""
        install_cmd = ["/bin/bash", "-c", "curl https://ollama.ai/install.sh | sh"]

        result = subprocess.run(install_cmd, capture_output=True, text=True)
        return result.returncode == 0

    @classmethod
    def _install_ollama_windows(cls) -> bool:
        """Install Ollama on Windows"""
        # Windows installation might require a different approach
        print("Windows Ollama installation requires manual download from ollama.ai")
        return False

    @classmethod
    def pull_models(cls, models: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        Pull specified Ollama models

        Args:
            models (List[str], optional): List of models to pull

        Returns:
            Dict[str, bool]: Model pull status
        """
        models_to_pull = models or cls.DEFAULT_MODELS

        model_status = {}
        for model in models_to_pull:
            try:
                result = subprocess.run(
                    ["ollama", "pull", model], capture_output=True, text=True
                )
                model_status[model] = result.returncode == 0
            except Exception as e:
                print(f"Error pulling model {model}: {e}")
                model_status[model] = False

        return model_status

    @classmethod
    def configure_model_paths(cls) -> Dict[str, str]:
        """
        Configure and return paths for model storage

        Returns:
            Dict[str, str]: Configured model paths
        """
        base_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "models"
        )

        os.makedirs(base_path, exist_ok=True)

        return {
            "base_path": base_path,
            "models_path": os.path.join(base_path, "ollama_models"),
            "cache_path": os.path.join(base_path, "model_cache"),
        }

    @classmethod
    def validate_ollama_setup(cls) -> bool:
        """
        Comprehensive validation of Ollama setup

        Returns:
            bool: True if Ollama is ready, False otherwise
        """
        if not cls.check_ollama_installed():
            print("Ollama not installed. Attempting installation...")
            if not cls.install_ollama():
                print("Ollama installation failed.")
                return False

        model_paths = cls.configure_model_paths()
        print(f"Model paths configured: {model_paths}")

        model_pull_status = cls.pull_models()
        failed_models = [
            model for model, status in model_pull_status.items() if not status
        ]

        if failed_models:
            print(f"Failed to pull models: {failed_models}")
            return False

        return True


def setup_ollama():
    """
    Entry point for Ollama setup
    """
    print("Initializing Ollama setup...")
    success = OllamaSetup.validate_ollama_setup()

    if success:
        print("Ollama setup completed successfully.")
    else:
        print("Ollama setup encountered issues.")

    return success


if __name__ == "__main__":
    setup_ollama()
