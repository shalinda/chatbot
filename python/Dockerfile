# Stage 1: Build Environment
FROM python:3.11-slim as build

# Set the working directory
WORKDIR /app

# Install system dependencies for building and AWS CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    && curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" \
    && unzip awscliv2.zip \
    && ./aws/install \
    && rm -rf awscliv2.zip aws/ \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only requirements.txt to leverage caching
COPY requirements.txt /app/requirements.txt

# Install Python dependencies into a virtual environment
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r /app/requirements.txt

# Stage 2: Runtime Environment
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy runtime dependencies from the build stage
COPY --from=build /app/venv /app/venv

# Copy application code
COPY . /app

# Set PATH to include the virtual environment
ENV PATH="/app/venv/bin:$PATH"

# Expose port 3001
EXPOSE 3001

# Run the app using Gunicorn with 4 worker processes
CMD ["gunicorn", "--bind", "0.0.0.0:3001", "wsgi:app", "--workers=4"]
