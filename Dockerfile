ARG PYTHON_VERSION=3-alpine

FROM python:${PYTHON_VERSION}

RUN \
    apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev

RUN mkdir -p /app
WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN apk --purge del .build-deps

COPY . .

RUN \
    python stockhelper/manage.py migrate && \
    python stockhelper/manage.py loaddata cards.json && \
    python stockhelper/manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "--bind", ":8080", "--workers", "2", "--chdir", "stockhelper", "stockhelper.wsgi"]
