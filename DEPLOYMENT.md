# Retail AI Assistant - Deployment Guide

## Deployment Architecture Overview

### Quick View
```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   LOCAL DEV  │─────→│   GITHUB     │─────→│   CI/CD      │
│  Python venv │      │  Repository  │      │   Pipeline   │
└──────────────┘      └──────────────┘      └──────────────┘
                                                   ↓
                                          ┌──────────────┐
                                          │   STAGING    │
                                          │  Environment │
                                          └──────────────┘
                                                   ↓
                                          (Manual Approval)
                                                   ↓
                                          ┌──────────────┐
                                          │ PRODUCTION   │
                                          │ Environment  │
                                          └──────────────┘
```

---

## 1. Development Environment Setup

### Local Machine Configuration
```bash
# ✓ Already Configured
Python 3.14 with venv
FastAPI running on port 8000
Streamlit running on port 8501
ChromaDB persistent storage
```

### Key Files
- `api/app.py` — FastAPI application
- `ui.py` — Streamlit UI (366 lines)
- `agent/` — LangGraph workflow
- `vectorstore/` — ChromaDB with embeddings
- `tests/test_agent.py` — 13/13 passing tests

### Development Workflow
```bash
1. Clone repository
   git clone https://github.com/kancherlanagaraju/retail-ai-assistant.git

2. Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install -r requirements.txt

4. Run tests
   pytest tests/test_agent.py -v

5. Start FastAPI
   python -m uvicorn api.app:app --reload

6. Start Streamlit (in another terminal)
   streamlit run ui.py
```

---

## 2. Source Control (GitHub)

### Repository Structure
```
kancherlanagaraju/retail-ai-assistant/
├── main                    (Production releases)
├── dev                     (Development branch)
└── feature/*               (Feature branches)
```

### Commit Strategy
```bash
# Feature work
git checkout -b feature/my-feature
git commit -m "Add feature X"
git push origin feature/my-feature
# Create Pull Request → Code Review → Merge to dev

# Release to production
git checkout main
git merge dev
git tag v1.0.0
git push origin main --tags
```

### Branch Protection Rules
- `main`: Require PR review, pass CI tests
- `dev`: Require PR review
- Feature branches: Delete after merge

---

## 3. CI/CD Pipeline (GitHub Actions)

### Workflow: `.github/workflows/test-and-deploy.yml`
```yaml
name: Test & Deploy

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python 3.14
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ -v --tb=short
      
      - name: Lint & Type Check
        run: |
          pylint agent/ api/ vectorstore/
          mypy agent/ api/ --ignore-missing-imports

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t retail-ai:latest .
          docker tag retail-ai:latest ghcr.io/${{ github.repository }}:latest
      
      - name: Push to Registry
        run: |
          echo ${{ secrets.GITHUB_TOKEN }} | docker login ghcr.io -u $ --password-stdin
          docker push ghcr.io/${{ github.repository }}:latest

  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/dev'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Staging
        run: |
          # Example: Deploy to Google Cloud Run
          gcloud run deploy retail-ai-staging \
            --image ghcr.io/${{ github.repository }}:latest \
            --platform managed \
            --region us-central1 \
            --set-env-vars ENVIRONMENT=STAGING
```

### Status Checks
- ✅ Unit tests (13/13 passing)
- ✅ Type checking (mypy)
- ✅ Linting (pylint, flake8)
- ✅ Docker build
- ✅ Security scan (optional)

---

## 4. Staging Environment

### Infrastructure
```
Component         | Technology        | Details
----------------- | ----------------- | -------------------------
Load Balancer     | Cloud Run/K8s     | Auto-scale: 1-5 instances
FastAPI           | Docker container  | Port 8000, env: STAGING
Streamlit         | Docker container  | Port 8501, env: STAGING
Database          | Cloud SQL         | PostgreSQL, minimal size
Vector Store      | Pinecone free/test| For testing
Cache             | Redis             | Session cache
Monitoring        | Stackdriver/CW    | Basic logging
```

