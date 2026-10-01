"""
Node implementations for LangGraph agent workflow.
Each node handles a specific step in the processing pipeline.
"""

import logging
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from agent.state import AgentState, Sentiment, Department

logger = logging.getLogger(__name__)

# Try to import LLMs, with fallbacks
try:
    from langchain_openai import ChatOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from langchain_anthropic import ChatAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ClassificationOutput(BaseModel):
    """Structured output for intent and sentiment classification."""
    sentiment: str = Field(
        description="Sentiment of the query: 'positive', 'neutral', or 'negative'"
    )
    department: str = Field(
        description="Department classification: 'HR', 'IT Support', 'Billing & Payments', 'Shipping & Delivery', or 'Other'"
    )
    audience: str = Field(
        description="Target audience: 'internal' for employees or 'external' for customers"
    )
    reasoning: str = Field(
        description="Brief explanation of the classification"
    )


def get_llm():
    """Get the best available LLM."""
    import os

    # Try Claude first (usually more reliable for structured output)
    if ANTHROPIC_AVAILABLE and os.getenv("ANTHROPIC_API_KEY"):
        logger.info("Using Claude Sonnet 3.5 for LLM calls")
        return ChatAnthropic(model="claude-3-5-sonnet-20241022")

    # Fall back to OpenAI if available
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        logger.info("Using GPT-4o for LLM calls")
        return ChatOpenAI(model="gpt-4o", temperature=0.3)

    # Fallback: use a mock LLM
    logger.warning("No LLM API keys available, using mock LLM")
    return None


def classify_intent_and_sentiment(state: AgentState) -> AgentState:
    """
    Classify user query for sentiment and department using LLM with structured output.

    Args:
        state: Current agent state with the query

    Returns:
        Updated state with sentiment, department, and audience
    """
    logger.info(f"Classifying query: {state.query[:100]}")

    try:
        # Get LLM
        llm = get_llm()

        if llm is None:
            # Mock classification
            logger.warning("Using mock classification (no LLM available)")
            classification = _mock_classify(state.query)
        else:
            # Use LLM with structured output
            classification_prompt = f"""
Analyze the following customer query and classify it:

Query: {state.query}

Classify the query into:
1. Sentiment: positive (happy/satisfied), neutral (informational), or negative (frustrated/angry)
2. Department: HR, IT Support, Billing & Payments, Shipping & Delivery, or Other
3. Audience: internal (employee) or external (customer)

Provide structured output with sentiment, department, audience, and a brief reasoning.
"""

            # Create prompt with structured output
            from langchain_core.messages import HumanMessage

            message = HumanMessage(content=classification_prompt)

            # Try to get structured output
            try:
                # Use with_structured_output if available
                if hasattr(llm, 'with_structured_output'):
                    structured_llm = llm.with_structured_output(ClassificationOutput)
                    response = structured_llm.invoke([message])
                    classification = {
                        'sentiment': response.sentiment,
                        'department': response.department,
                        'audience': response.audience,
                        'reasoning': response.reasoning
                    }
                else:
                    # Fallback to parsing JSON from response
                    response = llm.invoke([message])
                    response_text = response.content if hasattr(response, 'content') else str(response)

                    # Try to extract JSON
                    try:
                        # Look for JSON in the response
                        import re
                        json_match = re.search(r'\{[^{}]*\}', response_text)
                        if json_match:
                            classification = json.loads(json_match.group())
                        else:
                            classification = _mock_classify(state.query)
                    except:
                        classification = _mock_classify(state.query)
            except Exception as e:
                logger.warning(f"Structured output failed, using mock: {str(e)}")
                classification = _mock_classify(state.query)

        # Update state with classification results
        state.sentiment = classification.get('sentiment', 'neutral')
        state.department = classification.get('department', 'Other')
        state.audience = classification.get('audience', 'external')

        state.add_message("system", f"Classified as: {state.department} ({state.sentiment} sentiment)")
        logger.info(f"Classification: dept={state.department}, sentiment={state.sentiment}, audience={state.audience}")

        return state

    except Exception as e:
        logger.error(f"Classification failed: {str(e)}")
        state.sentiment = "neutral"
        state.department = "Other"
        state.audience = "external"
        return state


def _mock_classify(query: str) -> Dict[str, str]:
    """
    Mock classification based on keywords when LLM is not available.

    Args:
        query: User query to classify

    Returns:
        Classification dictionary
    """
    query_lower = query.lower()

    # Sentiment classification - expanded keywords
    negative_words = ['angry', 'furious', 'terrible', 'horrible', 'hate', 'worst', 'frustrated', 'disappointed', 'upset', 'annoyed']
    positive_words = ['thank', 'great', 'excellent', 'perfect', 'love', 'happy', 'good', 'satisfied']

    if any(word in query_lower for word in negative_words):
        sentiment = 'negative'
    elif any(word in query_lower for word in positive_words):
        sentiment = 'positive'
    else:
        sentiment = 'neutral'

    # Department classification - check in priority order
    # Check Billing first (payment-related terms take priority)
    if any(word in query_lower for word in ['refund', 'payment', 'bill', 'invoice', 'credit', 'subscription', 'charge']):
        department = 'Billing & Payments'
    # Check HR
    elif any(word in query_lower for word in ['vacation', 'leave', 'benefits', 'hr', 'payroll', 'onboarding', 'employee discount']):
        department = 'HR'
    # Check IT Support (be more specific to avoid false matches like "with")
    elif any(word in query_lower for word in ['password', 'vpn', 'email', 'laptop', 'printer', 'software', 'reset', 'login', 'it support', 'it help']):
        department = 'IT Support'
    # Check Shipping (last to avoid false matches)
    elif any(word in query_lower for word in ['ship', 'delivery', 'tracking', 'package', 'order', 'arrival', 'deliver']):
        department = 'Shipping & Delivery'
    else:
        department = 'Other'

    # Audience classification
    audience = 'internal' if any(word in query_lower for word in ['employee', 'staff', 'office', 'colleague']) else 'external'

    return {
        'sentiment': sentiment,
        'department': department,
        'audience': audience,
        'reasoning': 'Mock classification based on keywords'
    }


