FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install ezyapi && \
    ezy install

ENTRYPOINT ["ezy", "run"]
CMD ["start"]