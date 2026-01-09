#!/bin/bash
# Setup script for oracle-query-runner skill
# Creates virtual environment and installs dependencies

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
SCRIPT_PATH="$SCRIPT_DIR/scripts/oracle_query.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

echo "Setting up oracle-query-runner..."

# Create venv if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Upgrade pip in venv
echo "Upgrading pip..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet

# Install dependencies
if [ -f "$REQUIREMENTS" ]; then
    echo "Installing dependencies from requirements.txt..."
    "$VENV_DIR/bin/pip" install -r "$REQUIREMENTS" --quiet
else
    echo "Warning: requirements.txt not found at $REQUIREMENTS"
fi

# Ensure script is executable
if [ -f "$SCRIPT_PATH" ]; then
    chmod +x "$SCRIPT_PATH"
fi

VENV_PYTHON="$VENV_DIR/bin/python3"

echo ""
echo "Setup complete!"
echo "  Virtual environment: $VENV_DIR"
echo "  Python: $VENV_PYTHON"
echo ""
echo "You can now use oracle-query-runner. Try:"
echo "  $SCRIPT_PATH --help"
