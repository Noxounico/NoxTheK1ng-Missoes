FROM python:3.11-slim

WORKDIR /app

# Install Chrome and dependencies for Selenium
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    ca-certificates \
    fonts-liberation \
    libnss3 \
    libxss1 \
    && rm -rf /var/lib/apt/lists/*

# Setup Chrome path
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER=/usr/bin/chromedriver

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bot_complete.py .
COPY browser_handler.py .
COPY .env .env 2>/dev/null || true

CMD ["python", "bot_complete.py"]
