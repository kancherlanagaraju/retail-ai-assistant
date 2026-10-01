"""
FastAPI web application for Retail AI Assistant.
Provides REST endpoints for agent interaction.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from agent.graph import AgentExecutor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Retail AI Assistant API",
    description="Enterprise AI assistant for retail operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

        # Check if vector store needs initialization
        if not db_path.exists() or not list(db_path.glob("*")):
            logger.info("Vector store not found. Initializing...")
            from vectorstore.db_builder import initialize_and_populate_vectorstore
            initialize_and_populate_vectorstore()
            logger.info("✓ Vector store initialized on startup")
        else:
            logger.info("✓ Vector store already initialized")
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
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.post("/chat", response_model=ChatResponse, tags=["chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a user query through the agent.

    Args:
        request: Chat request with query and optional user info

    Returns:
        ChatResponse with agent's response and metadata
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        user_id = request.user_info.user_id if request.user_info else None

        logger.info(f"Processing query from session {session_id}: {request.query[:100]}")

        # Execute the agent
        result = agent_executor.execute(
            query=request.query,
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
async def submit_escalation(data: Dict[str, Any]) -> Dict[str, Any]:
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
async def agent_status() -> Dict[str, Any]:
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
