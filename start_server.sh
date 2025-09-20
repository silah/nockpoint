#!/bin/bash

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Start the Flask development server
python -m flask run --host=0.0.0.0 --port=5000 --debug
