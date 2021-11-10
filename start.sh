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

echo $'\n5. Creating the SQLite databases...'
python3 manage.py migrate

echo $'\n6. Loading the flashcards data...'
python3 manage.py loaddata cards.json

if [ ! -e .env ]; then
  echo $'\n7. Generating a secret key...'

  if type openssl > /dev/null; then
    echo "SECRET_KEY=$(openssl rand -base64 32)" > .env
  else
    echo "SECRET_KEY=$(head -c 32 /dev/urandom | base64)" > .env
  fi
else
  echo $'\n7. The secret key already exists.'
fi

echo $'\n8. Running the Django server...'
python3 manage.py runserver
