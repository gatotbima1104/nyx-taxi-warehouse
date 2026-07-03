FROM python:3.13.14-slim-bookworm

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY uv.lock pyproject.toml ./

RUN uv sync --frozen

COPY . .

CMD ["bash", "scripts/entrypoint.sh"]