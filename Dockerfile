# syntax = docker/dockerfile:1.2
FROM python:3.12.2-slim
LABEL maintainer="Vadim Kozyrevskiy" \
      email="vadikko2@mail.ru"
ENV TZ='Europe/Moscow'

# hadolint ignore=DL3008
RUN apt-get update && \
    apt-get install --no-install-recommends -y git && \
    pip install --no-cache-dir --upgrade pip==24.* && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

# Getting token variable
ARG GITHUB_TOKEN

# Install requirements
RUN sed -i.bak "s|https://github.com/vadikko2|https://$GITHUB_TOKEN@github.com/vadikko2|g" /code/requirements.txt &&  \
    cat /code/requirements.txt && \
    pip install --no-cache-dir -r /code/requirements.txt --root-user-action=ignore

COPY ./src/ /code/src/

EXPOSE 80
CMD ["uvicorn", "--app-dir", "/code/src/", "presentation.api.main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "80"]
