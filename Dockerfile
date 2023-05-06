# Start with a python 3 base image
ARG PYTHON_VERSION=3-alpine
FROM python:${PYTHON_VERSION}

WORKDIR /app
COPY requirements.txt .

# Install dependencies
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . .
ENV SECRET_KEY=$SECRET_KEY FMP_API_KEY=$FMP_API_KEY

# Initialize the Postgres database, load the flashcards data, and collect all static files
RUN \
    python stockhelper/manage.py migrate && \
    python stockhelper/manage.py loaddata cards.json && \
    python stockhelper/manage.py collectstatic --noinput

# Start an HTTP server
EXPOSE 8080
CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "--chdir", "stockhelper", "stockhelper.wsgi"]
