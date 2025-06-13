FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create database directory and set permissions
RUN mkdir -p src/database && chmod -R 777 src/database

# Expose port
EXPOSE 5001

# Define persistent volume for database
VOLUME /app/src/database

ENV FLASK_APP=src/main.py
ENV FLASK_ENV=production

CMD ["python", "src/main.py"]


