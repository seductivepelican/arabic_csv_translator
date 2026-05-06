# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (needed for sentencepiece/torch)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create models directory
RUN mkdir -p models

# One-time step to download the model into the image
# This makes the image large (~5GB) but truly offline/portable
RUN python scripts/download_model.py

# Command to run the translator
# Example usage: docker run -v /local/path:/data translator --input /data/input.csv --output /data/output.csv
ENTRYPOINT ["python", "main.py"]
