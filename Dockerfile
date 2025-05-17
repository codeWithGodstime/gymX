# First, use an official Python slim image to build the app
FROM python:3.12-slim-bookworm AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN python -m venv .venv && \
    .venv/bin/pip install --upgrade pip && \
    .venv/bin/pip install -r requirements.txt

# Copy project files
COPY . .

# Final image
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Copy the virtual environment and app code from the builder
COPY --from=builder /app /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/app/.venv/bin:$PATH"

# Expose port 8000
EXPOSE 8000

# Run the app with gunicorn
CMD ["gunicorn", "--bind", ":8000", "--workers", "2", "django_project.wsgi"]
