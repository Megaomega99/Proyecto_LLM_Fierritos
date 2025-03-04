FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy entire project
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r app/requirements.txt

# Create uploads directory
RUN mkdir -p uploads

# Expose port for FastAPI
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]