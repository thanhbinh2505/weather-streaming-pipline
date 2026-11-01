FROM apache/spark:3.5.0

USER root

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml ./

RUN uv python install 3.11
RUN uv sync --no-dev --group consumer

COPY consumer/main.py ./consumer/

ENV JAVA_HOME=/opt/java/openjdk
ENV PYSPARK_PYTHON=/app/.venv/bin/python
ENV PYTHONPATH="/app/.venv/lib/python3.11/site-packages:$PYTHONPATH"

CMD ["uv", "run", "python", "consumer/main.py"]