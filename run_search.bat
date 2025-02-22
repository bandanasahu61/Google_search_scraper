#!/bin/bash
echo "Installing requirements..."
python -m pip install -r requirements.txt

echo "Starting Google Search Scraper..."
python src/main.py

read -p "Press Enter to exit..."
