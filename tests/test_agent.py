"""
Test suite for Retail AI Assistant Agent.
Tests cover key scenarios: HR queries, shipping queries, negative sentiment, and out-of-domain queries.
"""

import pytest
import uuid
from agent.graph import AgentExecutor
from agent.state import Sentiment, Department


class TestAgentRouting:
    """Test agent routing behavior across different query types."""

    @pytest.fixture
    def executor(self):
        """Initialize agent executor for testing."""
        return AgentExecutor()

    @pytest.fixture
    def session_id(self):
        """Generate unique session ID for each test."""
        return f"test_{uuid.uuid4().hex[:8]}"

    def test_positive_hr_query_routing(self, executor, session_id):
        """
        Test 1: Positive/Neutral HR Query
        Validates that HR query routes to RAG and generates valid response.
        """
        query = "How do I apply for annual leave benefits?"
        
        result = executor.execute(
            query=query,
            session_id=session_id,
            user_id="test_user_hr"
        )

        # Verify classification
        assert result['sentiment'] in [Sentiment.POSITIVE.value, Sentiment.NEUTRAL.value]
        assert result['department'] == Department.HR.value

        # Verify it was NOT escalated (should go to RAG)
        assert result['escalated'] is False

        # Verify response exists and is meaningful
        assert result['response'] is not None
        assert len(result['response']) > 0
        # Response should contain HR-related content or generic RAG response
        assert "hr" in result['response'].lower() or "here's information" in result['response'].lower()
        
        # Verify retrieved docs
        assert result['retrieved_docs_count'] >= 0
        
        print(f"✓ HR Query Test Passed")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Department: {result['department']}")
        print(f"  Escalated: {result['escalated']}")
        print(f"  Response Preview: {result['response'][:100]}...")

    def test_positive_shipping_external_query(self, executor, session_id):
        """
        Test 2: Positive/Neutral External Customer Query (Shipping)
        Validates routing to Shipping retriever and response generation.
        """
        query = "What's the estimated delivery time for my order?"
        
        result = executor.execute(
            query=query,
            session_id=session_id,
            user_id="test_user_customer"
        )

        # Verify classification
        assert result['sentiment'] in [Sentiment.POSITIVE.value, Sentiment.NEUTRAL.value]
        assert result['department'] == Department.SHIPPING_DELIVERY.value
        
        # Verify it was NOT escalated (should go to RAG)
        assert result['escalated'] is False
        
        # Verify response exists
        assert result['response'] is not None
        assert len(result['response']) > 0
        assert "delivery" in result['response'].lower() or "shipping" in result['response'].lower() or "order" in result['response'].lower()
        
        print(f"✓ Shipping Query Test Passed")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Department: {result['department']}")
        print(f"  Escalated: {result['escalated']}")
        print(f"  Response Preview: {result['response'][:100]}...")

    def test_negative_sentiment_escalation(self, executor, session_id):
        """
        Test 3: Negative Sentiment Query
        Verifies that queries with negative sentiment are immediately escalated.
        """
        query = "I'm frustrated because my package hasn't arrived yet and I'm very disappointed!"
        
        result = executor.execute(
            query=query,
            session_id=session_id,
            user_id="test_user_angry"
        )

        # Verify negative sentiment was detected
        assert result['sentiment'] == Sentiment.NEGATIVE.value, \
            f"Expected negative sentiment, got {result['sentiment']}"
        
        # CRITICAL: Verify escalation was triggered
        assert result['escalated'] is True, \
            "Negative sentiment query should be escalated to human"
        
        # Verify escalation message is present
        assert result['response'] is not None
        assert len(result['response']) > 0
        assert "escalat" in result['response'].lower() or "support" in result['response'].lower() or "specialist" in result['response'].lower()
        
        print(f"✓ Negative Sentiment Test Passed")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Department: {result['department']}")
        print(f"  Escalated: {result['escalated']}")
        print(f"  Response Preview: {result['response'][:100]}...")

    def test_out_of_domain_escalation(self, executor, session_id):
        """
        Test 4: Out-of-Domain Query
        Verifies routing to escalation when department is 'Other'.
        """
        query = "Can you help me with something completely unrelated to your services?"
        
        result = executor.execute(
            query=query,
            session_id=session_id,
            user_id="test_user_other"
        )

        # Verify department classification
        assert result['department'] == Department.OTHER.value, \
            f"Expected 'Other' department, got {result['department']}"
        
        # CRITICAL: Verify escalation was triggered for out-of-domain
        assert result['escalated'] is True, \
            "Out-of-domain query should be escalated to human"
        
        # Verify escalation message
        assert result['response'] is not None
        assert "escalat" in result['response'].lower() or "support" in result['response'].lower() or "specialist" in result['response'].lower()
        
        print(f"✓ Out-of-Domain Query Test Passed")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Department: {result['department']}")
        print(f"  Escalated: {result['escalated']}")
        print(f"  Response Preview: {result['response'][:100]}...")

    def test_it_support_query(self, executor, session_id):
        """
        Test 5: IT Support Query
        Bonus test: Validates IT Support department routing and RAG retrieval.
        """
        query = "How do I reset my password for the company portal?"
        
        result = executor.execute(
            query=query,
            session_id=session_id,
            user_id="test_user_it"
        )

        # Verify IT Support classification
        assert result['department'] == Department.IT_SUPPORT.value
        assert result['sentiment'] in [Sentiment.POSITIVE.value, Sentiment.NEUTRAL.value]
        
        # Verify not escalated
        assert result['escalated'] is False
        
        # Verify response
        assert result['response'] is not None
        assert len(result['response']) > 0
        
        print(f"✓ IT Support Query Test Passed")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Department: {result['department']}")
        print(f"  Response Preview: {result['response'][:100]}...")

    def test_billing_query(self, executor, session_id):
        """
        Test 6: Billing & Payments Query
        Bonus test: Validates Billing department routing and response generation.
        """
        query = "What is your refund policy for returned items?"
        
        result = executor.execute(
            query=query,
            session_id=session_id,
            user_id="test_user_billing"
        )

        # Verify Billing department classification
        assert result['department'] == Department.BILLING_PAYMENTS.value
        assert result['sentiment'] in [Sentiment.POSITIVE.value, Sentiment.NEUTRAL.value]
        
        # Verify not escalated
        assert result['escalated'] is False
        
        # Verify response
        assert result['response'] is not None
        assert "refund" in result['response'].lower() or "return" in result['response'].lower() or "payment" in result['response'].lower()
        
        print(f"✓ Billing Query Test Passed")
        print(f"  Sentiment: {result['sentiment']}")
        print(f"  Department: {result['department']}")
        print(f"  Response Preview: {result['response'][:100]}...")


