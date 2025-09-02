#!/bin/bash

echo "Starting AI Medical Insurance Coverage Checker..."

# Start backend in background
echo "Starting backend..."
cd /app/backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

# Wait a bit for backend to initialize
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is responding
if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is ready!"
else
    echo "⚠️ Backend may not be fully ready, but continuing..."
fi

# Start frontend
echo "Starting frontend..."
cd /app/frontend
streamlit run streamlit_app.py --server.port ${PORT:-8501} --server.address 0.0.0.0 --server.headless true
