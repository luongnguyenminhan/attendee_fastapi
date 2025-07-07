from typing import Optional, Any
from fastapi import HTTPException, status


class CustomHTTPException(HTTPException):
    """Base custom HTTP exception"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status_code, detail={"message": message, "detail": detail}
        )
        self.message = message


class NotFoundException(CustomHTTPException):
    """Exception raised when a resource is not found"""

    def __init__(
        self, message: str = "Resource not found", detail: Optional[Any] = None
    ):
        super().__init__(
            message=message, status_code=status.HTTP_404_NOT_FOUND, detail=detail
        )


class ValidationException(CustomHTTPException):
    """Exception raised when validation fails"""

    def __init__(
        self, message: str = "Validation failed", detail: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
        )


class UnauthorizedException(CustomHTTPException):
    """Exception raised when user is not authenticated"""

    def __init__(
        self, message: str = "Unauthorized access", detail: Optional[Any] = None
    ):
        super().__init__(
            message=message, status_code=status.HTTP_401_UNAUTHORIZED, detail=detail
        )


class ForbiddenException(CustomHTTPException):
    """Exception raised when user doesn't have permission"""

    def __init__(self, message: str = "Access forbidden", detail: Optional[Any] = None):
        super().__init__(
            message=message, status_code=status.HTTP_403_FORBIDDEN, detail=detail
        )


class ConflictException(CustomHTTPException):
    """Exception raised when there's a conflict with current state"""

    def __init__(self, message: str = "Conflict", detail: Optional[Any] = None):
        super().__init__(
            message=message, status_code=status.HTTP_409_CONFLICT, detail=detail
        )


class BadRequestException(CustomHTTPException):
    """Exception raised for bad requests"""

    def __init__(self, message: str = "Bad request", detail: Optional[Any] = None):
        super().__init__(
            message=message, status_code=status.HTTP_400_BAD_REQUEST, detail=detail
        )


class InternalServerException(CustomHTTPException):
    """Exception raised for internal server errors"""

    def __init__(
        self, message: str = "Internal server error", detail: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class DatabaseException(CustomHTTPException):
    """Exception raised for database errors"""

    def __init__(self, message: str = "Database error", detail: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
        )


class ExternalServiceException(CustomHTTPException):
    """Exception raised for external service errors"""

    def __init__(
        self, message: str = "External service error", detail: Optional[Any] = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
        )
