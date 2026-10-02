"""FastAPI dependencies for authentication."""

import logging
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status, Header

from auth.jwt_handler import verify_token, extract_token_from_header

logger = logging.getLogger(__name__)


async def get_current_user(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """
    Dependency to verify JWT token and extract current user.

    Args:
        authorization: Authorization header (automatically injected by FastAPI)

    Returns:
        Decoded token payload containing user information

    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = extract_token_from_header(authorization)
    if not token:
        logger.warning("Invalid Authorization header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Use: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = verify_token(token)
    if not payload:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if not user_id:
        logger.warning("User ID not found in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: user_id not found",
        )

    logger.debug(f"User authenticated: {user_id}")
    return payload
