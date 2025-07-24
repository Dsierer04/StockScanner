FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y build-essential wget gnupg \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
ENV PYTHONUNBUFFERED=1
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stock_dashboard:app"]
# Expose the port Render will use
EXPOSE 8000

# Start the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "stock_dashboard:app"]
