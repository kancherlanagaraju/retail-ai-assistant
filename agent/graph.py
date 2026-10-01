"""
LangGraph workflow definition for Retail AI Assistant.
Builds and compiles the state graph with conditional routing.
"""

import logging
from typing import Optional

from langgraph.graph import StateGraph, END
from .state import AgentState
from .nodes import (
    classify_intent_and_sentiment,
    rag_node,
    human_escalation_node,
    route_to_rag_or_escalation
)

logger = logging.getLogger(__name__)


class RetailAgentGraph:
    """LangGraph workflow for Retail AI Assistant."""

    def __init__(self):
        """Initialize and compile the graph."""
        self.graph = None
        self.compiled_graph = None
        self._build_graph()

    def _build_graph(self) -> None:
        """Build the LangGraph state graph."""
        logger.info("Building LangGraph workflow")

        # Create the state graph
        self.graph = StateGraph(AgentState)

        # Add nodes
        logger.info("Adding nodes...")
        self.graph.add_node("classify", classify_intent_and_sentiment)
        self.graph.add_node("rag", rag_node)
        self.graph.add_node("escalate", human_escalation_node)

        # Set entry point
        self.graph.set_entry_point("classify")

        # Add conditional routing from classify node
        logger.info("Adding conditional routing...")
        self.graph.add_conditional_edges(
            "classify",
            route_to_rag_or_escalation,
            {
                "rag_node": "rag",
                "human_escalation": "escalate"
            }
        )

        # Add edges to end node
        self.graph.add_edge("rag", END)
        self.graph.add_edge("escalate", END)

        # Compile the graph
        logger.info("Compiling graph...")
        self.compiled_graph = self.graph.compile()
        logger.info("✓ Graph compiled successfully")

    def invoke(self, state: AgentState) -> AgentState:
        """
        Execute the agent workflow.

        Args:
            state: Initial agent state with query

        Returns:
            Final agent state with response
        """
        logger.info(f"Invoking agent with query: {state.query[:100]}")

        try:
            final_state = self.compiled_graph.invoke(state)
            logger.info("Agent execution completed")
            return final_state

        except Exception as e:
            logger.error(f"Agent execution failed: {str(e)}")
            state.response = "I apologize, but I encountered an error processing your request. A specialist will be in touch shortly."
            state.escalated = True
            return state

    def stream(self, state: AgentState):
        """
        Stream the agent workflow execution for real-time updates.

        Args:
            state: Initial agent state with query

        Yields:
            Intermediate state updates
        """
        logger.info(f"Streaming agent with query: {state.query[:100]}")

        try:
            for output in self.compiled_graph.stream(state):
                yield output

        except Exception as e:
            logger.error(f"Agent streaming failed: {str(e)}")
            state.response = "I apologize, but I encountered an error processing your request."
            yield state


class AgentExecutor:
    """High-level executor for the retail agent."""

    def __init__(self):
        """Initialize the executor with the compiled graph."""
        self.agent_graph = RetailAgentGraph()

    def execute(
        self,
        query: str,
        session_id: str,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Execute the agent for a given query.

        Args:
            query: User query
            session_id: Session identifier
            user_id: Optional user identifier

        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Executing agent for: {query[:100]}")

        # Create initial state
        state = AgentState(
            query=query,
            session_id=session_id,
            user_id=user_id
        )

        # Execute the graph
        final_state = self.agent_graph.invoke(state)

        # Handle both dict and AgentState return types (LangGraph returns dict by default)
        if isinstance(final_state, dict):
            return {
                'response': final_state.get('response', ''),
                'sentiment': final_state.get('sentiment', 'neutral'),
                'department': final_state.get('department', 'Other'),
                'audience': final_state.get('audience', 'external'),
                'escalated': final_state.get('escalated', False),
                'contact_info': final_state.get('user_contact_info', {}),
                'retrieved_docs_count': len(final_state.get('retrieved_docs', [])),
                'metadata': final_state
            }
        else:
            # Handle AgentState object
            return {
                'response': final_state.response,
                'sentiment': final_state.sentiment,
                'department': final_state.department,
                'audience': final_state.audience,
                'escalated': final_state.escalated,
                'contact_info': final_state.user_contact_info,
                'retrieved_docs_count': len(final_state.retrieved_docs),
                'metadata': final_state.to_dict()
            }

    def stream_execute(self, query: str, session_id: str, user_id: Optional[str] = None):
        """
        Stream agent execution for real-time updates.

        Args:
            query: User query
            session_id: Session identifier
            user_id: Optional user identifier

        Yields:
            Execution updates
        """
        state = AgentState(
            query=query,
            session_id=session_id,
            user_id=user_id
        )

        for output in self.agent_graph.stream(state):
            yield output

    def get_graph_structure(self) -> dict:
        """
        Get the structure of the compiled graph for visualization.

        Returns:
            Dictionary describing the graph
        """
        try:
            return {
                'nodes': list(self.agent_graph.graph.nodes.keys()),
                'edges': [
                    {'from': edge[0], 'to': edge[1]}
                    for edge in self.agent_graph.graph.edges
                ]
            }
        except Exception as e:
            logger.error(f"Failed to get graph structure: {str(e)}")
            return {}

    def get_status(self) -> dict:
        """Get the current status of the executor."""
        return {
            'status': 'ready',
            'graph_structure': self.get_graph_structure(),
            'message': 'Agent ready to process queries'
        }


if __name__ == "__main__":
    """Test the agent graph."""
    import uuid

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info("="*70)
    logger.info("TESTING RETAIL AI ASSISTANT AGENT")
    logger.info("="*70)

    executor = AgentExecutor()

    # Test cases
    test_queries = [
        "I'm frustrated because my package hasn't arrived!",  # Should escalate (negative)
        "How do I reset my password?",  # Should go to RAG (IT Support)
        "I need help with something unusual",  # Should escalate (Other)
        "What's the return policy?",  # Should go to RAG (Billing & Payments)
    ]

    for i, query in enumerate(test_queries, 1):
        logger.info(f"\nTest {i}: {query}")
        logger.info("-" * 70)

        result = executor.execute(
            query=query,
            session_id=f"test_{i}_{uuid.uuid4().hex[:8]}",
            user_id="test_user"
        )

        logger.info(f"Sentiment: {result['sentiment']}")
        logger.info(f"Department: {result['department']}")
        logger.info(f"Audience: {result['audience']}")
        logger.info(f"Escalated: {result['escalated']}")
        logger.info(f"Response preview: {result['response'][:100]}...")

    logger.info("\n" + "="*70)
    logger.info("✓ ALL TESTS COMPLETED")
    logger.info("="*70)
