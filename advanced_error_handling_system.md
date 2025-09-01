# Advanced Error Handling and Logging System for LlamaKeeper

## Overview
A robust, extensible error handling and logging system that provides comprehensive monitoring, detailed error tracking, and intelligent error recovery mechanisms.

## Core Error Handling Architecture

```python
import logging
import traceback
import json
import uuid
from enum import Enum, auto
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass, field

class ErrorSeverity(Enum):
    """
    Categorization of error severity levels
    Provides a structured approach to error classification
    """
    DEBUG = auto()
    INFO = auto()
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass
class ErrorContext:
    """
    Comprehensive error context tracking
    """
    error_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)
    severity: ErrorSeverity = ErrorSeverity.ERROR
    source_module: Optional[str] = None
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    additional_context: Dict[str, Any] = field(default_factory=dict)

class AdvancedErrorHandler:
    """
    Sophisticated error handling and logging system
    Supports comprehensive error tracking, recovery, and reporting
    """
    
    def __init__(
        self, 
        log_file: Optional[str] = 'llamakeeper_errors.log',
        error_reporting_callback: Optional[Callable] = None
    ):
        """
        Initialize advanced error handler
        
        Args:
            log_file (str, optional): Path to error log file
            error_reporting_callback (Callable, optional): External error reporting function
        """
        # Logging configuration
        self._logger = self._configure_logger(log_file)
        
        # Error tracking
        self._error_registry: Dict[str, ErrorContext] = {}
        self._error_reporting_callback = error_reporting_callback
        
        # Error recovery strategies
        self._recovery_strategies: Dict[str, Callable] = {}
    
    def _configure_logger(
        self, 
        log_file: Optional[str]
    ) -> logging.Logger:
        """
        Configure comprehensive logging system
        
        Args:
            log_file (str, optional): Path to log file
        
        Returns:
            logging.Logger: Configured logger
        """
        # Create logger
        logger = logging.getLogger('LlamaKeeperErrorLogger')
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler (if log file specified)
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(exc_info)s'
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def capture_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR
    ) -> ErrorContext:
        """
        Capture and log a comprehensive error context
        
        Args:
            error (Exception): Caught exception
            context (Dict, optional): Additional error context
            severity (ErrorSeverity): Error severity level
        
        Returns:
            ErrorContext: Detailed error information
        """
        # Create error context
        error_context = ErrorContext(
            severity=severity,
            source_module=error.__module__,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            additional_context=context or {}
        )
        
        # Log error
        log_method = {
            ErrorSeverity.DEBUG: self._logger.debug,
            ErrorSeverity.INFO: self._logger.info,
            ErrorSeverity.WARNING: self._logger.warning,
            ErrorSeverity.ERROR: self._logger.error,
            ErrorSeverity.CRITICAL: self._logger.critical
        }.get(severity, self._logger.error)
        
        log_method(
            f"Error Captured: {error_context.error_type} - {error_context.error_message}",
            extra={'error_context': error_context.__dict__}
        )
        
        # Store in error registry
        self._error_registry[error_context.error_id] = error_context
        
        # Trigger external error reporting if callback is set
        if self._error_reporting_callback:
            try:
                self._error_reporting_callback(error_context)
            except Exception as reporting_error:
                self._logger.error(f"Error reporting failed: {reporting_error}")
        
        return error_context
    
    def register_recovery_strategy(
        self, 
        error_type: str, 
        recovery_func: Callable
    ):
        """
        Register a recovery strategy for a specific error type
        
        Args:
            error_type (str): Error type to handle
            recovery_func (Callable): Recovery function
        """
        self._recovery_strategies[error_type] = recovery_func
    
    def attempt_recovery(
        self, 
        error_context: ErrorContext
    ) -> Dict[str, Any]:
        """
        Attempt to recover from an error using registered strategies
        
        Args:
            error_context (ErrorContext): Error context to recover from
        
        Returns:
            Dict: Recovery result
        """
        recovery_strategy = self._recovery_strategies.get(
            error_context.error_type
        )
        
        if recovery_strategy:
            try:
                recovery_result = recovery_strategy(error_context)
                
                self._logger.info(
                    f"Successfully recovered from error: {error_context.error_id}"
                )
                
                return {
                    'success': True,
                    'result': recovery_result
                }
            except Exception as recovery_error:
                self._logger.error(
                    f"Recovery attempt failed: {recovery_error}"
                )
        
        return {
            'success': False,
            'message': 'No recovery strategy available'
        }
    
    def get_error_summary(
        self, 
        since: Optional[datetime] = None,
        severity_threshold: ErrorSeverity = ErrorSeverity.WARNING
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive error summary
        
        Args:
            since (datetime, optional): Retrieve errors since this time
            severity_threshold (ErrorSeverity): Minimum severity to include
        
        Returns:
            Dict: Error summary statistics
        """
        filtered_errors = [
            error for error in self._error_registry.values()
            if (not since or error.timestamp >= since) and 
               error.severity.value >= severity_threshold.value
        ]
        
        error_summary = {
            'total_errors': len(filtered_errors),
            'errors_by_severity': {},
            'top_error_types': {},
            'recent_errors': []
        }
        
        # Aggregate error statistics
        for error in filtered_errors:
            # Count by severity
            severity_count = error_summary['errors_by_severity'].get(
                error.severity.name, 0
            )
            error_summary['errors_by_severity'][error.severity.name] = severity_count + 1
            
            # Count by error type
            type_count = error_summary['top_error_types'].get(
                error.error_type, 0
            )
            error_summary['top_error_types'][error.error_type] = type_count + 1
        
        # Get recent errors
        error_summary['recent_errors'] = [
            {
                'error_id': error.error_id,
                'timestamp': error.timestamp.isoformat(),
                'severity': error.severity.name,
                'error_type': error.error_type,
                'error_message': error.error_message
            }
            for error in sorted(
                filtered_errors, 
                key=lambda e: e.timestamp, 
                reverse=True
            )[:10]
        ]
        
        return error_summary

# Example Recovery Strategies
def ollama_connection_recovery(error_context: ErrorContext):
    """
    Example recovery strategy for Ollama connection errors
    """
    # Attempt to restart Ollama service
    # Implement actual recovery logic here
    return {
        'action': 'restart_ollama_service',
        'timestamp': datetime.now().isoformat()
    }

def ai_generation_fallback(error_context: ErrorContext):
    """
    Fallback strategy for AI generation failures
    """
    # Provide a default generated text
    return {
        'fallback_text': "I apologize, but I'm currently unable to generate a response.",
        'timestamp': datetime.now().isoformat()
    }

# Global Error Handler
error_handler = AdvancedErrorHandler(
    log_file='llamakeeper_errors.log',
    error_reporting_callback=None  # Optional external reporting
)

# Register recovery strategies
error_handler.register_recovery_strategy(
    'OllamaConnectionError', 
    ollama_connection_recovery
)

error_handler.register_recovery_strategy(
    'AIGenerationError', 
    ai_generation_fallback
)

# Example Usage in a Component
def example_ai_generation_with_error_handling():
    """
    Demonstrate error handling in an AI generation context
    """
    try:
        # Simulated AI generation that might fail
        result = generate_ai_text()
        return result
    except Exception as e:
        # Capture error
        error_context = error_handler.capture_error(
            e, 
            context={'generation_params': {...}},
            severity=ErrorSeverity.ERROR
        )
        
        # Attempt recovery
        recovery_result = error_handler.attempt_recovery(error_context)
        
        if recovery_result['success']:
            return recovery_result['result']
        else:
            # Handle unrecoverable error
            return None

# Periodic Error Summary Generation
def generate_periodic_error_summary():
    """
    Generate and potentially report error summary
    """
    # Get errors from last 24 hours
    yesterday = datetime.now() - timedelta(days=1)
    summary = error_handler.get_error_summary(
        since=yesterday, 
        severity_threshold=ErrorSeverity.WARNING
    )
    
    # Optional: Send summary to monitoring system
    if summary['total_errors'] > 0:
        send_error_report(summary)
```

## Key Features

1. **Comprehensive Error Tracking**
   - Detailed error context capture
   - Severity-based logging
   - Extensible error registry

2. **Intelligent Recovery**
   - Pluggable recovery strategies
   - Automatic error recovery attempts
   - Fallback mechanism support

3. **Advanced Logging**
   - Console and file logging
   - Structured log formatting
   - Configurable log levels

4. **Error Reporting**
   - Detailed error summaries
   - Severity-based filtering
   - Top error type identification

## Error Severity Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General information about system operation
- **WARNING**: Potential issues that don't prevent functionality
- **ERROR**: Significant problems affecting system behavior
- **CRITICAL**: Severe errors that may cause system failure

## Benefits

- **Robustness**: Comprehensive error handling
- **Observability**: Detailed error tracking and reporting
- **Flexibility**: Easily extensible error management
- **Resilience**: Automatic recovery strategies

## Recommended Next Steps

1. Implement more sophisticated recovery strategies
2. Create external error reporting integrations
3. Develop machine learning-based error prediction
4. Add distributed tracing support