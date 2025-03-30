### Chatgpt generated
# Use slim Python base image
FROM python:3.10-slim

# Install system dependencies for image processing
RUN apt-get update && apt-get install -y \
  build-essential \
  libgl1-mesa-glx \
  libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app/backend

# Copy dependency file and install Python packages
COPY requirements.txt ../requirements.txt
RUN pip install --no-cache-dir -r ../requirements.txt

# Copy source code
COPY backend/ .

# Expose FastAPI port
EXPOSE 8000

# Run the FastAPI app (assumes app instance is in main.py)
CMD ["fastapi", "run", "main.py", "--host", "0.0.0.0", "--port", "8000"]

