FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget curl unzip gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN GECKO_VERSION=$(curl -s https://api.github.com/repos/mozilla/geckodriver/releases/latest \
    | grep "tag_name" \
    | cut -d '"' -f 4)

COPY geckodriver /usr/local/bin

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir selenium psutil groq

CMD ["python", "squizz.py"]
