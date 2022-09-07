# Start with a lightweight python 3 image
FROM python:3-alpine

# Send python output in real-time without needing to be buffered
ENV PYTHONUNBUFFERED=1
# Don't write .pyc files when importing source modules
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /code
COPY requirements.txt /code

# Install the packages needed to install psycopg2-binary: https://stackoverflow.com/a/47871121
RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    # Install all python dependencies
    pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

COPY . /code
WORKDIR /code/stockhelper
# Initialize the SQLite databases
RUN python manage.py migrate
# Load the flashcards data
RUN python manage.py loaddata cards.json
