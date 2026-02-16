#!/bin/bash


# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt

echo "Environment setup complete. Activate with 'source venv/bin/activate'"
