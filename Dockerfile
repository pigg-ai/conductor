FROM python:3.11.6-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY conductor /app
COPY uv.lock /app
COPY pyproject.toml /app
COPY main.py /app


WORKDIR /app
RUN uv sync --frozen

CMD ["uv", "run", "main.py"]