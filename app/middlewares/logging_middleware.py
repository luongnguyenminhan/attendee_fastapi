import time
import logging
from typing import Callable
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware to log request details and response time"""

    # Generate unique request ID
    request_id = str(uuid.uuid4())

    # Start timing
    start_time = time.time()

    # Log request start
    logger.info(
        f"Request {request_id} started: {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Add request ID to request state for access in routes
    request.state.request_id = request_id

    try:
        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)

        # Log successful response
        logger.info(
            f"Request {request_id} completed: {response.status_code} "
            f"in {process_time:.3f}s"
        )

        return response

    except Exception as e:
        # Calculate processing time
        process_time = time.time() - start_time

        # Log error
        logger.error(
            f"Request {request_id} failed: {str(e)} " f"after {process_time:.3f}s"
        )

        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error_code": 500,
                "message": "Internal server error",
                "request_id": request_id,
            },
            headers={"X-Request-ID": request_id},
        )


def setup_logging_middleware(app):
    """Setup logging middleware for the FastAPI app"""
    app.middleware("http")(logging_middleware)
