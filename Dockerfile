# Start with a lightweight python 3 image
FROM python:3-alpine

# Send python output in real-time without needing to be buffered
ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY requirements.txt /code
# Install all python dependencies
RUN pip install -r requirements.txt

COPY . /code
WORKDIR /code/stockhelper
# Initialize the SQLite databases
RUN python manage.py migrate
# Load the flashcards data
RUN python manage.py loaddata cards.json
