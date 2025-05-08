# syntax = docker/dockerfile:1.2
FROM python:3.12.2-slim
LABEL maintainer="Vadim Kozyrevskiy" \
      email="vadikko2@mail.ru"

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install --no-install-recommends -y git ffmpeg && \
    pip install --no-cache-dir --upgrade pip==24.* && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Redis
ARG REDIS_HOSTNAME
ARG REDIS_PORT
ARG REDIS_DATABASE
ARG REDIS_USER
ARG REDIS_PASSWORD
ENV REDIS_HOSTNAME=$REDIS_HOSTNAME
ENV REDIS_PORT=$REDIS_PORT
ENV REDIS_DATABASE=$REDIS_DATABASE
ENV REDIS_USER=$REDIS_USER
ENV REDIS_PASSWORD=$REDIS_PASSWORD

# S3
ARG S3_ENDPOINT_URL
ARG S3_REGION_NAME
ARG S3_BUCKET_NAME
ARG S3_PATH_PREFIX
ARG S3_ACCESS_KEY_ID
ARG S3_SECRET_ACCESS_KEY
ENV S3_ENDPOINT_URL=$S3_ENDPOINT_URL
ENV S3_REGION_NAME=$S3_REGION_NAME
ENV S3_BUCKET_NAME=$S3_BUCKET_NAME
ENV S3_PATH_PREFIX=$S3_PATH_PREFIX
ENV S3_ACCESS_KEY_ID=$S3_ACCESS_KEY_ID
ENV S3_SECRET_ACCESS_KEY=$S3_SECRET_ACCESS_KEY


# Install requirements
RUN pip install --no-cache-dir -r /code/requirements.txt --root-user-action=ignore

COPY ./src/ /code/src/

EXPOSE 80
EXPOSE 443
CMD ["uvicorn", "--app-dir", "/code/src/", "presentation.api.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "80"]
