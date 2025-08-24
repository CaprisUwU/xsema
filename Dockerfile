# Production Dockerfile for XSEMA NFT Analytics Engine
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN addgroup --system app && adduser --system --group app

# Set work directory
WORKDIR /app

# Install Python dependencies - Using secure requirements
COPY requirements-minimal-secure.txt .
RUN pip install --no-cache-dir -r requirements-minimal-secure.txt

# Copy project
COPY . .

# Debug: List files to ensure railway_start.py is copied
RUN ls -la && echo "=== Checking for railway_start.py ===" && ls -la railway_start.py || echo "railway_start.py not found!"

# Change ownership to app user
RUN chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run the application - Using railway_start.py as Railway expects
# Fallback to direct uvicorn if railway_start.py fails
CMD ["sh", "-c", "python railway_start.py || uvicorn app:app --host 0.0.0.0 --port 8000"]
