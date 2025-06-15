#!/bin/bash

# Script to run live database tests for TravelORM

# Set environment variables
export USE_HARDCODED_CREDENTIALS="true"
export DB_USERNAME="postgres"
export DB_PASSWORD="your_password_here"  # Replace with actual password
export DB_HOST="datamodelstack-travelitinerarydatabase47bf6447-e3cjz9xihder.c5cee08qie98.us-west-1.rds.amazonaws.com"
export DB_PORT="5432"
export DB_NAME="travel_itinerary"

# Activate virtual environment
source venv/bin/activate

# Install the package in development mode if not already installed
pip install -e .

# Run the tests
echo "Running live database tests..."
python tests/test_live_database.py

# Check the exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Live database tests passed!"
    exit 0
else
    echo "❌ Live database tests failed!"
    exit 1
fi
