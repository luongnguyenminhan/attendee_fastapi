import logging
import traceback
from functools import wraps
from typing import Callable

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.base_model import APIResponse
from app.exceptions.exception import (
    ConflictException,
    CustomHTTPException,
    DatabaseException,
    ExternalServiceException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.middlewares.translation_manager import _

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable) -> Callable:
    """Decorator to handle exceptions in route functions"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            # If result is already APIResponse, return as is
            if isinstance(result, APIResponse):
                return result
            # Otherwise wrap in success response
            return APIResponse.success(data=result)

        except CustomHTTPException as e:
            logger.warning(f"Custom HTTP exception: {e.message}")
            return APIResponse.error(error_code=e.status_code, message=e.message, data=e.detail)

        except HTTPException as e:
            logger.warning(f"HTTP exception: {e.detail}")
            return APIResponse.error(error_code=e.status_code, message=str(e.detail))

        except SQLAlchemyError as e:
            logger.error(f"Database error: {str(e)}")
            return APIResponse.error(
                error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=_("database_error"),
            )

        except ValueError as e:
            logger.warning(f"Value error: {str(e)}")
            return APIResponse.error(error_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message=str(e))

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return APIResponse.error(
                error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=_("internal_server_error"),
            )

    return wrapper


async def custom_http_exception_handler(request: Request, exc: CustomHTTPException) -> JSONResponse:
    """Handle custom HTTP exceptions"""
    logger.warning(f"Custom HTTP exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse.error(
            error_code=exc.status_code,
            message=exc.message,
            data=exc.detail if hasattr(exc, "detail") else None,
        ).dict(),
    )


async def not_found_exception_handler(request: Request, exc: NotFoundException) -> JSONResponse:
    """Handle not found exceptions"""
    logger.warning(f"Not found: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=APIResponse.error(error_code=status.HTTP_404_NOT_FOUND, message=exc.message).dict(),
    )


async def validation_exception_handler(request: Request, exc: ValidationException) -> JSONResponse:
    """Handle validation exceptions"""
    logger.warning(f"Validation error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse.error(error_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message=exc.message).dict(),
    )


async def unauthorized_exception_handler(request: Request, exc: UnauthorizedException) -> JSONResponse:
    """Handle unauthorized exceptions"""
    logger.warning(f"Unauthorized: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=APIResponse.error(error_code=status.HTTP_401_UNAUTHORIZED, message=exc.message).dict(),
    )


async def forbidden_exception_handler(request: Request, exc: ForbiddenException) -> JSONResponse:
    """Handle forbidden exceptions"""
    logger.warning(f"Forbidden: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content=APIResponse.error(error_code=status.HTTP_403_FORBIDDEN, message=exc.message).dict(),
    )


async def conflict_exception_handler(request: Request, exc: ConflictException) -> JSONResponse:
    """Handle conflict exceptions"""
    logger.warning(f"Conflict: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=APIResponse.error(error_code=status.HTTP_409_CONFLICT, message=exc.message).dict(),
    )


async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """Handle database exceptions"""
    logger.error(f"Database error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.error(
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=_("database_error"),
        ).dict(),
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy exceptions"""
    logger.error(f"SQLAlchemy error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.error(
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=_("database_error"),
        ).dict(),
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions"""
    logger.error(f"Unexpected error: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse.error(
            error_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=_("internal_server_error"),
        ).dict(),
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for the FastAPI app"""

    # Custom exception handlers
    app.add_exception_handler(CustomHTTPException, custom_http_exception_handler)
    app.add_exception_handler(NotFoundException, not_found_exception_handler)
    app.add_exception_handler(ValidationException, validation_exception_handler)
    app.add_exception_handler(UnauthorizedException, unauthorized_exception_handler)
    app.add_exception_handler(ForbiddenException, forbidden_exception_handler)
    app.add_exception_handler(ConflictException, conflict_exception_handler)
    app.add_exception_handler(DatabaseException, database_exception_handler)
    app.add_exception_handler(ExternalServiceException, database_exception_handler)

    # SQLAlchemy exception handler
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

    # General exception handler (catch-all)
    app.add_exception_handler(Exception, general_exception_handler)
