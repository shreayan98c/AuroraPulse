# Use official Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy pyproject.toml and lock file (if any) first for caching
COPY pyproject.toml poetry.lock* /app/

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pip requirements from pyproject.toml

# If using PEP 621 / simple pip install
RUN pip install --upgrade pip setuptools wheel
RUN pip install .

# Copy the rest of the app
COPY . /app

# Expose Streamlit default port
EXPOSE 8501

# Streamlit config: prevent telemetry
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_TELEMETRY_ENABLED=false

# Entry point using uv
ENTRYPOINT ["uv", "run", "streamlit", "run", "main.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
