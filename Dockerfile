FROM python:3.9-slim

WORKDIR /app

COPY ezy.json /app/
COPY . /app/

RUN pip install --upgrade pip && \
    pip install ezyapi && \
    pwd && ls -la && \
    ezy install

CMD ["sh", "-c", "ls -la && ezy install && ezy run start"]

