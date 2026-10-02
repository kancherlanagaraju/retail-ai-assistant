"""
FastAPI web application for Retail AI Assistant.
Provides REST endpoints for agent interaction.
"""

import logging
import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from agent.graph import AgentExecutor
from auth.jwt_handler import create_access_token
from auth.dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="Retail AI Assistant API",
    description="Enterprise AI assistant for retail operations",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please wait before making more requests.",
            "retry_after": exc.detail if hasattr(exc, 'detail') else "Check Rate-Limit-Reset header"
        }
    )

# Configure CORS with security in mind
# Read allowed origins from environment variable or use sensible defaults
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",")]

logger.info(f"CORS allowed origins: {allowed_origins}")

# Add CORS middleware with restricted settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Only allow specific origins (not "*")
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Only allow necessary methods
    allow_headers=["Content-Type", "Authorization"],  # Only allow necessary headers
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Initialize agent executor
agent_executor = AgentExecutor()


# Startup event to initialize vector store
@app.on_event("startup")
async def startup_event():
    """Initialize vector store on application startup."""
    try:
        from pathlib import Path
        db_path = Path("./vectorstore/chroma_db")

        # Check if vector store has documents
        from vectorstore.db_builder import VectorStoreBuilder, initialize_and_populate_vectorstore

        needs_initialization = True
        if db_path.exists():
            try:
                builder = VectorStoreBuilder()
                stats = builder.get_collection_stats()
                if stats.get('total_documents', 0) > 0:
                    logger.info(f"Vector store initialized with {stats['total_documents']} documents")
                    needs_initialization = False
            except Exception:
                pass

        if needs_initialization:
            logger.info("Vector store empty or missing. Initializing...")
            initialize_and_populate_vectorstore()
            logger.info("Vector store initialized on startup")
    except Exception as e:
        logger.warning(f"Vector store initialization skipped: {str(e)}")
        # Continue anyway - app can still work with mock data


# Request/Response models
class UserInfo(BaseModel):
    """User information for the request."""
    name: Optional[str] = None
    email: Optional[str] = None
    user_id: Optional[str] = None


