# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

# TODO: Lock these to a specific java version and have dependabot update these
FROM eclipse-temurin:8-jre AS java8
FROM eclipse-temurin:17-jre AS java17
FROM eclipse-temurin:21-jre AS java21
FROM eclipse-temurin:25-jre AS java25
FROM ghcr.io/astral-sh/uv:0.11.6 AS pyuv

FROM python:3.13.1-slim AS base
COPY --from=pyuv /uv /uvx /bin/

# Disable development dependencies
ENV UV_NO_DEV=1

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

# Tell the app we are in docker
ENV IN_DOCKER=True

WORKDIR /app

# Create a non-privileged user that the app will run under.
# See https://docs.docker.com/go/dockerfile-user-best-practices/
ARG UID=1000
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/bin/bash" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install java
RUN mkdir -p /usr/lib/jvm

COPY --from=java8 /opt/java/openjdk /usr/lib/jvm/java-8-temurin
COPY --from=java17 /opt/java/openjdk /usr/lib/jvm/java-17-temurin
COPY --from=java21 /opt/java/openjdk /usr/lib/jvm/java-21-temurin
COPY --from=java25 /opt/java/openjdk /usr/lib/jvm/java-25-temurin

# Alias java
RUN ln -s /usr/lib/jvm/java-8-temurin/bin/java /usr/bin/java8 && \
    ln -s /usr/lib/jvm/java-17-temurin/bin/java /usr/bin/java17 && \
    ln -s /usr/lib/jvm/java-21-temurin/bin/java /usr/bin/java21 && \
    ln -s /usr/lib/jvm/java-25-temurin/bin/java /usr/bin/java25

# Make sure they work
RUN java8 -version
RUN java17 -version
RUN java21 -version

# Script requirements

RUN apt-get update && \
    apt-get install -y curl jq openssl sudo lsof && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project

# Copy the source code into the container.
COPY --chown=appuser:appuser . /app

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked

# Switch back to the non-privileged user.
#USER appuser # Now done in entrypoint

# Expose the port that the application listens on.
EXPOSE 7843

# Run the application using exec form (JSON array) so signals are delivered properly.
ENTRYPOINT ["/app/entrypoint.sh"]
#CMD ["waitress-serve", "--host=0.0.0.0", "--port=7843", "app:app"]
CMD ["/app/.venv/bin/python3", "-u", "-m", "app"]
