# Use lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    gnupg \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (for Twitter scraping)
RUN playwright install --with-deps firefox

# Copy the application code
COPY . .

# Expose the port Render uses
EXPOSE 8000

# Start the app with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stock_dashboard:app"]


# Start the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stock_dashboard:app"]

