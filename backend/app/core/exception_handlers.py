import logging
import time
import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .logging_config import error_tracker, performance_monitor


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions

    Logs the error and returns a standardized error response
    """
    # Prepare error context
    error_context = {
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host,
    }

    # Log the error
    error_tracker.log_error(error=exc, context=error_context, severity="critical")

    # Generate traceback for detailed logging
    error_traceback = traceback.format_exc()
    logging.error(f"Unhandled exception: {error_traceback}")

    # Return standardized error response
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "error_id": len(error_tracker.error_log),  # Unique error identifier
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handler for HTTP exceptions

    Logs the error and returns appropriate error response
    """
    # Prepare error context
    error_context = {
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host,
        "status_code": exc.status_code,
    }

    # Log the error
    error_tracker.log_error(error=exc, context=error_context, severity="warning")

    # Return HTTP exception response
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


async def validation_exception_handler(request: Request, exc: ValueError):
    """
    Handler for validation exceptions

    Logs validation errors and returns appropriate error response
    """
    # Prepare error context
    error_context = {
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host,
    }

    # Log the validation error
    error_tracker.log_error(error=exc, context=error_context, severity="error")

    # Return validation error response
    return JSONResponse(
        status_code=422, content={"error": "Validation Error", "message": str(exc)}
    )


def add_exception_handlers(app):
    """
    Add exception handlers to the FastAPI application

    Args:
        app (FastAPI): The FastAPI application instance
    """
    app.add_exception_handler(Exception, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(ValueError, validation_exception_handler)


async def performance_middleware(request: Request, call_next):
    """
    Middleware to track request performance

    Measures and logs request processing time
    """
    start_time = time.time()

    try:
        response = await call_next(request)
    except Exception as exc:
        # Ensure performance is tracked even if an exception occurs
        duration = time.time() - start_time
        performance_monitor.track_request(duration=duration, endpoint=request.url.path)
        raise

    # Track request performance
    duration = time.time() - start_time
    performance_monitor.track_request(duration=duration, endpoint=request.url.path)

    return response
