#!/bin/bash
# Run script for Retail AI Assistant
# Handles SSL certificate issues on macOS

# Set Python to not verify HTTPS certificates (fixes macOS SSL issues)
export PYTHONHTTPSVERIFY=0

# Run the application
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
