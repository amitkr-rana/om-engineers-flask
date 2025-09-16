#!/usr/bin/env python3
"""
Script to reset the database with the updated schema
Run this when you've made changes to the database models
"""

from app import create_app
from database import reset_database

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        print("Resetting database with updated schema...")
        reset_database()
        print("Database reset complete!")
        print("The email field is now nullable and customer names should save properly.")