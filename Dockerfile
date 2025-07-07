# Use Python 3.13-alpine as base image
FROM python:3.13-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_CREATE=false \
    PRISMA_CLI_QUERY_ENGINE_TYPE=binary \
    PRISMA_CLI_BINARY_TARGETS=linux-musl

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies and Poetry
RUN apk add --no-cache \
    build-base \
    curl \
    libffi-dev \
    openssl \
    openssl-dev \
    postgresql-dev && \
    curl --proto "=https" -ssL https://install.python-poetry.org | python3 - && \
    addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies including dev dependencies
RUN poetry install --no-interaction --no-ansi --no-root --with dev

# Copy application code
COPY src/ ./src
COPY prisma/ ./prisma

# Create necessary directories and set permissions
RUN mkdir -p /app/src/prisma_client && \
    chown -R appuser:appgroup /app

# Switch to appuser for Prisma operations
USER appuser

# Fetch Prisma binaries and generate client
RUN poetry run prisma py fetch && \
    poetry run prisma generate --schema=./prisma/schema.prisma

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["poetry", "run", "python3", "-m", "src.server"] 