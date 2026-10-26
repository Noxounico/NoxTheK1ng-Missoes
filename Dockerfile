FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot_safe.py .
COPY .env .env 2>/dev/null || true

CMD ["python", "bot_safe.py"]
