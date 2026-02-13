FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# ffmpeg is often useful for video apps, though strict TVHUB usage might not need it yet
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose port 5000
EXPOSE 5000

# Run with Gunicorn (Production server)
# 4 workers is a good starting point
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
