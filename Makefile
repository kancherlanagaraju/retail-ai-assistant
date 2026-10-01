.PHONY: help venv install install-dev clean test test-coverage lint format run run-docker build-docker push-docker

# Variables
PYTHON := python3
VENV := venv
PYTHON_VENV := $(VENV)/bin/python
PIP_VENV := $(VENV)/bin/pip
DOCKER_IMAGE := retail-ai-assistant
DOCKER_TAG := latest

help:
	@echo "Retail AI Assistant - Development Commands"
	@echo "=========================================="
	@echo ""
	@echo "Setup:"
	@echo "  make venv              Create virtual environment"
	@echo "  make install           Install dependencies"
	@echo "  make install-dev       Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  make run               Run the application"
	@echo "  make test              Run tests"
	@echo "  make test-coverage     Run tests with coverage report"
	@echo "  make lint              Run code linter (flake8)"
	@echo "  make format            Format code with black"
	@echo ""
	@echo "Docker:"
	@echo "  make build-docker      Build Docker image"
	@echo "  make run-docker        Run application in Docker"
	@echo "  make stop-docker       Stop Docker containers"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean             Remove virtual environment and cache"
	@echo "  make clean-docker      Remove Docker images and containers"

venv:
	$(PYTHON) -m venv $(VENV)
	$(PIP_VENV) install --upgrade pip setuptools wheel

install: venv
	$(PIP_VENV) install -r requirements.txt

install-dev: install
	$(PIP_VENV) install black flake8 mypy pytest pytest-asyncio pytest-cov

run:
	$(PYTHON_VENV) -m uvicorn api.app:app --reload --host 0.0.0.0 --port 8000

test:
	$(PYTHON_VENV) -m pytest tests/ -v

test-coverage:
	$(PYTHON_VENV) -m pytest tests/ -v --cov=agent --cov=api --cov=vectorstore --cov=config --cov-report=html --cov-report=term

lint:
	$(PYTHON_VENV) -m flake8 agent/ api/ vectorstore/ config/ --max-line-length=100

format:
	$(PYTHON_VENV) -m black agent/ api/ vectorstore/ config/ tests/ --line-length=100

build-docker:
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

run-docker:
	docker-compose up -d

stop-docker:
	docker-compose down

logs-docker:
	docker-compose logs -f retail-ai-assistant

clean:
	rm -rf $(VENV)
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true

clean-docker:
	docker-compose down -v
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) 2>/dev/null || true

.DEFAULT_GOAL := help
