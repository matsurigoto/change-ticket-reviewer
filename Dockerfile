FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY config ./config
RUN useradd -r -u 10001 app
USER 10001
ENTRYPOINT ["ticket-reviewer"]