class ChatRequest(BaseModel):
    """Chat request model."""
    query: str = Field(..., min_length=1, max_length=5000, description="User query")
    user_info: Optional[UserInfo] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response model."""
    response: str
    sentiment: Optional[str]
    department: Optional[str]
    escalated: bool
    session_id: str
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)


# Authentication models
class LoginRequest(BaseModel):
    """Login request with user credentials."""
    user_id: str = Field(..., min_length=1, description="Unique user identifier")
    password: Optional[str] = Field(None, description="Optional password (not validated in MVP)")


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str


# Configure rate limits from environment variables
CHAT_RATE_LIMIT = os.getenv("CHAT_RATE_LIMIT", "10/minute")
ESCALATION_RATE_LIMIT = os.getenv("ESCALATION_RATE_LIMIT", "30/minute")
HEALTH_RATE_LIMIT = os.getenv("HEALTH_RATE_LIMIT", "100/minute")
STATUS_RATE_LIMIT = os.getenv("STATUS_RATE_LIMIT", "30/minute")

logger.info(f"Rate limits configured: chat={CHAT_RATE_LIMIT}, escalation={ESCALATION_RATE_LIMIT}, health={HEALTH_RATE_LIMIT}, status={STATUS_RATE_LIMIT}")

# Endpoints
@app.get("/", tags=["root"])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Retail AI Assistant API",
        "docs": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", response_model=HealthResponse, tags=["health"])
@limiter.limit(HEALTH_RATE_LIMIT)
async def health(request: Request) -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.post("/login", response_model=TokenResponse, tags=["auth"])
async def login(login_request: LoginRequest) -> TokenResponse:
    """
    Login endpoint to get JWT access token.

    In this MVP, any user_id is accepted (no password validation).
    In production, integrate with proper authentication system.

    Args:
        login_request: User credentials (user_id required)

    Returns:
        JWT access token for subsequent API calls
    """
    try:
        user_id = login_request.user_id.strip()
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="user_id cannot be empty"
            )

        # Create JWT token
        token = create_access_token(user_id=user_id)

        logger.info(f"User logged in: {user_id}")

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24 hours in seconds
            user_id=user_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Login failed"
        )


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
@limiter.limit(CHAT_RATE_LIMIT)
async def chat(request: Request, chat_request: ChatRequest, authorization: Optional[str] = None) -> ChatResponse:
    """
    Process a user query through the agent.

    Authentication is optional for MVP (for backward compatibility).
    In production, set REQUIRE_AUTH=true to enforce authentication.

    Args:
        request: FastAPI request object
        chat_request: Chat request with query and optional user info
        authorization: Optional Bearer token for authentication

    Returns:
        ChatResponse with agent's response and metadata
    """
    try:
        # Optional authentication
        require_auth = os.getenv("REQUIRE_AUTH", "false").lower() == "true"
        authenticated_user_id = None

        if authorization:
            try:
                current_user = await get_current_user(authorization=authorization)
                authenticated_user_id = current_user.get("user_id")
                logger.info(f"Authenticated request from user: {authenticated_user_id}")
            except HTTPException:
                if require_auth:
                    raise
                logger.warning("Invalid authentication provided, continuing as unauthenticated")
        elif require_auth:
            raise HTTPException(
                status_code=401,
                detail="Authentication required. Please login first.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Generate session ID if not provided
        session_id = chat_request.session_id or str(uuid.uuid4())
        user_id = authenticated_user_id or (chat_request.user_info.user_id if chat_request.user_info else None)

        logger.info(f"Processing query from session {session_id}: {chat_request.query[:100]} (user: {user_id})")

        # Execute the agent
        result = agent_executor.execute(
            query=chat_request.query,
            session_id=session_id,
            user_id=user_id
        )

        logger.info(f"Query processed. Sentiment: {result['sentiment']}, Department: {result['department']}")

        return ChatResponse(
            response=result['response'],
            sentiment=result['sentiment'],
            department=result['department'],
            escalated=result['escalated'],
            session_id=session_id
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )


@app.post("/escalation", tags=["escalation"])
@limiter.limit(ESCALATION_RATE_LIMIT)
async def submit_escalation(request: Request, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Submit an escalation ticket with user contact information.

    Args:
        data: Dictionary with name, email, phone, and query details

    Returns:
        Ticket confirmation with ID and SLA
    """
    try:
        import uuid as uuid_module

        ticket_id = f"TKT-{uuid_module.uuid4().hex[:8].upper()}"

        logger.info(f"""
        ╔════════════════════════════════════════════════════════════════════╗
        ║               ESCALATION TICKET RECEIPT                           ║
        ╠════════════════════════════════════════════════════════════════════╣
        ║ Ticket ID:        {ticket_id}
        ║ Timestamp:        {datetime.now().isoformat()}
        ║ Department:       {data.get('department', 'Unspecified')}
        ║ Customer Name:    {data.get('name', 'Not provided')}
        ║ Email:            {data.get('email', 'Not provided')}
        ║ Phone:            {data.get('phone', 'Not provided')}
        ║ Status:           CREATED
        ║ SLA:              24 hours
        ╚════════════════════════════════════════════════════════════════════╝
        """)

        return {
            'ticket_id': ticket_id,
            'status': 'created',
            'timestamp': datetime.now().isoformat(),
            'message': f'Escalation ticket created. Confirmation email sent to {data.get("email")}',
            'sla_hours': 24
        }

    except Exception as e:
        logger.error(f"Error submitting escalation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting escalation: {str(e)}"
        )


@app.get("/agent/status", tags=["agent"])
@limiter.limit(STATUS_RATE_LIMIT)
async def agent_status(request: Request) -> Dict[str, Any]:
    """Get agent status and configuration."""
    return agent_executor.get_status()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
