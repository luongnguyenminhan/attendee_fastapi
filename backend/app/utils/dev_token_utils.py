"""
Dev utility for generating auth tokens for testing API endpoints.
TODO: Remove this file in production!
"""
from app.utils.security import create_access_token

def get_dev_auth_token(email: str, user_id: str, organization_id: str = None, expires_in: int = 3600) -> str:
    """Generate a JWT access token for dev/test only."""
    # TODO: Remove this in production!
    data = {
        "sub": email,
        "user_id": user_id,
        "organization_id": organization_id,
    }
    return create_access_token(data=data, expires_delta=expires_in)
