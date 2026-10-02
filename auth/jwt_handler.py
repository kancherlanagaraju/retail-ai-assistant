"""JWT token handling for authentication."""

import os
import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Get JWT secret from environment or use default (change in production!)
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def create_access_token(user_id: str, user_data: Optional[Dict[str, Any]] = None) -> str:
    """
    Create a JWT access token.

    Args:
        user_id: User identifier
        user_data: Optional additional user data to include in token

    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow(),
    }

    if user_data:
        payload.update(user_data)

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    logger.info(f"Access token created for user: {user_id}")
    return token


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token to verify

    Returns:
        Decoded token payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        logger.debug(f"Token verified for user: {payload.get('user_id')}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None


def extract_token_from_header(authorization_header: str) -> Optional[str]:
    """
    Extract JWT token from Authorization header.

    Expected format: "Bearer <token>"

    Args:
        authorization_header: Authorization header value

    Returns:
        Token string if valid format, None otherwise
    """
    if not authorization_header:
        return None

    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None

    return parts[1]
