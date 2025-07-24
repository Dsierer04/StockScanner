# Use a lightweight Python image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    libnss3 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libdrm2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Install Playwright browsers
RUN playwright install --with-deps firefox

# Copy the entire project
COPY . .

# Expose the port Render will use
EXPOSE 8000

# Start the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stock_dashboard:app"]

