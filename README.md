# Retail AI Assistant

An enterprise-grade AI assistant for retail operations powered by LangGraph and OpenAI. This system is designed to handle customer inquiries, process transactions, and provide intelligent recommendations for retail stores.

## Project Structure

```
retail-ai-assistant/
├── config/
│   └── settings.py          # Configuration and environment variables
├── data/
│   └── synthetic_datasets.json  # Training and evaluation datasets
├── vectorstore/
│   └── db_builder.py        # Vector database initialization and management
├── agent/
│   ├── state.py             # Agent state management
│   ├── nodes.py             # Node definitions for the agent graph
│   └── graph.py             # Graph orchestration and workflows
├── api/
│   └── app.py               # FastAPI application and endpoints
├── requirements.txt         # Python dependencies
├── README.md               # Project documentation
└── tests/
    └── test_agent.py       # Unit and integration tests
```

## Setup Instructions

### Prerequisites
- Python 3.10 or higher (tested on Python 3.14)
- pip package manager
- OpenAI API key (optional — app works with mock LLM if not provided)
- Anthropic API key (optional — alternative to OpenAI)

### Virtual Environment Setup

#### Option 1: Using venv (Built-in)
```bash
# Navigate to the project directory
cd retail-ai-assistant

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option 2: Using conda (if you prefer)
```bash
# Create conda environment
conda create -n retail-ai python=3.9

# Activate environment
conda activate retail-ai

# Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

1. Copy the example `.env` file:
```bash
cp .env.example .env
```

2. Update `.env` with your configuration (API keys are optional):
```
# Optional: Add your OpenAI API key for better LLM performance
OPENAI_API_KEY=your_api_key_here

# Optional: Or use Anthropic Claude instead
ANTHROPIC_API_KEY=your_anthropic_key_here

# Vector store configuration
CHROMA_DB_PATH=./vectorstore/chroma_db
LOG_LEVEL=INFO
```

**Note:** The app includes mock LLM and embeddings for testing without API keys. For production use, add at least one API key (OpenAI or Anthropic).

## Running the Application

### Start the FastAPI Server

**Option 1: Using the run script (Recommended - handles SSL issues)**
```bash
./run.sh
```

**Option 2: Using uvicorn directly**
```bash
# Make sure your virtual environment is activated
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

**Option 3: If you encounter SSL issues (macOS)**
```bash
# Disable SSL verification (temporary fix)
PYTHONHTTPSVERIFY=0 uvicorn api.app:app --reload
```

**On first run:** The application will automatically initialize the vector store from `data/synthetic_datasets.json` (takes ~5-10 seconds). Subsequent runs will use the cached vector store.

The API will be available at `http://localhost:8000`

### Access API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Run Tests
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agent.py -v

# Run with coverage
pytest --cov=agent --cov=api tests/
```

## Authentication & Security

### JWT Token Authentication
The API supports optional JWT authentication for production deployments:

**Login to get token:**
```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user@example.com"}'

# Response:
# {"access_token": "eyJhbGc...", "token_type": "bearer", "expires_in": 86400, "user_id": "user@example.com"}
```

**Use token in subsequent requests:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "Help with my order"}'
```

**Configuration:**
- `REQUIRE_AUTH=false` (default) - Authentication optional, backward compatible
- `REQUIRE_AUTH=true` (production) - Authentication required on all protected endpoints
- `JWT_SECRET` - Change this in production!
- `JWT_EXPIRATION_HOURS` - Token expiration time

---

## Key Components

### Agent State (`agent/state.py`)
Manages the state machine for the agentic workflow, including user queries, context, and decision paths.

### Agent Nodes (`agent/nodes.py`)
Defines individual processing nodes:
- Query processing
- Intent classification
- Database lookup
- Response generation

### Agent Graph (`agent/graph.py`)
Orchestrates the workflow using LangGraph's StateGraph for reliable agent execution with proper state management.

### Vector Store (`vectorstore/db_builder.py`)
Initializes and manages ChromaDB for semantic search of product catalogs, customer data, and FAQs.

### API Server (`api/app.py`)
FastAPI application exposing RESTful endpoints for:
- Chat interactions
- Product search
- Order processing
- Agent status monitoring

