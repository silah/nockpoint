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
from app.models import User, ClubSettings, InventoryCategory

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
        
        # Create default inventory categories
        print("Creating default inventory categories...")
        default_categories = [
            {'name': 'Bows', 'description': 'Recurve, compound, and traditional bows'},
            {'name': 'Arrows', 'description': 'Carbon, aluminum, and wooden arrows'},
            {'name': 'Targets', 'description': 'Target backstops, stands, and boss materials (straw, foam)'},
            {'name': 'Target Faces', 'description': 'Paper and plastic target faces in standard sizes (20, 40, 60, 80, 122 cm)'},
            {'name': 'Safety Equipment', 'description': 'Arm guards, finger tabs, chest guards'},
            {'name': 'Accessories', 'description': 'Quivers, bow stands, and other accessories'},
            {'name': 'Maintenance', 'description': 'Bow strings, wax, tools'},
            {'name': 'Arrow Consumables', 'description': 'Tips, vanes, feathers, nocks, shafts'},
        ]
        
        categories_created = 0
        for cat_data in default_categories:
            if not InventoryCategory.query.filter_by(name=cat_data['name']).first():
                category = InventoryCategory(**cat_data)
                db.session.add(category)
                categories_created += 1
        
        if categories_created > 0:
            db.session.commit()
            print(f"✅ Created {categories_created} inventory categories")
        else:
            print("ℹ️  All inventory categories already exist")

        # Set up default club settings with activation code
        settings = ClubSettings.get_settings()
        if not settings.activation_code:
            settings.activation_code = 'NOCKPOINT2025'
            db.session.commit()
            print("✅ Default activation code set: NOCKPOINT2025")
        else:
            print(f"ℹ️  Activation code already set: {settings.activation_code}")
        
        print("✅ Database initialization completed!")

if __name__ == '__main__':
    init_database()