#!/bin/bash

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install it first."
    exit 1
fi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

echo "Virtual environment created and activated successfully!" 