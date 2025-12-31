FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

ENV FLASK_APP=app.py

CMD python init_db.py && echo "Database ready, starting gunicorn..." && gunicorn --bind 0.0.0.0:${PORT:-5000} --timeout 120 --workers 2 --log-level info app:app
