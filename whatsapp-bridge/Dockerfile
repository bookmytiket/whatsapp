
# Use Python 3.10 slim image
FROM python:3.10-slim

# Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    curl \
    libglib2.0-0 \
    libnss3 \
    libgconf-2-4 \
    libfontconfig1 \
    libxrender1 \
    libxtst6 \
    libxi6 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxdamage1 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libpangocairo-1.0-0 \
    libpango-1.0-0 \
    libxkbcommon0 \
    && rm -rf /var/lib/apt/lists/*

# Install Chromium
RUN apt-get update && apt-get install -y chromium chromium-driver

# Set environment variables for Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromium-driver
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
