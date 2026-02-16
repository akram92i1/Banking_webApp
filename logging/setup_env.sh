#!/bin/bash

# Create virtual environment
python3 -m venv ai_agent_Env

# Activate virtual environment
source ai_agent_Env/bin/activate

# Upgrade pip and install build tools
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r ai_agent_requirement.txt

echo "Environment setup complete. Activate with 'source ai_agent_Env/bin/activate'"
