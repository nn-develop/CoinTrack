FROM python:3.13.1-bullseye

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Create a group with GID 1000 and a user with UID 1000
RUN groupadd -g 1000 devgroup && \
    useradd -u 1000 -g devgroup -m -s /bin/bash devuser

# Install PostgreSQL dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    && apt-get clean

WORKDIR /app

# Install pip packages 
COPY requirements-dev.txt requirements-dev.txt
COPY requirements.txt requirements.txt

# (for production enviroment change to requirements.txt)
RUN pip install --no-cache-dir -r requirements-dev.txt

# Switch to the non-root user 'devuser'
USER devuser