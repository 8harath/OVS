# database.py - Database initialization script
"""
This script initializes the database using SQLAlchemy ORM.
It creates all tables and populates them with sample data.

Note: The old raw SQL implementation has been replaced with SQLAlchemy ORM.
All database operations now use the models defined in models.py
"""

import os
import sys
from app import create_app
from models import db
from utils import create_sample_data, logger

def init_db():
    """Initialize database with tables and sample data"""
    # Create app instance
    app = create_app()

    with app.app_context():
        try:
            # Create all tables
            db.create_all()
            logger.info("Database tables created successfully")

            # Create sample data (admin user, candidates, elections)
            create_sample_data(db)
            logger.info("Sample data created successfully")

            print("✓ Database initialized successfully!")
            print(f"✓ Database location: {app.config['SQLALCHEMY_DATABASE_URI']}")
            print("\nDefault admin credentials:")
            print(f"  Voter ID: ADMIN001")
            print(f"  Password: {app.config.get('ADMIN_PASSWORD', 'Admin@123')}")
            print("\nYou can now run the application with: python app.py")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            print(f"✗ Error initializing database: {e}")
            sys.exit(1)

def reset_db():
    """Drop all tables and reinitialize database"""
    app = create_app()

    with app.app_context():
        try:
            # Drop all tables
            db.drop_all()
            logger.info("All tables dropped")
            print("✓ Database reset - all tables dropped")

            # Recreate tables
            db.create_all()
            logger.info("Database tables recreated")

            # Create sample data
            create_sample_data(db)
            logger.info("Sample data created")

            print("✓ Database reset complete!")

        except Exception as e:
            logger.error(f"Error resetting database: {e}")
            print(f"✗ Error resetting database: {e}")
            sys.exit(1)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Database management script')
    parser.add_argument('--reset', action='store_true',
                       help='Drop all tables and reinitialize database')
    args = parser.parse_args()

    if args.reset:
        confirm = input("Are you sure you want to reset the database? All data will be lost! (yes/no): ")
        if confirm.lower() == 'yes':
            reset_db()
        else:
            print("Database reset cancelled.")
    else:
        init_db()