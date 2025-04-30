#!/bin/bash
set -e

export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
pyenv global 3.11

# Activate the virtual environment
source venv/bin/activate

# Run the FastAPI server with Uvicorn
exec uvicorn main:app --host 0.0.0.0 --port 80