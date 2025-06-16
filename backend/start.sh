#!/bin/bash

# Check if virtual environment exists
if ! poetry env list --full-path | grep -q 'Activated'; then
  echo "Poetry environment not found. Installing..."
  poetry install
fi

# Start FastAPI using Uvicorn
echo "Starting FastAPI app..."
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