### Deployment Steps
```bash
# 1. Trigger from GitHub (webhook)
# 2. CI/CD builds Docker image
# 3. Push to container registry
# 4. Deploy to staging (rolling update)
# 5. Run smoke tests
#    - GET /health → 200 OK
#    - POST /chat → response in <5s
#    - Check CPU/memory usage
# 6. Generate test report
```

### Access Staging
```
Dashboard   : https://staging-retail-ai.example.com
API Docs    : https://staging-retail-ai.example.com/docs
Logs        : Cloud Logging dashboard
Metrics     : Grafana/DataDog
```

### Testing Checklist
- [ ] Health check passes
- [ ] Chat endpoint responds
- [ ] Escalation form works
- [ ] Vector search works
- [ ] LLM responses generated
- [ ] Database queries succeed
- [ ] Cache layer functional
- [ ] Error handling works
- [ ] Performance acceptable (<3s p95)

---

## 5. Production Environment

### High Availability Setup
```
Region 1 (us-east-1)        Region 2 (eu-west-1)
├─ FastAPI: 5-25 instances  ├─ FastAPI: 5-25 instances
├─ Streamlit: managed       ├─ Streamlit: managed
├─ PostgreSQL: replica      ├─ PostgreSQL: replica
└─ Redis cluster            └─ Redis cluster

                   ↓ ↓ ↓
          CloudFlare CDN
          (Rate limiting, DDoS)
```

### Deployment Strategy: Blue-Green
```
1. Deploy new version to "Green" environment
2. Run full test suite against Green
3. Switch traffic from Blue to Green (0-downtime)
4. Keep Blue running for 24h rollback window
5. If errors detected: switch back to Blue automatically
```

### Deployment Checklist
- [ ] All tests pass
- [ ] Manual approval obtained
- [ ] Database backups taken
- [ ] Vector store backed up
- [ ] Secrets rotated (if needed)
- [ ] Monitoring alerts configured
- [ ] On-call team notified
- [ ] Deployment window scheduled
- [ ] Rollback plan documented

### SLA & Monitoring
```
Uptime Target     : 99.9% (43 min downtime/month)
Response Time p95 : <2 seconds
Error Rate        : <0.1%
Vector Search     : <100ms
LLM Response      : <5 seconds
```

#### Key Metrics to Track
- **Latency:** Response times by endpoint
- **Throughput:** Requests per second
- **Error Rate:** 5xx and 4xx by endpoint
- **Vector Search:** Query latency
- **LLM Cost:** API calls & spend
- **Escalation Rate:** Negative sentiment queries
- **Database:** Query time, connection pool usage

---

## 6. Cloud Provider Options

### Option 1: Google Cloud (Recommended)
```
Service          | Configuration
---------------- | -------------------------
Compute          | Cloud Run (containers)
                 | Auto-scale: 0-50 instances
                 | 
Database         | Cloud SQL (PostgreSQL)
                 | High availability enabled
                 | 2 replicas for failover
                 | 
Vector Store     | Pinecone or Weaviate
                 | or Vertex AI Vector Search
                 | 
Cache            | Cloud Memorystore (Redis)
                 | High availability mode
                 | 
Monitoring       | Cloud Logging + Monitoring
                 | Custom metrics for LLM cost
                 | 
Secrets          | GCP Secret Manager
                 | Automatic rotation
                 | 
CDN              | Cloud CDN + Cloud Armor
                 | DDoS protection
                 | Rate limiting
                 | 
Cost             | ~$1,500-2,000/month
                 | (1M calls, 1000 concurrent users)
```

**Setup:**
```bash
# 1. Create GCP project
gcloud projects create retail-ai-prod

# 2. Enable APIs
gcloud services enable run.googleapis.com sql.googleapis.com

# 3. Create Cloud SQL instance
gcloud sql instances create retail-ai-db \
  --database-version=POSTGRES_15 \
  --tier=db-custom-4-16384 \
  --region=us-central1

# 4. Deploy to Cloud Run
gcloud run deploy retail-ai \
  --source . \
  --platform=managed \
  --region=us-central1 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=50 \
  --set-env-vars=ENVIRONMENT=PRODUCTION,OPENAI_API_KEY=$OPENAI_KEY
```

