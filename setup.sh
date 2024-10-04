#!/bin/bash

# Create the virtual environment
echo "Creating virtual environment..."
python3 -m venv .env

echo "Setup complete. Your virtual environment is now ready to use."
echo "To activate it, use 'source .env/bin/activate'."
echo "If it's your first time you'll want to run the following after activating..."
echo "pip install -r requirements.txt"
echo "To deactivate the virtual environment, type 'deactivate'."
