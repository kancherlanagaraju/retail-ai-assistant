# Retail AI Assistant - System Architecture

## Overview

The Retail AI Assistant is a production-ready customer support system that combines intelligent query classification, semantic search, and escalation workflows. It uses LangGraph for orchestration, ChromaDB for vector storage, and multiple LLM providers with graceful degradation.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     1. USER INTERFACE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│          ┌─────────────────────────────────┐                     │
│          │      Streamlit UI (8501)        │                     │
│          │  • Chat interface               │                     │
│          │  • Escalation form              │                     │
│          │  • Session management           │                     │
│          └─────────────────────────────────┘                     │
│                        ↓ (HTTP)                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      2. REST API                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│          ┌──────────────────────────────────────────┐            │
│          │  FastAPI Server (Port 8000)              │            │
│          │  ┌────────┬─────────┬─────────┬────────┐ │            │
│          │  │ /chat  │/health  │/escalate│/agent │ │            │
│          │  │        │         │         │/status│ │            │
│          │  └────────┴─────────┴─────────┴────────┘ │            │
│          └──────────────────────────────────────────┘            │
│                        ↓ (async)                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              3. AGENT WORKFLOW (LangGraph)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────┐   ┌──────────────┐   ┌─────────────────┐ │
│  │ classify_intent_ │   │ route_node   │   │   rag_node      │ │
│  │ sentiment        │→→→│              │→→→│                 │ │
│  │                  │   │ Sentiment?   │   │ Vector search   │ │
│  │ • Sentiment      │   │ Department?  │   │ LLM response    │ │
│  │ • Department     │   │              │   │                 │ │
│  │ • Audience       │   └──────────────┘   └─────────────────┘ │
│  │                  │         ↓                                  │
│  └──────────────────┘    Negative or                             │
│                          "Other"?                                │
│                             ↓                                    │
│                    ┌─────────────────────┐                       │
│                    │ escalation_node     │                       │
│                    │                     │                       │
│                    │ • Collect contact   │                       │
│                    │ • Create ticket     │                       │
│                    │ • 24h SLA           │                       │
│                    └─────────────────────┘                       │
│                             ↓                                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│           4. KNOWLEDGE & STORAGE LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │    ChromaDB        │  │   Embeddings     │  │    LLMs      │ │
│  │                    │  │                  │  │              │ │
│  │ • 60 QA pairs      │  │ OpenAI (primary):│  │ 1. Claude    │ │
│  │ • 4 departments    │  │ text-embedding-  │  │    3.5       │ │
│  │ • Persistent       │  │ 3-small          │  │              │ │
│  │   storage          │  │                  │  │ 2. GPT-4o    │ │
│  │ • Cosine sim       │  │ Mock (fallback): │  │              │ │
│  │ • Metadata filter  │  │ SHA256-based     │  │ 3. Mock LLM  │ │
│  │                    │  │ deterministic    │  │ (graceful)   │ │
│  └────────────────────┘  └──────────────────┘  └──────────────┘ │
│                             ↓ ↑                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                5. DATA SOURCE                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│    ┌────────────────────────────────────────────────────────┐   │
│    │   synthetic_datasets.json                              │   │
│    │   15 QA pairs × 4 departments:                         │   │
│    │   • HR (leave, benefits, payroll)                     │   │
│    │   • IT Support (password, VPN, laptop)                │   │
│    │   • Billing & Payments (refunds, invoices)            │   │
│    │   • Shipping & Delivery (tracking, delivery)          │   │
│    └────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer Details

### Layer 1: User Interface
**Component:** Streamlit (Port 8501)
- **Chat Interface:** Accept user queries with real-time streaming
- **Escalation Form:** Collect contact information (name, email, phone)
- **Session State:** Maintain conversation history and metadata
- **Files:** `ui.py` (366 lines)

### Layer 2: REST API
**Component:** FastAPI (Port 8000)
- **GET /health** — System status check
- **POST /chat** — Process query and return response
- **POST /escalation** — Manual escalation endpoint
- **GET /agent/status** — Workflow execution details
- **Files:** `api/app.py`
- **Features:**
  - CORS enabled for Streamlit communication
  - Pydantic validation for all requests
  - Async/await for high concurrency
  - Automatic vector store initialization on startup

### Layer 3: Agent Workflow (LangGraph)
**Component:** LangGraph StateGraph with conditional routing

#### State Definition (`agent/state.py`)
```python
AgentState:
  - query: str
  - sentiment: Sentiment (positive/neutral/negative)
  - department: Department (HR/IT/Billing/Shipping/Other)
  - audience: str (internal/external)
  - retrieved_docs: List[Dict]
  - response: str
  - escalated: bool
  - messages: List[Tuple[str, str]]  # (role, content)
```

