# Ask Me First in one container.
#   docker build -t askmefirst .
#   docker run -p 8000:8000 --env-file backend/.env askmefirst
#   docker run -p 8000:8000 -e DEMO_MODE=1 askmefirst    # no keys needed
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend
COPY frontend frontend

# Keys come in at run time (--env-file), never baked into the image.
RUN useradd --create-home app && chown -R app /app
USER app
WORKDIR /app/backend
ENV PORT=8000 LOG_RUNS=0
EXPOSE 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
