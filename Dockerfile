FROM debian:bookworm-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

COPY . .

CMD ["python3", "impulsos_auto_bot.py"]
