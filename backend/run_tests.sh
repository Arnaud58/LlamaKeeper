#!/bin/bash

# Ensure the script is executable
chmod +x "$0"

# Activate the virtual environment if needed
# source ~/miniconda3/etc/profile.d/conda.sh
# conda activate keeper

# Change to the backend directory
cd "$(dirname "$0")"

# Run tests with coverage
pytest \
    --cov=app \
    --cov-report=html:coverage_report \
    --cov-report=xml \
    --cov-report=term-missing \
    tests/

# Optional: Open the coverage report in the default browser
# xdg-open coverage_report/index.html