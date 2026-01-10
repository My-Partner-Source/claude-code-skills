#!/bin/bash
# Setup script for aws-sso-env-switcher skill
# Creates virtual environment and installs dependencies

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
SCRIPT_PATH="$SCRIPT_DIR/scripts/aws_sso_env.py"
REQUIREMENTS="$SCRIPT_DIR/requirements.txt"

echo "Setting up aws-sso-env-switcher..."

# Check for AWS CLI v2
if ! command -v aws &> /dev/null; then
    echo "Warning: AWS CLI not found"
    echo "Install from: https://aws.amazon.com/cli/"
else
    AWS_VERSION=$(aws --version 2>&1 | grep -oP 'aws-cli/\K[0-9]+' || echo "1")
    if [ "$AWS_VERSION" -lt 2 ]; then
        echo "Warning: AWS CLI v2 is required for SSO support"
        echo "Current version: $(aws --version)"
        echo "Upgrade from: https://aws.amazon.com/cli/"
    fi
fi

# Check for kubectl
if ! command -v kubectl &> /dev/null; then
    echo "Warning: kubectl not found"
    echo "Install from: https://kubernetes.io/docs/tasks/tools/"
fi

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

# Update shebang in aws_sso_env.py to use venv Python
VENV_PYTHON="$VENV_DIR/bin/python3"
if [ -f "$SCRIPT_PATH" ]; then
    echo "Updating script shebang to use virtual environment..."
    # macOS sed requires '' after -i, Linux doesn't - try both
    if sed -i '' "1s|.*|#!$VENV_PYTHON|" "$SCRIPT_PATH" 2>/dev/null; then
        :
    else
        sed -i "1s|.*|#!$VENV_PYTHON|" "$SCRIPT_PATH"
    fi
    chmod +x "$SCRIPT_PATH"
else
    echo "Warning: aws_sso_env.py not found at $SCRIPT_PATH"
fi

echo ""
echo "Setup complete!"
echo "  Virtual environment: $VENV_DIR"
echo "  Python: $VENV_PYTHON"
echo ""
echo "Next steps:"
echo "  1. Copy .credentials.example to .credentials and configure:"
echo "     cd $SCRIPT_DIR/references"
echo "     cp .credentials.example .credentials"
echo "     chmod 600 .credentials"
echo ""
echo "  2. Edit .credentials with your AWS SSO details"
echo ""
echo "  3. Test the skill:"
echo "     $SCRIPT_PATH list"
echo "     $SCRIPT_PATH status"
echo ""
