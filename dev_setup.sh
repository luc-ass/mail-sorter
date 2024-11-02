#!/bin/bash

# Stop execution if any command fails
set -e

# Define the virtual environment directory
VENV_DIR=".venv"

# Check if the virtual environment directory already exists
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists. Skipping creation."
else
    echo "Creating virtual environment in $VENV_DIR..."
    python3 -m venv $VENV_DIR
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install required packages
echo "Installing requirements from requirements.txt..."
pip install -r requirements.txt

echo "Development environment setup complete. To activate the environment, run:"
echo "source $VENV_DIR/bin/activate"
