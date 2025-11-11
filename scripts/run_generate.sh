#!/bin/bash
# Script wrapper để chạy generate_dummy_data.py
# Tự động activate virtual environment

cd "$(dirname "$0")/.."
source venv/bin/activate
python scripts/generate_dummy_data.py
