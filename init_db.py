#!/usr/bin/env python
"""Initialize database - create tables or run migrations"""
import os
import sys
from app import create_app
from app.models import db

def init_database():
    """Initialize database with tables"""
    app = create_app()
    
    with app.app_context():
        try:
            print("Checking database connection...")
            # Test connection
            db.engine.connect()
            print("Database connected successfully")
            
            print("Creating tables if they don't exist...")
            db.create_all()
            print("Database tables ready")
            
            return True
        except Exception as e:
            print(f"Database initialization error: {e}")
            return False

if __name__ == '__main__':
    success = init_database()
    sys.exit(0 if success else 1)
