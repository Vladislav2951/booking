FROM python:3.13-slim


COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /uvx /bin/
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV UV_PROJECT_ENVIRONMENT=/usr/local

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --no-install-project
COPY . .


EXPOSE 8000

# RUN chmod +x prestart.sh
# ENTRYPOINT ["./prestart.sh"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