#### Nodes (`agent/nodes.py`)

1. **classify_intent_and_sentiment**
   - Uses Claude 3.5 Sonnet with structured output
   - Fallback to GPT-4o, then mock classification
   - Keywords: "leave"→HR, "payment"→Billing, "password"→IT
   - Sentiment: negative words (angry, frustrated, disappointed, etc.)

2. **route_to_rag_or_escalation**
   - **Escalate if:** Negative sentiment OR Department = "Other"
   - **RAG if:** Positive/neutral AND known department

3. **rag_node**
   - Calls VectorStoreBuilder.search() with department filter
   - Retrieves top 5 documents via cosine similarity
   - Uses LLM to generate response from context
   - Returns formatted answer

4. **human_escalation_node**
   - Generates escalation message with empathy
   - Collects mock contact info (can be extended)
   - Creates internal ticket with 24-hour SLA
   - Logs escalation metadata

#### Router Logic (`agent/nodes.py:route_to_rag_or_escalation`)
```
IF sentiment == "negative" OR department == "Other":
    → human_escalation_node
ELSE:
    → rag_node
```

**Files:** `agent/graph.py`, `agent/nodes.py`, `agent/state.py`

### Layer 4: Knowledge & Storage

#### Vector Store (ChromaDB)
- **Database:** Persistent SQLite backend at `./vectorstore/chroma_db/`
- **Collection:** `retail-qa` (60 documents)
- **Metadata:** category, audience
- **Distance Metric:** Cosine similarity
- **Search:** Supports optional category filtering

**Retrieval Example:**
```
Query: "How do I apply for annual leave?"
Filter: category = "HR"
Result: Top 5 HR documents with cosine scores
```

#### Embeddings (`vectorstore/db_builder.py:get_embeddings()`)

**Primary (Production):**
- **Provider:** OpenAI
- **Model:** `text-embedding-3-small`
- **Dimensions:** 1536
- **Speed:** ~100 tokens/request
- **Cost:** ~$0.02 per 1M tokens

**Fallback (Development):**
- **Type:** Mock embeddings
- **Method:** SHA-256 hash → float array (384 dims)
- **Deterministic:** Same text = same embedding
- **Use:** Testing without API costs

#### LLM Selection (`agent/nodes.py:get_llm()`)

| Rank | Provider | Model | Use Case |
|------|----------|-------|----------|
| 1 | Anthropic | Claude 3.5 Sonnet | Structured output, reasoning |
| 2 | OpenAI | GPT-4o | High quality, multimodal capable |
| 3 | None | Mock LLM | Testing without API keys |

**Fallback Logic:**
```python
IF ANTHROPIC_API_KEY:
    return Claude 3.5 Sonnet
ELIF OPENAI_API_KEY:
    return GPT-4o
ELSE:
    return MockLLM (keyword-based)
```

### Layer 5: Data Source

**File:** `data/synthetic_datasets.json`

**Structure:**
```json
[
  {
    "doc": "Q: How do I request time off or PTO? A: You can request...",
    "category": "HR",
    "audience": "internal"
  }
]
```

**Distribution:**
- **Total:** 60 QA pairs
- **HR:** 15 (leave, benefits, payroll, onboarding)
- **IT Support:** 15 (password, VPN, email, laptop, software)
- **Billing & Payments:** 15 (refunds, invoices, subscriptions, charges)
- **Shipping & Delivery:** 15 (tracking, delivery times, returns, packaging)

**Audiences:**
- **Internal:** Employee-facing questions
- **External:** Customer-facing questions

---

## Data Flow

### Happy Path (RAG)
```
1. User submits query → Streamlit
2. FastAPI /chat endpoint receives query
3. LangGraph executes:
   a. classify_intent_and_sentiment
      - "How do I apply for leave?" → HR, neutral
   b. route_to_rag_or_escalation
      - Neutral + HR → route to rag_node
   c. rag_node
      - Search ChromaDB for HR docs
      - Get "How do I request time off or PTO?"
      - LLM generates response
4. FastAPI returns response
5. Streamlit displays answer
```

### Escalation Path
```
1. User submits negative query → Streamlit
2. FastAPI /chat endpoint receives query
3. LangGraph executes:
   a. classify_intent_and_sentiment
      - "I'm very frustrated!" → negative, other dept
   b. route_to_rag_or_escalation
      - Negative sentiment → route to escalation_node
   c. human_escalation_node
      - Generate empathy message
      - Request contact info
      - Create ticket
4. FastAPI returns escalation message
5. Streamlit shows escalation form
```

---

## Configuration

