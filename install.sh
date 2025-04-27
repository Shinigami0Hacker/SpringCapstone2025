#!/bin/bash

SECRET_FILE="/etc/device-secret-token"
MODEL_MANAGER_API_ENDPOINT="http://model.athena-lab.cloud"

if [ ! -f "$FILE" ]; then
    echo "Not found secret, exiting..."
    exit 1
fi

echo "Found secret, starting..."

sudo apt-get update

if [ -d "$HOME/.pyenv" ]; then
    echo "Detect the installed pyenv package. Skip the installation!"

else
    sudo apt-get install --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev -y
    git clone https://github.com/pyenv/pyenv.git ~/.pyenv
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
fi

if [-d ""]; then
    python ./utils/db.py

pyenv install 3.10
pyenv virtualenv 3.10 .venv
pyenv local .venv

pip3 install -r requirement.txt

nohup uvicorn main:app --host 0.0.0.0 --port 80 --reload /var/log/yield 2>&1 &

