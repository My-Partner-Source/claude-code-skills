#!/bin/bash
# Setup script for datadog-api skill
# Creates virtual environment and installs dependencies

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
SCRIPT_PATH="$SCRIPT_DIR/scripts/datadog_api.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

echo "Setting up datadog-api..."

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

# Update shebang in datadog_api.py to use venv Python
VENV_PYTHON="$VENV_DIR/bin/python3"
if [ -f "$SCRIPT_PATH" ]; then
    echo "Updating script shebang to use virtual environment..."
    # Portable sed that works on both macOS and Linux
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "1s|.*|#!$VENV_PYTHON|" "$SCRIPT_PATH"
    else
        sed -i "1s|.*|#!$VENV_PYTHON|" "$SCRIPT_PATH"
    fi
    chmod +x "$SCRIPT_PATH"
else
    echo "Warning: datadog_api.py not found at $SCRIPT_PATH"
fi

echo ""
echo "Setup complete!"
echo "  Virtual environment: $VENV_DIR"
echo "  Python: $VENV_PYTHON"
echo ""
echo "You can now use datadog-api. Try:"
echo "  $SCRIPT_PATH --help"