### Environment Variables (`.env`)
```
OPENAI_API_KEY=sk-...        # OpenAI embeddings & LLM
ANTHROPIC_API_KEY=...         # Claude (optional, preferred)
```

### LangGraph Settings
- **Checkpoint:** In-memory (no persistence)
- **Recursion Limit:** 25 iterations
- **Timeout:** None (async/await)

### ChromaDB Settings
- **Path:** `./vectorstore/chroma_db/`
- **Collection:** `retail-qa`
- **Distance Metric:** cosine
- **Persistence:** SQLite backend

---

## Deployment

### Local Development
```bash
# Terminal 1: FastAPI
python -m uvicorn api.app:app --reload

# Terminal 2: Streamlit
streamlit run ui.py
```

### Docker
```bash
docker build -t retail-ai .
docker run -p 8000:8000 -p 8501:8501 retail-ai
```

### Production
- Deploy FastAPI to AWS Lambda / Cloud Run
- Deploy Streamlit to Streamlit Cloud / Railway
- Use managed vector DB (Pinecone / Weaviate) instead of local ChromaDB

---

## Testing

### Unit Tests (13 passing)
- **Route:** Positive/neutral HR query → RAG
- **Route:** Positive/neutral Shipping query → RAG
- **Escalate:** Negative sentiment → escalation
- **Escalate:** Unknown department ("Other") → escalation
- **Classify:** IT Support, Billing departments
- **Error Handling:** Empty/long/special character queries
- **State Management:** Session tracking, metadata

**Run Tests:**
```bash
pytest tests/test_agent.py -v
```

---

## Performance Metrics

| Component | Speed | Cost | Quality |
|-----------|-------|------|---------|
| Embeddings (OpenAI) | ~100ms | $0.02/1M tokens | ⭐⭐⭐⭐⭐ |
| Embeddings (Mock) | ~5ms | Free | ⭐⭐ (deterministic) |
| ChromaDB Search | ~50ms | Free | ⭐⭐⭐⭐ (cosine) |
| Claude Response | ~2s | $0.15/1K input | ⭐⭐⭐⭐⭐ |
| GPT-4o Response | ~1s | $0.03/1K input | ⭐⭐⭐⭐⭐ |
| Mock LLM | ~10ms | Free | ⭐⭐ (basic) |
| **End-to-End** | **~3s** | **Variable** | **⭐⭐⭐⭐** |

---

## Error Handling & Graceful Degradation

### Embedding Failures
```
OpenAI API unavailable
    ↓
Fall back to Mock embeddings
    ↓
Continue with SHA-256 hash vectors
```

### LLM Failures
```
Claude API unavailable
    ↓
Try OpenAI GPT-4o
    ↓
Use Mock LLM (keyword-based)
    ↓
Return formatted document text
```

### Vector Store Issues
```
ChromaDB initialization fails
    ↓
Return escalation message
    ↓
Flag as escalated
    ↓
Human support takes over
```

---

## Security Considerations

✅ **Implemented:**
- Environment variables for API keys (not hardcoded)
- CORS filtering for Streamlit
- Pydantic validation on all inputs
- No PII logging (queries sanitized)

⚠️ **Future Enhancements:**
- Rate limiting per user/session
- Request signing for API endpoints
- Audit logs for escalations
- Encrypted vector store backup
- SOC 2 compliance for production

---

## Future Enhancements

1. **Multi-language Support**
   - Translate queries to English before classification
   - Support responses in user's language

2. **Advanced Routing**
   - Intent-based routing (payment dispute vs. refund request)
   - Confidence scores for escalation thresholds
   - A/B testing of routing rules

3. **Feedback Loop**
   - User satisfaction rating
   - Escalation resolution tracking
   - Fine-tune embeddings on real queries

4. **Analytics**
   - Query volume by department
   - Escalation rate trends
   - Response quality metrics
   - Cost optimization dashboard

5. **Integration**
   - Slack bot wrapper
   - Zendesk ticketing system
   - Salesforce CRM sync
   - Webhooks for external systems

---

## Summary

The Retail AI Assistant combines **intelligent classification**, **semantic search**, and **human escalation** into a cohesive system. It prioritizes **reliability** through graceful degradation and **modularity** through LangGraph's state-driven architecture. Whether running on OpenAI's production embeddings or mock fallbacks, the system ensures customer queries are handled with empathy and efficiency.

**Key Strengths:**
- ✅ Modular LangGraph workflow
- ✅ Multi-provider LLM support
- ✅ Persistent vector store with filtering
- ✅ Comprehensive test coverage (13/13 passing)
- ✅ Graceful error handling
- ✅ Easy local development

**Ready for:** Production deployment with minor infrastructure changes (managed DB, cloud hosting, monitoring)
