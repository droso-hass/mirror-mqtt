FROM python:3.10-slim

WORKDIR /app
COPY . .
RUN apt-get update && apt-get install -y uhubctl && pip3 install -r requirements.txt && chmod +x mirror.py

CMD "/app/mirror.py"