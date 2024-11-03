#!/bin/bash

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Please activate virtual environment first"
    exit 1
fi

# Generate requirements.txt
pip freeze > requirements.txt

echo "Requirements file generated successfully!" 