FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create data directory and ensure permissions
RUN mkdir -p data && chmod 755 data

# Create empty fitness_data.json if it doesn't exist
RUN if [ ! -f fitness_data.json ]; then echo '{"meals": [], "settings": {}}' > fitness_data.json; fi

# Expose port (Railway uses PORT env var)
EXPOSE $PORT

# Run with gunicorn (Railway will set $PORT)
CMD gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - app_pro:app
