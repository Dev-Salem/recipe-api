# Stage 1: Build stage
FROM python:3.12-alpine3.20 as builder
LABEL maintainer="@dev_salem0"

ENV PYTHONUNBUFFERED=1

# Install dependencies for building Python packages
RUN apk add --no-cache \
    build-base \
    postgresql-dev \
    musl-dev \
    libffi-dev \
    openssl-dev \
    python3-dev

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Create virtual environment
RUN python -m venv /py

# Upgrade pip
RUN /py/bin/pip install --upgrade pip

# Install production requirements
RUN /py/bin/pip install -r /tmp/requirements.txt

# Install development requirements if needed
ARG DEV=false
RUN if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi

# Stage 2: Final stage
FROM python:3.12-alpine3.20
LABEL maintainer="@dev_salem0"

ENV PYTHONUNBUFFERED=1

# Install PostgreSQL client
RUN apk add --no-cache postgresql-client

# Copy only the necessary parts from the builder stage
COPY --from=builder /py /py
COPY ./app /app

WORKDIR /app
EXPOSE 8000

ENV PATH="/py/bin:$PATH"

# Add django user
RUN adduser --disabled-password --no-create-home django-user

USER django-user
