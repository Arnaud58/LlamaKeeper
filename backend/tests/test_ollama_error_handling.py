import pytest
import logging
import structlog
from app.plugins.ai_models.ollama_model_plugin import OllamaModelPlugin
from app.core.logging_config import error_tracker

class TestOllamaErrorHandling:
    def setup_method(self):
        """
        Reset error tracker before each test
        """
        error_tracker.error_count = 0
        error_tracker.error_log = []
    
    def test_logging_configuration(self):
        """
        Verify logging configuration
        """
        # Vérifier la configuration de base
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        
        # Vérifier la présence des handlers
        handlers = root_logger.handlers
        assert len(handlers) == 2  # Console et fichier
        
        # Vérifier la configuration de structlog
        logger = structlog.get_logger()
        assert isinstance(logger, structlog.stdlib.BoundLogger)
    
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