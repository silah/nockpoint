#!/usr/bin/env python3
"""
Setup test data for inventory categories
"""

import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import InventoryCategory

def setup_categories():
    """Create basic inventory categories"""
    app = create_app()
    
    with app.app_context():
        # Create categories if they don't exist
        categories = [
            {'name': 'Bows', 'description': 'Recurve, compound, longbows and other bow types'},
            {'name': 'Arrows', 'description': 'Arrows, shafts, points, nocks, and fletching'},
            {'name': 'Targets', 'description': 'Target faces, stands, and target accessories'},
            {'name': 'Safety Equipment', 'description': 'Arm guards, finger tabs, chest guards'},
            {'name': 'Accessories', 'description': 'Quivers, bow strings, tools, and other accessories'}
        ]
        
        for cat_data in categories:
            existing = InventoryCategory.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = InventoryCategory(
                    name=cat_data['name'],
                    description=cat_data['description']
                )
                db.session.add(category)
                print(f"✅ Created category: {cat_data['name']}")
            else:
                print(f"⚠️  Category already exists: {cat_data['name']}")
        
        db.session.commit()
        print("\n🎯 Category setup complete!")

if __name__ == '__main__':
    print("Setting up inventory categories...")
    setup_categories()