### Option 2: AWS
```
Service          | Configuration
---------------- | -------------------------
Compute          | Lambda + API Gateway
                 | or ECS on Fargate
                 | 
Database         | RDS PostgreSQL Multi-AZ
                 | Storage: 100GB+
                 | 
Vector Store     | Pinecone or self-hosted
                 | 
Cache            | ElastiCache (Redis)
                 | 
Monitoring       | CloudWatch + Alarms
                 | X-Ray for tracing
                 | 
Secrets          | AWS Secrets Manager
                 | 
CDN              | CloudFront
                 | WAF for DDoS
                 | 
Cost             | ~$1,200-1,800/month
```

### Option 3: Azure
```
Service          | Configuration
---------------- | -------------------------
Compute          | Container Instances
                 | App Service
                 | 
Database         | Azure Database for PostgreSQL
                 | Flexible Server
                 | 
Vector Store     | Azure Cognitive Search
                 | or Pinecone
                 | 
Cache            | Azure Cache for Redis
                 | 
Monitoring       | Azure Monitor
                 | Application Insights
                 | 
Secrets          | Key Vault
                 | 
CDN              | Azure Front Door
                 | 
Cost             | ~$1,400-2,000/month
```

### Option 4: Heroku / Railway (Easiest for Startups)
```
Everything included:
- PostgreSQL database
- Dyno compute (2-3 app dynos)
- Redis add-on
- Monitoring included
- SSL/TLS automatic
- One-command deploy

Cost: $50-150/month (very simple)
Setup: git push heroku main
```

---

## 7. Cost Breakdown (Monthly)

### Staging Environment
```
Component              Cost/Month
FastAPI compute        $20
Streamlit              $10
PostgreSQL             $15
Vector store (free)    $0
Redis cache            $5
Monitoring             $10
Data transfer          $5
OpenAI API             $50
────────────────────────────
SUBTOTAL              $115
```

### Production Environment (1M API calls)
```
Component              Cost/Month
FastAPI compute        $300
Streamlit              $150
PostgreSQL (HA)        $100
Vector store           $250
Redis (HA)             $50
Monitoring             $50
CDN/Gateway            $100
Data transfer          $100
OpenAI API             $500
────────────────────────────
SUBTOTAL              $1,600

+30% buffer (failures, scale): $2,080
```

---

## 8. Disaster Recovery

### Backup Strategy
```
Component          | Frequency | Retention | RPO/RTO
------------------ | --------- | --------- | --------
Database           | Daily     | 30 days   | 1hr/15min
Vector Store       | Weekly    | 90 days   | 1day/1hr
Secrets            | Monthly   | 12 months | Manual/5min
Code               | Commit    | Unlimited | -/-
```

### Failover Procedure
```
1. Monitoring alerts on main region
2. Automatic health check to standby region
3. Switch DNS to standby (30s - 5min)
4. Verify all endpoints responding
5. Notify ops team
6. Investigate root cause
7. Restore main region
8. Perform post-incident review
```

### Testing Recovery
```bash
# Monthly: Run disaster recovery drill
1. Restore database from backup
2. Verify data consistency
3. Test failover process
4. Measure actual RTO
5. Document findings
6. Update runbooks
```

---

## 9. Monitoring & Observability

### Key Metrics Dashboard
```
Real-time Metrics:
├─ Requests/min
├─ Error rate (%)
├─ Response time (p50/p95/p99)
├─ CPU usage (%)
├─ Memory usage (%)
├─ Database connections
├─ Vector search latency (ms)
├─ LLM API latency (ms)
├─ LLM API cost ($)
├─ Cache hit rate (%)
└─ Escalation rate (%)
```

### Alerting Rules
```
Alert when:
- Error rate > 1% for 5 minutes
- Response time p95 > 3 seconds
- CPU > 80% for 10 minutes
- Database connection pool > 90%
- Vector search > 500ms
- OpenAI API errors > 5/min
- Downtime detected
```

