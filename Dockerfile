FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY dijkstra.py /app/dijkstra.py

ENTRYPOINT ["python", "/app/dijkstra.py"]
