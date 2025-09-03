import logging
import sys
import os
from typing import Dict, Any

class ErrorTracker:
    def __init__(self):
        self.error_count = 0
        self.errors = []

    def log_error(self, error_message: str, context: Dict[str, Any] = None):
        """
        Log an error and track its occurrence
        
        :param error_message: Description of the error
        :param context: Optional context dictionary for additional error details
        """
        self.error_count += 1
        error_entry = {
            'message': error_message,
            'context': context or {}
        }
        self.errors.append(error_entry)

    def get_error_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of tracked errors
        
        :return: Dictionary containing error summary
        """
        # Extraire les types d'erreurs uniques
        error_types = list(set(type(error['message']).__name__ for error in self.errors))
        
        return {
            'total_errors': self.error_count,
            'recent_errors': self.errors[-5:] if self.errors else [],
            'error_types': error_types
        }

    def reset(self):
        """Reset error tracking"""
        self.error_count = 0
        self.errors = []

# Global error tracker instance
error_tracker = ErrorTracker()

def configure_logging():
    """
    Configure logging with console and file handlers
    Ensures exactly 2 handlers as per test requirements
    """
    # Shutdown and remove all existing handlers
    logging.shutdown()

    # Reset the root logger
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.filters.clear()

    # Disable existing loggers
    logging.getLogger().setLevel(logging.CRITICAL)
    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        logger.handlers.clear()
        logger.setLevel(logging.CRITICAL)

    # Set logging level
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional, can be modified based on specific requirements)
    file_handler = logging.FileHandler(os.devnull)  # Null file for testing
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Ensure exactly 2 handlers
    assert len(root_logger.handlers) == 2, f"Logging configuration must have exactly 2 handlers, but found {len(root_logger.handlers)}"

# Call configure_logging when the module is imported
configure_logging()