### Log Aggregation
```
Send logs to:
- CloudWatch / Cloud Logging / DataDog
- Include:
  * Request ID
  * User ID
  * LLM provider
  * Vector search latency
  * LLM response time
  * Escalation flag
  * Error stack traces
  * Cost per request
```

---

## 10. Security Checklist

- [ ] API keys in Secrets Manager (not in code)
- [ ] HTTPS/TLS enabled (all endpoints)
- [ ] Rate limiting enabled (100 req/min per user)
- [ ] CORS properly configured
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (using ORM)
- [ ] XSS prevention (sanitize outputs)
- [ ] CSRF tokens for state-changing requests
- [ ] DDoS protection enabled
- [ ] Firewall rules configured
- [ ] VPC/security groups set up
- [ ] Encryption at rest enabled
- [ ] Audit logging enabled
- [ ] Secrets rotation scheduled (90 days)
- [ ] Penetration testing scheduled (quarterly)

---

## 11. Deployment Checklist

Before each production deployment:

```
Code Quality:
  ✓ All tests passing (13/13)
  ✓ Code review approved
  ✓ No security issues found
  ✓ Performance benchmarks met

Infrastructure:
  ✓ Staging tests successful
  ✓ Database backed up
  ✓ Vector store backed up
  ✓ Secrets rotated
  ✓ Monitoring configured

Operational:
  ✓ On-call team notified
  ✓ Deployment window approved
  ✓ Rollback plan documented
  ✓ Customer communication ready
  ✓ Runbooks updated

Post-deployment:
  ✓ Smoke tests passed
  ✓ Metrics normal
  ✓ Error rate < 0.1%
  ✓ Performance acceptable
  ✓ No customer reports
```

---

## Quick Start: Deploy to GCP

```bash
# 1. Install tools
gcloud auth login
gcloud config set project retail-ai-prod

# 2. Create infrastructure
terraform apply  # If using IaC

# 3. Set environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="..."

# 4. Build and push
docker build -t retail-ai:latest .
docker tag retail-ai:latest gcr.io/retail-ai-prod/retail-ai:latest
docker push gcr.io/retail-ai-prod/retail-ai:latest

# 5. Deploy
gcloud run deploy retail-ai \
  --image gcr.io/retail-ai-prod/retail-ai:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=PRODUCTION

# 6. Get URL
gcloud run services describe retail-ai --region us-central1
```

---

## Deployment Architecture Diagrams

### File Formats Available
- **HTML**: `Deployment_Architecture.html` (Interactive, open in browser)
- **SVG**: `deployment_architecture_diagram.svg` (Scalable vector graphic)
- **PNG/JPEG**: Use online converter (e.g., https://cloudconvert.com)

### Convert SVG to JPEG Online
1. Go to: https://cloudconvert.com/svg-to-jpeg
2. Upload: `deployment_architecture_diagram.svg`
3. Download: High-quality JPEG

Or locally using ImageMagick:
```bash
convert deployment_architecture_diagram.svg \
  -background white \
  -alpha remove \
  -density 300 \
  -quality 95 \
  Deployment_Architecture.jpeg
```

---

## Troubleshooting

### Deployment Failures

**Issue: Docker build fails**
```bash
# Solution
docker system prune -a
docker build --no-cache -t retail-ai:latest .
```

**Issue: Health check fails**
```bash
# Check endpoint
curl http://localhost:8000/health
# Should return: {"status": "ok"}
```

**Issue: Database connection fails**
```bash
# Verify credentials
echo $DATABASE_URL
# Verify network access
telnet $DB_HOST 5432
```

**Issue: Vector search slow**
```bash
# Check embeddings model
# If using mock embeddings: performance is expected (~5ms)
# If using OpenAI: check network latency
# Consider batch queries or caching
```

---

## Support & Resources

- **Documentation**: See `Architecture.md` and `README.md`
- **Tests**: `pytest tests/test_agent.py -v`
- **API Docs**: `http://localhost:8000/docs` (after starting FastAPI)
- **Issues**: GitHub Issues on repository
- **Contact**: nagaraju.kancherla2@boomiteam.com

---

**Status**: ✅ Production-Ready | 🚀 Ready to Deploy
