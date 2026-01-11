#!/bin/bash
# Setup script for rabbitmq-queue-monitor skill
# Creates virtual environment and installs dependencies

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "Setting up rabbitmq-queue-monitor skill..."

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists."
fi

# Activate and install dependencies
echo "Installing dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"

# Update script shebang to use venv Python
SCRIPT_PATH="$SCRIPT_DIR/scripts/rabbitmq_monitor.py"
if [ -f "$SCRIPT_PATH" ]; then
    # Check if shebang already points to venv
    CURRENT_SHEBANG=$(head -1 "$SCRIPT_PATH")
    VENV_SHEBANG="#!$VENV_DIR/bin/python3"

    if [ "$CURRENT_SHEBANG" != "$VENV_SHEBANG" ]; then
        echo "Updating script shebang to use virtual environment..."
        sed -i "1s|.*|$VENV_SHEBANG|" "$SCRIPT_PATH"
    fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "Usage:"
echo "  $SCRIPT_DIR/scripts/rabbitmq_monitor.py --env DEV overview"
echo "  $SCRIPT_DIR/scripts/rabbitmq_monitor.py --env DEV queues"
echo "  $SCRIPT_DIR/scripts/rabbitmq_monitor.py --env DEV queue my-queue-name"
echo ""
echo "Don't forget to configure your credentials:"
echo "  cp $SCRIPT_DIR/references/.credentials.example $SCRIPT_DIR/references/.credentials"
echo "  chmod 600 $SCRIPT_DIR/references/.credentials"
