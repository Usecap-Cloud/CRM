FROM python:3.10-slim

WORKDIR /src

# Install system dependencies for MySQL
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Collect static files at build time
RUN python manage.py collectstatic --noinput 2>/dev/null || true

# Expose the port (Zeabur assigns $PORT dynamically)
EXPOSE 8080

# Startup script: run migrations then start gunicorn
# Uses $PORT from Zeabur, falling back to 8080
CMD sh -c "python manage.py migrate --noinput && gunicorn crm_usecap.wsgi:application --bind 0.0.0.0:${PORT:-8080} --workers 2"
