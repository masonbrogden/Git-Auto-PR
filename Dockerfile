# Use official Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install CA certificates and dependencies
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Default command to run the bot
CMD ["python", "bot/main.py"]
