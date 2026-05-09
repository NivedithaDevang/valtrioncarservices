FROM python:3.11-slim

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install (also install eventlet for SocketIO)
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt eventlet gunicorn

# Copy app
COPY . /app

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

EXPOSE 8080

# Run the app
CMD ["python", "run.py"]
