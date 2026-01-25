#!/usr/bin/env python
"""
Create an admin user for the default club.

Usage:
    python create_admin.py
"""

from app import create_app, db
from app.models import Club, ClubMembership, User
from werkzeug.security import generate_password_hash
from datetime import datetime
import sys

def create_admin_user():
    """Create admin user and club if needed"""
    
    app = create_app()
    with app.app_context():
        # Check if default club exists, create if not
        default_club = Club.query.filter_by(slug='default').first()
        if not default_club:
            print("Creating default club...")
            default_club = Club(
                name="Default Club",
                slug="default",
                description="Default archery club",
                email="admin@example.com",
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.session.add(default_club)
            db.session.commit()
            print(f"✓ Created club: {default_club.name}")
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            return
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username="admin",
            email="admin@example.com",
            password_hash=generate_password_hash("admin123"),
            first_name="Admin",
            last_name="User",
            is_active=True
        )
        db.session.add(admin)
        db.session.flush()
        
        # Create club membership
        membership = ClubMembership(
            user_id=admin.id,
            club_id=default_club.id,
            role='admin',
            is_active=True,
            joined_at=datetime.utcnow()
        )
        db.session.add(membership)
        db.session.commit()
        
        print()
        print("✓ Admin user created successfully!")
        print()
        print("Login credentials:")
        print("  Username: admin")
        print("  Password: admin123")
        print()

if __name__ == '__main__':
    try:
        create_admin_user()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