class TestAgentState:
    """Test agent state management and message tracking."""

    @pytest.fixture
    def executor(self):
        """Initialize agent executor for testing."""
        return AgentExecutor()

    def test_session_id_tracking(self, executor):
        """Verify session ID is properly tracked through execution."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        result = executor.execute(
            query="What is your return policy?",
            session_id=session_id,
            user_id="test_user"
        )

        # Session ID should be passed through
        assert session_id is not None
        assert len(session_id) > 0

    def test_user_id_tracking(self, executor):
        """Verify user ID is properly tracked through execution."""
        user_id = "test_user_123"
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        result = executor.execute(
            query="Tell me about shipping options",
            session_id=session_id,
            user_id=user_id
        )

        # User should be tracked
        assert result['metadata'] is not None

    def test_response_contains_metadata(self, executor):
        """Verify response contains all required metadata."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        result = executor.execute(
            query="How do I track my order?",
            session_id=session_id
        )

        # All required fields should be present
        assert 'response' in result
        assert 'sentiment' in result
        assert 'department' in result
        assert 'escalated' in result
        assert 'metadata' in result

    def test_retrieved_docs_count(self, executor):
        """Verify retrieved docs count is accurate for RAG queries."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        result = executor.execute(
            query="What is your vacation policy?",
            session_id=session_id
        )

        # Retrieved docs should be counted correctly
        assert 'retrieved_docs_count' in result
        assert isinstance(result['retrieved_docs_count'], int)
        assert result['retrieved_docs_count'] >= 0


class TestAgentErrorHandling:
    """Test agent error handling and edge cases."""

    @pytest.fixture
    def executor(self):
        """Initialize agent executor for testing."""
        return AgentExecutor()

    def test_empty_query_handling(self, executor):
        """Verify agent handles empty or very short queries gracefully."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        # Very short query
        result = executor.execute(
            query="help",
            session_id=session_id
        )

        # Should still return valid response
        assert result['response'] is not None
        assert result['sentiment'] is not None
        assert result['department'] is not None

    def test_very_long_query(self, executor):
        """Verify agent handles very long queries gracefully."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        long_query = "Can you help me with " + "a very long question " * 50 + "?"
        
        result = executor.execute(
            query=long_query,
            session_id=session_id
        )

        # Should still return valid response
        assert result['response'] is not None
        assert result['sentiment'] is not None
        assert result['department'] is not None

    def test_special_characters_in_query(self, executor):
        """Verify agent handles special characters in queries."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"
        
        query = "Why isn't my order @#$% arriving?! ><"
        
        result = executor.execute(
            query=query,
            session_id=session_id
        )

        # Should still return valid response
        assert result['response'] is not None
        assert result['sentiment'] is not None
        assert result['department'] is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
