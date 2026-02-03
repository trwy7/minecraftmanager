# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/go/dockerfile-reference/

# Want to help us make this template better? Share your feedback here: https://forms.gle/ybq9Krt8jtBL3iCk7

FROM eclipse-temurin:8-jre AS java8
FROM eclipse-temurin:17-jre AS java17
FROM eclipse-temurin:21-jre AS java21

FROM python:3.13.1-slim as base

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
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install java
RUN mkdir -p /usr/lib/jvm

COPY --from=java8 /opt/java/openjdk /usr/lib/jvm/java-8-temurin
COPY --from=java17 /opt/java/openjdk /usr/lib/jvm/java-17-temurin
COPY --from=java21 /opt/java/openjdk /usr/lib/jvm/java-21-temurin
RUN ln -s /usr/lib/jvm/java-8-temurin/bin/java /usr/bin/java8 && \
    ln -s /usr/lib/jvm/java-17-temurin/bin/java /usr/bin/java17 && \
    ln -s /usr/lib/jvm/java-21-temurin/bin/java /usr/bin/java21

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements.txt,target=requirements.txt \
    python -m pip install -r requirements.txt

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Switch back to the non-privileged user.
USER appuser

# Expose the port that the application listens on.
EXPOSE 7843

# Run the application using exec form (JSON array) so signals are delivered properly.
CMD ["waitress-serve", "--host=0.0.0.0", "--port=7843", "app:app"]
# CMD ["gunicorn", "--bind", "0.0.0.0:7842", "-w", "4", "app:app"]Z