import jwt
from typing import Optional, List
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse

from app.core.base_model import APIResponse
from app.exceptions.exception import UnauthorizedException
from app.middlewares.translation_manager import _


class AuthMiddleware:
    """Authentication middleware for JWT token validation"""

    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.security = HTTPBearer()

    async def __call__(self, request: Request, call_next):
        """Middleware function to validate JWT tokens"""

        # Skip auth for certain paths
        skip_paths = [
            "/docs",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/register",
            "/auth/refresh",
        ]

        if request.url.path in skip_paths or request.url.path.startswith("/docs"):
            return await call_next(request)

        # Get authorization header
        authorization = request.headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=APIResponse.error(
                    error_code=status.HTTP_401_UNAUTHORIZED, message=_("unauthorized")
                ).dict(),
            )

        try:
            # Extract token
            token = authorization.split(" ")[1]

            # Decode and validate token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Add user info to request state
            request.state.user_id = payload.get("user_id")
            request.state.email = payload.get("email")
            request.state.organization_id = payload.get("organization_id")

            return await call_next(request)

        except jwt.ExpiredSignatureError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=APIResponse.error(
                    error_code=status.HTTP_401_UNAUTHORIZED, message=_("token_expired")
                ).dict(),
            )
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=APIResponse.error(
                    error_code=status.HTTP_401_UNAUTHORIZED, message=_("invalid_token")
                ).dict(),
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=APIResponse.error(
                    error_code=status.HTTP_401_UNAUTHORIZED, message=_("unauthorized")
                ).dict(),
            )


def setup_auth_middleware(app, secret_key: str):
    """Setup authentication middleware for the FastAPI app"""
    auth_middleware = AuthMiddleware(secret_key)
    app.middleware("http")(auth_middleware)
