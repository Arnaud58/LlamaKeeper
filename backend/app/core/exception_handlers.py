import logging
import time
import traceback

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .logging_config import error_tracker


async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions

    Logs the error and returns a standardized error response
    """
    # Prepare error context
    error_context = {
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host if request.client else "Unknown",
        "exception_type": type(exc).__name__,
    }

    # Determine appropriate status code and error message
    if isinstance(exc, HTTPException):
        # HTTPException is already handled by http_exception_handler
        raise exc
    elif isinstance(exc, ValueError):
        status_code = 422  # Unprocessable Entity
        error_message = f"Validation Error: {str(exc)}"
    elif isinstance(exc, PermissionError):
        status_code = 403  # Forbidden
        error_message = f"Permission Denied: {str(exc)}"
    else:
        status_code = 500  # Internal Server Error
        error_message = f"Unhandled Exception: {str(exc)}"

    # Log the error
    error_tracker.log_error(error_message, context=error_context)

    # Generate traceback for detailed logging
    error_traceback = traceback.format_exc()
    logging.error(f"Unhandled exception: {error_traceback}")

    # Return standardized error response
    return JSONResponse(
        status_code=status_code,
        content={
            "error": "Internal Server Error" if status_code == 500 else "Error",
            "message": error_message,
            "error_type": type(exc).__name__,
            "error_id": error_tracker.error_count,  # Unique error identifier
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
        "client": request.client.host if request.client else "Unknown",
        "status_code": exc.status_code,
    }

    # Log the error
    error_tracker.log_error(
        f"HTTP {exc.status_code} Error: {exc.detail}",
        context=error_context
    )

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
        "client": request.client.host if request.client else "Unknown",
    }

    # Log the validation error
    error_tracker.log_error(
        f"Validation Error: {str(exc)}",
        context=error_context
    )

    # Return validation error response
    return JSONResponse(
        status_code=422,
        content={"error": "Validation Error", "message": str(exc)}
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
        # Log performance even if an exception occurs
        duration = time.time() - start_time
        logging.info(f"Request to {request.url.path} took {duration:.4f} seconds (with exception)")
        raise

    # Log request performance
    duration = time.time() - start_time
    logging.info(f"Request to {request.url.path} took {duration:.4f} seconds")

    return response
