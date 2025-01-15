#!/usr/bin/env python3

import sys
import os

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, db

def main():
    with app.app_context():
        db.drop_all()
        print("All tables dropped from the database.")

if __name__ == "__main__":
    main()