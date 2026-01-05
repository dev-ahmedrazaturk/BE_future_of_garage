# Render-friendly FastAPI Dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# (Optional but helpful) build tools for any packages that might need compiling
# If your build works without this, you can remove this RUN block.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first (better caching)
COPY requirements.txt .

RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt

# Copy the rest of the app
COPY . .

# Render sets $PORT. Default to 10000 if not set.
# EXPOSE 10000

# CMD sh -c "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"

# # Step 6: Expose the port the app runs on
# EXPOSE 8003

# Step 7: Command to run FastAPI using Uvicorn (with --reload for development)
CMD ["/venv/bin/uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0"]