## Development Workflow

### Adding Dependencies
```bash
# Add a new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

### Code Quality
```bash
# Format code
pip install black
black .

# Lint code
pip install flake8
flake8 .

# Type checking
pip install mypy
mypy .
```

## Configuration Management

### Environment Variables
Key environment variables can be configured in `.env`:

```bash
# API & Server
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
PORT=8000
DEBUG=False

# CORS (Security) - Prevent CSRF attacks
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
# Set this to your actual frontend URL(s) in production

# Rate Limiting (Security) - Prevent DoS attacks
# Format: requests/time_period
CHAT_RATE_LIMIT=10/minute
ESCALATION_RATE_LIMIT=30/minute
HEALTH_RATE_LIMIT=100/minute
STATUS_RATE_LIMIT=30/minute

# Vector Store
CHROMA_DB_PATH=./vectorstore/chroma_db
```

**Rate Limiting Notes:**
- `/chat` endpoint: Limited to 10 requests/minute per IP (most critical)
- `/escalation` endpoint: Limited to 30 requests/minute per IP
- `/health` endpoint: Limited to 100 requests/minute per IP (healthchecks)
- `/agent/status` endpoint: Limited to 30 requests/minute per IP
- Adjust these limits based on your production load
- Returns HTTP 429 (Too Many Requests) when limit exceeded

### Centralized Configuration
All configurations are also available in `config/settings.py`. Key settings include:
- API credentials
- Model parameters
- Vector store settings
- Logging configuration
- Cache settings

## Data Management

### Synthetic Datasets (`data/synthetic_datasets.json`)
The source of truth for all vector store data. Contains:
- Product catalog
- Customer personas
- Order history samples
- FAQ entries
- Common query patterns

### Vector Store (`vectorstore/chroma_db/`)
**Not committed to GitHub** — Generated on first run from `synthetic_datasets.json`.
- Automatically initialized when the app starts
- Stores vector embeddings and metadata
- Persisted locally for performance
- Can be regenerated by deleting the directory and restarting the app

## Logging and Monitoring

The system includes structured logging throughout:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Agent initialized")
```

## Production Deployment

### Docker Support (Optional)
Create a `Dockerfile` in the project root:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t retail-ai-assistant .
docker run -p 8000:8000 retail-ai-assistant
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Write tests for new functionality
3. Ensure all tests pass: `pytest`
4. Commit with clear messages
5. Submit a pull request

## Troubleshooting

### Virtual Environment Issues
```bash
# Deactivate current environment
deactivate

# Remove and recreate
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt
```

### NumPy/ChromaDB Compatibility (Python 3.14+)
If you see errors about `np.float_` being deprecated:
```bash
# Ensure you have compatible versions
pip install --upgrade chromadb numpy pandas
```

### Port Already in Use
```bash
# Run on different port
uvicorn api.app:app --reload --host 0.0.0.0 --port 8001
```

### ChromaDB Vector Store Issues
On first run, the vector store will be initialized at `./vectorstore/chroma_db`:
```bash
# Clear vector store if needed
rm -rf vectorstore/chroma_db
```

### SSL Certificate Error (macOS / Corporate Networks)
If you see `SSLError: certificate verify failed` when initializing the vector store:

**Quick Fix (Recommended):**
```bash
# Use the provided run script (handles SSL automatically)
./run.sh
```

**Or run with environment variable:**
```bash
PYTHONHTTPSVERIFY=0 uvicorn api.app:app --reload
```

**Proper Fix (Optional):**
```bash
# macOS with Homebrew
brew install ca-certificates
export SSL_CERT_FILE=$(brew --prefix)/etc/ca-certificates/cert.pem

# Or use Python's certifi
export SSL_CERT_FILE=$(python -c "import certifi; print(certifi.where())")
```

This is a known issue with:
- Fresh Python installations on macOS
- Corporate networks with SSL interception
- System without proper CA certificates

The app continues to work even if SSL verification fails - it just uses escalation instead of RAG retrieval.

## License

Internal Project - Retail AI Assistant Inc.

## Support

For issues and questions, contact the AI Engineering team.
