#!/bin/bash

ENV_NAME="catalog_env"
REQUIREMENTS_FILE="requirements.txt"

# --- Step 1: Create the Virtual Environment ---
echo "--- Creating Python virtual environment: $ENV_NAME ---"
# Check if python3 or python command is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is not found. Please install Python 3 first."
    exit 1
fi

$PYTHON_CMD -m venv $ENV_NAME

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment. Ensure venv module is available."
    exit 1
fi

echo "Environment created successfully."

# --- Step 2: Activate the Environment and Install Requirements ---

# Activation command differs by OS/Shell
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux or macOS (Bash/Zsh)
    source $ENV_NAME/bin/activate
else
    # Windows (This part usually requires user intervention if not using Git Bash)
    echo "Please activate your environment manually using:"
    echo "For Command Prompt: .\\venv\\Scripts\\activate"
    echo "For PowerShell: .\\venv\\Scripts\\Activate.ps1"
    echo "Once activated, run 'pip install -r requirements.txt'"
    exit 0 # Exit the script to let the user activate manually
fi

echo "--- Installing dependencies from $REQUIREMENTS_FILE ---"
pip install -r $REQUIREMENTS_FILE

if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements."
    exit 1
fi

echo "--- Setup complete! ---"
echo "To activate this environment in the future, run: source $ENV_NAME/bin/activate"

