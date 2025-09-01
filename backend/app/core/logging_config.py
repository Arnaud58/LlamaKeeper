import json
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler

import structlog


def configure_logging():
    """
    Configure comprehensive logging system with structured logging

    Supports:
    - Console logging
    - File logging with rotation
    - Structured JSON logging
    - Different log levels
    """
    # Configure standard logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            RotatingFileHandler(
                "app.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB
            ),
        ],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add log level
            structlog.processors.add_log_level,
            # Format as JSON
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class ErrorTracker:
    """
    Centralized error tracking and monitoring system
    """

    def __init__(self):
        self.logger = structlog.get_logger()
        self.error_count = 0
        self.error_log = []

    def log_error(
        self, error: Exception, context: dict = None, severity: str = "error"
    ):
        """
        Log an error with comprehensive details

        Args:
            error (Exception): The error to log
            context (dict, optional): Additional context about the error
            severity (str, optional): Error severity level
        """
        self.error_count += 1

        error_details = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "severity": severity,
            "context": context or {},
        }

        self.error_log.append(error_details)

        # Log using structlog
        self.logger.error("Error occurred", error=error_details)

    def get_error_summary(self) -> dict:
        """
        Generate a summary of errors

        Returns:
            dict: Error summary statistics
        """
        return {
            "total_errors": self.error_count,
            "recent_errors": self.error_log[-10:],  # Last 10 errors
            "error_types": self._count_error_types(),
        }

    def _count_error_types(self) -> dict:
        """
        Count occurrences of different error types

        Returns:
            dict: Error type counts
        """
        error_types = {}
        for error in self.error_log:
            error_type = error["error_type"]
            error_types[error_type] = error_types.get(error_type, 0) + 1
        return error_types


class PerformanceMonitor:
    """
    Performance monitoring for tracking system performance
    """

    def __init__(self):
        self.logger = structlog.get_logger()
        self.request_times = []
        self.max_tracked_requests = 100

    def track_request(self, duration: float, endpoint: str):
        """
        Track request performance

        Args:
            duration (float): Request processing time in seconds
            endpoint (str): API endpoint
        """
        request_data = {
            "endpoint": endpoint,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.request_times.append(request_data)

        # Limit tracked requests
        if len(self.request_times) > self.max_tracked_requests:
            self.request_times = self.request_times[-self.max_tracked_requests :]

        # Log slow requests
        if duration > 1.0:  # Threshold for slow requests
            self.logger.warning("Slow request detected", request=request_data)

    def get_performance_summary(self) -> dict:
        """
        Generate performance summary

        Returns:
            dict: Performance metrics
        """
        if not self.request_times:
            return {"total_requests": 0}

        durations = [req["duration"] for req in self.request_times]

        return {
            "total_requests": len(self.request_times),
            "avg_response_time": sum(durations) / len(durations),
            "max_response_time": max(durations),
            "min_response_time": min(durations),
            "recent_slow_requests": [
                req for req in self.request_times if req["duration"] > 1.0
            ],
        }


# Global error tracker and performance monitor
error_tracker = ErrorTracker()
performance_monitor = PerformanceMonitor()
