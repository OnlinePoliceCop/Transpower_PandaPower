#!/bin/bash

# Activate conda environment
eval "$(conda shell.bash hook)"
conda activate transpower

# Run the Flask application
python main.py 