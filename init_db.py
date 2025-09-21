#!/usr/bin/env python3
"""
Database initialization script for Docker container
Creates all tables and adds initial admin user
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import User

def init_database():
    """Initialize database with tables and admin user"""
    
    # Create Flask app
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        
        # Create all tables
        db.create_all()
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='archer').first()
        
        if not admin_user:
            print("Creating admin user 'archer'...")
            
            # Create admin user
            admin_user = User(
                username='archer',
                email='admin@nockpoint.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                membership_type='annual',
                is_active=True
            )
            admin_user.set_password('nockpoint123')
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("✅ Admin user created successfully!")
            print("   Username: archer")
            print("   Password: nockpoint123")
            print("   Role: admin")
        else:
            print("ℹ️  Admin user 'archer' already exists")
        
        print("✅ Database initialization completed!")

if __name__ == '__main__':
    init_database()