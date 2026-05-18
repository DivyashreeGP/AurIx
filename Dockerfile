# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:$PATH" \
    PYTHONPATH="/app"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install AI engine dependencies (support multiple providers)
RUN pip install --no-cache-dir \
    google-genai \
    openai \
    python-dotenv

# Copy the project files (excluding files in .dockerignore)
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/results /app/temp_files /app/Rule-Engine/results

# Make scripts executable
RUN chmod +x docker-start.sh

# Expose port for API
EXPOSE 8000

# Health check using curl (now installed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Default command
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
