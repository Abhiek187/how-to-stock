#!/bin/bash
# Execute all the necessary steps to run the project

# Check if the virtual environment exists
VENV="venv"

if [ ! -d "$VENV" ]; then
    echo "1. Creating a folder for the virtual environment..."
    python3 -m venv "$VENV"
else
    echo "1. The virtual environment already exists."
fi

# $'strings' allow for escaped characters
echo $'\n2. Activating the virtual environment...'
source "$VENV"/bin/activate

echo $'\n3. Installing all python dependencies...'
pip3 install -r requirements.txt

echo $'\n4. Heading into the stockhelper directory...'
cd stockhelper

if [ ! -e .env ]; then
    echo $'\n5. Generating a secret key...'

    if type openssl > /dev/null; then
        echo "SECRET_KEY=$(openssl rand -base64 32)" > .env
    else
        echo "SECRET_KEY=$(head -c 32 /dev/urandom | base64)" > .env
    fi

    echo $'\n6. Turning on DEBUG mode...'
    echo "DEBUG=true" >> .env
else
    echo $'\n5. The secret key already exists.'
    echo $'\n6. DEBUG mode is on.'
fi

echo $'\n7. Creating the SQLite database...'
python3 manage.py migrate

echo $'\n8. Loading the flashcards data...'
python3 manage.py loaddata cards.json

echo $'\n9. Running the Django server...'
python3 manage.py runserver
