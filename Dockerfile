FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 libcairo2 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/instance /app/static/uploads

EXPOSE 6040

CMD ["gunicorn", "--bind", "0.0.0.0:6040", "--workers", "2", "--timeout", "120", "app:app"]
