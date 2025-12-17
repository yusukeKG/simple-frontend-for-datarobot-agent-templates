FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# DataRobot uses /opt/code as working directory
WORKDIR /opt/code

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY src/ ./src/
COPY start-app.sh .
COPY metadata.yaml .

# Fix line endings and make executable
RUN sed -i 's/\r$//' start-app.sh && \
    chmod +x start-app.sh

# Set environment variables
ENV PORT=8080 \
    DOCKER_CONTAINER=1 \
    PYTHONPATH=/opt/code \
    FLASK_APP=src.backend.app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/api/health || exit 1

# Use exec form to ensure proper signal handling
ENTRYPOINT ["/bin/bash", "./start-app.sh"]