def rag_node(state: AgentState) -> AgentState:
    """
    Retrieve relevant documents from ChromaDB and generate answer using RAG.

    Args:
        state: Current agent state with classification results

    Returns:
        Updated state with retrieved docs and response
    """
    logger.info(f"RAG retrieval for department: {state.department}")

    try:
        # Import vector store builder
        from vectorstore.db_builder import VectorStoreBuilder

        # Initialize vector store
        builder = VectorStoreBuilder()

        # Retrieve documents with category filter
        state.retrieved_docs = builder.search(
            query=state.query,
            category=state.department if state.department != 'Other' else None,
            k=5
        )

        logger.info(f"Retrieved {len(state.retrieved_docs)} documents")

        # Generate response based on retrieved documents
        if state.retrieved_docs:
            # Format retrieved documents
            doc_context = "\n\n".join([
                f"[{doc['metadata']['category']}] {doc['content']}"
                for doc in state.retrieved_docs[:3]
            ])

            response_prompt = f"""Based on the following information, provide a helpful answer to the customer query.

Query: {state.query}

Context:
{doc_context}

Please provide a clear, concise answer that directly addresses the query using the provided context.
If the context doesn't fully address the query, acknowledge that and suggest next steps."""

            # Get LLM
            llm = get_llm()

            if llm:
                from langchain_core.messages import HumanMessage
                message = HumanMessage(content=response_prompt)
                response = llm.invoke([message])
                state.response = response.content if hasattr(response, 'content') else str(response)
            else:
                # Generate mock response
                state.response = f"Based on our records, here's information about {state.department}:\n\n"
                for doc in state.retrieved_docs[:2]:
                    state.response += f"• {doc['content'][:150]}...\n\n"
                state.response += "Is there anything else you'd like to know?"
        else:
            # No documents found
            state.response = f"I couldn't find specific information about your query in our {state.department} knowledge base. "
            state.response += "A human specialist will be able to help you better."
            state.escalated = True

        state.add_message("assistant", state.response)
        logger.info("RAG response generated")

        return state

    except Exception as e:
        logger.error(f"RAG node failed: {str(e)}")
        state.response = "I apologize, but I encountered an issue processing your request. A specialist will contact you shortly."
        state.escalated = True
        return state


def human_escalation_node(state: AgentState) -> AgentState:
    """
    Handle human escalation when sentiment is negative or department is unknown.
    Collects contact information for follow-up.

    Args:
        state: Current agent state

    Returns:
        Updated state with escalation details and contact info
    """
    logger.info("Escalating to human support")

    state.escalated = True

    # Generate escalation message
    if state.sentiment == 'negative':
        reason = "We noticed you may be frustrated with your experience, and we want to make sure we help properly."
    else:
        reason = "Your query requires specialized attention from our support team."

    escalation_message = f"""
I appreciate you reaching out. {reason}

A member of our {state.department} support team will contact you within 24 hours to assist you personally.

To help us serve you better, please provide:
- Name: [Your Name]
- Email: [Your Email Address]
- Phone: [Your Contact Number]

We're committed to resolving your issue quickly. Thank you for your patience!
"""

    state.response = escalation_message

    # Mock collection of contact info
    state.user_contact_info = {
        'name': 'Customer',
        'email': 'customer@example.com',
        'phone': '+1-555-0100',
        'department': state.department,
        'sentiment': state.sentiment,
        'original_query': state.query
    }

    state.add_message("assistant", state.response)
    state.add_message("system", f"Escalated to human support. Contact info: {state.user_contact_info}")

    logger.info(f"Escalated with contact info: {state.user_contact_info}")

    return state


def route_to_rag_or_escalation(state: AgentState) -> str:
    """
    Determine whether to proceed with RAG or escalate to human.

    Escalate if:
    - Sentiment is negative
    - Department is 'Other'

    Args:
        state: Current agent state

    Returns:
        Node name: either "rag_node" or "human_escalation"
    """
    logger.info(f"Routing: sentiment={state.sentiment}, department={state.department}")

    # Check if should escalate
    if state.sentiment == 'negative' or state.department == 'Other':
        logger.info("Routing to human escalation")
        return "human_escalation"
    else:
        logger.info("Routing to RAG node")
        return "rag_node"
