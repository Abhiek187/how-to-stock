#!/bin/bash
# Execute all the necessary steps to run the project
echo $'1. Installing all python dependencies...'
uv sync

# $'strings' allow for escaped characters
echo $'\n2. Heading into the stockhelper directory...'
cd stockhelper

if [ ! -e .env ]; then
    # Throw an error if the user didn't pass in their API key
    if [ $# == 0 ]; then
        echo "Error: No API key provided"
        exit 1
    fi
    
    echo $'\n3. Generating a secret key...'

    if type openssl > /dev/null; then
        echo "SECRET_KEY=$(openssl rand -base64 32)" > .env
    else
        echo "SECRET_KEY=$(head -c 32 /dev/urandom | base64)" > .env
    fi

    echo $'\n4. Turning on DEBUG mode...'
    echo "DEBUG=true" >> .env

    echo $'\n5. Saving the API key...'
    echo "FMP_API_KEY=$1" >> .env
else
    echo $'\n3. The secret key already exists.'
    echo $'\n4. DEBUG mode is on.'
    echo $'\n5. The API key is already stored.'
fi

echo $'\n6. Creating the SQLite database...'
uv run manage.py migrate

echo $'\n7. Loading the flashcards data...'
uv run manage.py loaddata cards.json

echo $'\n8. Running the Django server...'
uv run manage.py runserver
