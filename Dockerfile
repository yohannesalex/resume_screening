# FROM python:3.9-slim

# WORKDIR /app

# RUN apt-get update && apt-get install -y \
#     poppler-utils \
#     tesseract-ocr \
#     libtesseract-dev \
#     && rm -rf /var/lib/apt/lists/*

# COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt

# # Copy the entire app directory
# COPY /app .

# # Set Python path
# ENV PYTHONPATH=/app

# CMD ["python", "-m", "consumer"]
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    tesseract-ocr \
    poppler-utils \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install NLTK data
RUN python -m nltk.downloader punkt stopwords wordnet omw-1.4

# Copy application code
COPY . .

# Create shared volume directory
RUN mkdir -p /shared_volume

# Set environment variables
ENV TESSERACT_CMD=/usr/bin/tesseract
ENV POPPLER_PATH=/usr/bin

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]