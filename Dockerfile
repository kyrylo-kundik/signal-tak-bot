# Use Python 3.11 slim image as base
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY signal_bot/ signal_bot/

# Create non-root user
RUN useradd -m -r appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser
