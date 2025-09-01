# Use the official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY backend/requirements.txt ./backend/
COPY frontend/requirements.txt ./frontend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install --no-cache-dir -r frontend/requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create a startup script that runs both services
RUN echo '#!/bin/bash\n\
echo "Starting AI Medical Insurance Coverage Checker..."\n\
echo "Starting backend..."\n\
cd /app/backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 &\n\
sleep 5\n\
echo "Starting frontend..."\n\
cd /app/frontend && streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose the frontend port (Render will use this)
EXPOSE 8501

# Start the application
CMD ["/app/start.sh"]
