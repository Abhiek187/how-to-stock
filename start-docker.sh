#!/bin/bash
ENV="stockhelper/.env"

# Populate the .env file if it doesn't exist
if [ ! -e "$ENV" ]; then
    # Throw an error if the user didn't pass in their API key
    if [ $# == 0 ]; then
        echo "Error: No API key provided"
        exit 1
    fi

    echo $'Generating a secret key...'
    if type openssl > /dev/null; then
        echo "SECRET_KEY=$(openssl rand -base64 32)" > "$ENV"
    else
        echo "SECRET_KEY=$(head -c 32 /dev/urandom | base64)" > "$ENV"
    fi

    echo $'\nTurning on DEBUG mode...'
    echo "DEBUG=true" >> "$ENV"

    echo $'\nSaving the API key...'
    echo "FMP_API_KEY=$1" >> "$ENV"
else
    echo "The .env file is already created."
fi

# Spin up a docker container
docker compose up -d
