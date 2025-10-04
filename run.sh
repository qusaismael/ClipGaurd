#!/bin/bash
# ClipGuard Launcher Script

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$DIR/venv" ]; then
    source "$DIR/venv/bin/activate"
fi

# Run ClipGuard
python3 "$DIR/main.py"


