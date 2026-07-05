FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# Copy project configuration
COPY pyproject.toml .

# Install python dependencies
RUN pip install --no-cache-dir -e .

# Install playwright browsers
RUN playwright install chromium
RUN playwright install-deps

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run the application
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8501"]
