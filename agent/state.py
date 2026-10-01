"""
Agent state definition for Retail AI Assistant using LangGraph.
Defines the state schema for the agentic workflow.
"""

from typing import Optional, List, Dict, Any, Literal
from dataclasses import dataclass, field
from enum import Enum


class Sentiment(str, Enum):
    """Sentiment classification."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class Department(str, Enum):
    """Department categories."""
    HR = "HR"
    IT_SUPPORT = "IT Support"
    BILLING_PAYMENTS = "Billing & Payments"
    SHIPPING_DELIVERY = "Shipping & Delivery"
    OTHER = "Other"


class Audience(str, Enum):
    """User audience type."""
    INTERNAL = "internal"
    EXTERNAL = "external"


@dataclass
class AgentState:
    """
    State definition for LangGraph workflow.
    Contains all information needed throughout the agent's processing pipeline.
    """

    # Input
    query: str

    # Classification results
    sentiment: Optional[str] = None  # 'positive', 'neutral', 'negative'
    department: Optional[str] = None  # Department classification
    audience: Optional[str] = None  # 'internal' or 'external'

    # Retrieved context
    retrieved_docs: List[Dict[str, Any]] = field(default_factory=list)

    # Output
    response: str = ""

    # Escalation
    escalated: bool = False
    user_contact_info: Optional[Dict[str, str]] = None  # Name, Email, Phone

    # Metadata
    session_id: str = ""
    user_id: Optional[str] = None
    messages: List[Dict[str, str]] = field(default_factory=list)

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        self.messages.append({"role": role, "content": content})

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            'query': self.query,
            'sentiment': self.sentiment,
            'department': self.department,
            'audience': self.audience,
            'response': self.response,
            'escalated': self.escalated,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'retrieved_docs_count': len(self.retrieved_docs),
            'messages_count': len(self.messages),
        }
