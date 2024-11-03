#!/bin/bash

# Create and activate virtual environment
./scripts/create_venv.sh

# Install initial dependencies based on imports in your code
source venv/bin/activate
pip install anthropic pyyaml

# Generate requirements file
./scripts/generate_requirements.sh

echo "Setup completed successfully!" 

# pip install -r requirements.txt 