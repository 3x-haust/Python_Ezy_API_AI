FROM python:3.9-slim

COPY ezy.json /app/
COPY . /app/

RUN pip install --upgrade pip && \
    pip install ezyapi && \
    ezy install

ENTRYPOINT ["ezy", "run"]
CMD ["start"]