# Start with a python 3 base image
ARG PYTHON_VERSION=3-alpine
FROM python:${PYTHON_VERSION}
# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    uv sync --locked --group prod --no-dev --no-cache && \
    apk --purge del .build-deps

COPY . .
ENV SECRET_KEY=$SECRET_KEY FMP_API_KEY=$FMP_API_KEY

# Initialize the Postgres database, load the flashcards data, and collect all static files
RUN \
    uv run stockhelper/manage.py migrate && \
    uv run stockhelper/manage.py loaddata cards.json && \
    uv run stockhelper/manage.py collectstatic --noinput

# Start an HTTP server
EXPOSE 8080
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "--chdir", "stockhelper", "stockhelper.wsgi"]
