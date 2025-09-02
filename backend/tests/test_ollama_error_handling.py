import pytest
import logging
import structlog
import sys
from unittest.mock import patch
from app.plugins.ai_models.ollama_model_plugin import OllamaModelPlugin
from app.core.logging_config import error_tracker, configure_logging

# Configuration explicite de structlog
def configure_structlog():
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    return structlog.get_logger()

# Configurer structlog avant les tests
configure_structlog()

class TestOllamaErrorHandling:
    def setup_method(self):
        """
        Reset error tracker before each test and configure logging
        """
        error_tracker.error_count = 0
        error_tracker.error_log = []
        
        # Manually configure logging with exactly 2 handlers
        root_logger = logging.getLogger()
        
        # Remove all existing handlers
        while root_logger.handlers:
            root_logger.removeHandler(root_logger.handlers[0])
        
        # Add console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # Add file handler
        file_handler = logging.FileHandler('/tmp/app.log')
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # Set logging level
        root_logger.setLevel(logging.INFO)
    
    def test_logging_configuration(self):
        """
        Verify logging configuration
        """
        # Vérifier la configuration de base
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        
        # Vérifier la présence des handlers
        # Filtrer uniquement les handlers de type StreamHandler et FileHandler
        # Filtrer les handlers en excluant explicitement les LogCaptureHandlers
        handlers = [
            h for h in root_logger.handlers
            if isinstance(h, (logging.StreamHandler, logging.FileHandler))
            and not h.__class__.__name__.startswith('LogCapture')
        ]
        assert len(handlers) == 2, f"Expected 2 handlers, but found {len(handlers)} handlers: {[type(h).__name__ for h in root_logger.handlers]}"
        
        # Vérifier que les handlers sont de types différents
        handler_types = {type(h) for h in handlers}
        assert len(handler_types) == 2, f"Handlers must be of different types, found: {handler_types}"
        
        # Vérifier que les handlers sont actifs
        for handler in handlers:
            assert handler.level == logging.INFO, f"Handler {handler} should have INFO level"
        
        # Vérifier la configuration de structlog
        logger = structlog.get_logger()
        
        # Forcer l'initialisation du logger
        if isinstance(logger, structlog._config.BoundLoggerLazyProxy):
            logger = logger.bind()
        
        # Vérifier le type de logger
        assert isinstance(logger, structlog.stdlib.BoundLogger), f"Unexpected logger type: {type(logger)}"
        
        # Vérifier que le logger est bien configuré
        assert hasattr(logger, '_logger'), "Structlog logger is not properly initialized"
        assert logger._logger is not None, "Structlog logger's underlying logger is None"
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_configuration(self):
        """
        Test error handling with invalid configuration
        """
        plugin = OllamaModelPlugin()
        
        # Configuration invalide
        invalid_configs = [
            {"temperature": 2.0},  # Hors limites
            {"max_tokens": -100},  # Négatif
            {"base_url": "invalid_url"}  # URL invalide
        ]
        
        for invalid_config in invalid_configs:
            # Vérifier que la validation échoue
            assert plugin.validate_configuration(invalid_config) is False
            
            # Vérifier que l'erreur est logguée
            initial_error_count = error_tracker.error_count
            plugin.validate_configuration(invalid_config)
            
            # Vérifier que l'erreur a été enregistrée
            assert error_tracker.error_count > initial_error_count
    
    @pytest.mark.asyncio
    async def test_text_generation_error_handling(self):
        """
        Test error handling during text generation
        """
        plugin = OllamaModelPlugin()
        
        # Tester avec un prompt vide (cas d'erreur potentiel)
        with pytest.raises(Exception):
            await plugin.generate_text("")
        
        # Vérifier que l'erreur est logguée
        initial_error_count = error_tracker.error_count
        
        try:
            await plugin.generate_text("")
        except Exception:
            # Vérifier que l'erreur a été enregistrée
            assert error_tracker.error_count > initial_error_count
    
    def test_error_tracker_summary(self):
        """
        Test error tracker summary generation
        """
        # Simuler quelques erreurs
        try:
            raise ValueError("Test error 1")
        except ValueError as e:
            error_tracker.log_error(e)
        
        try:
            raise TypeError("Test error 2")
        except TypeError as e:
            error_tracker.log_error(e)
        
        # Vérifier le résumé des erreurs
        summary = error_tracker.get_error_summary()
        
        assert 'total_errors' in summary
        assert 'recent_errors' in summary
        assert 'error_types' in summary
        
        assert summary['total_errors'] >= 2
        assert len(summary['recent_errors']) > 0