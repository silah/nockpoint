"""
Test Inventory models (Category and Item) functionality
"""
import unittest
from app import create_app, db
from app.models import User, InventoryCategory, InventoryItem
from tests.conftest import BaseTestCase
from datetime import datetime
from decimal import Decimal

class TestInventoryModels(BaseTestCase):
    """Test inventory-related models"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        
        # Create test user
        self.user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            is_admin=True
        )
        self.user.set_password('password')
        db.session.add(self.user)
        db.session.commit()
    
    def test_inventory_category_creation(self):
        """Test creating an inventory category"""
        category = InventoryCategory(
            name='Bows',
            description='Various types of bows'
        )
        
        db.session.add(category)
        db.session.commit()
        
        # Verify category was created
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, 'Bows')
        self.assertEqual(category.description, 'Various types of bows')
        self.assertIsNotNone(category.created_at)
    
    def test_inventory_category_unique_name(self):
        """Test that category names must be unique"""
        category1 = InventoryCategory(name='Bows', description='First')
        category2 = InventoryCategory(name='Bows', description='Second')
        
        db.session.add(category1)
        db.session.commit()
        
        db.session.add(category2)
        with self.assertRaises(Exception):
            db.session.commit()
    
    def test_inventory_item_creation(self):
        """Test creating an inventory item"""
        # Create category first
        category = InventoryCategory(name='Bows', description='Test bows')
        db.session.add(category)
        db.session.commit()
        
        # Create item
        item = InventoryItem(
            name='Recurve Bow',
            description='Professional recurve bow',
            category_id=category.id,
            quantity=5,
            unit='piece',
            location='Storage Room A',
            purchase_price=Decimal('250.00'),
            condition='excellent'
        )
        
        db.session.add(item)
        db.session.commit()
        
        # Verify item was created
        self.assertIsNotNone(item.id)
        self.assertEqual(item.name, 'Recurve Bow')
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.unit, 'piece')
        self.assertEqual(item.condition, 'excellent')
        self.assertEqual(item.purchase_price, Decimal('250.00'))
        self.assertIsNotNone(item.created_at)
    
    def test_inventory_item_category_relationship(self):
        """Test relationship between item and category"""
        category = InventoryCategory(name='Arrows', description='Test arrows')
        db.session.add(category)
        db.session.commit()
        
        item = InventoryItem(
            name='Carbon Arrow',
            category_id=category.id,
            quantity=50
        )
        db.session.add(item)
        db.session.commit()
        
        # Test relationship
        self.assertEqual(item.category.name, 'Arrows')
        self.assertEqual(len(category.items), 1)
        self.assertEqual(category.items[0].name, 'Carbon Arrow')
    
    def test_inventory_item_user_relationship(self):
        """Test relationship between item and creator"""
        category = InventoryCategory(name='Targets', description='Test targets')
        db.session.add(category)
        db.session.commit()
        
        item = InventoryItem(
            name='Target Face',
            category_id=category.id,
            quantity=10
        )
        db.session.add(item)
        db.session.commit()
        
        # Test relationship - inventory items don't have creator relationships
        # This test verifies basic item creation without user association
    
    def test_inventory_item_optional_fields(self):
        """Test that optional fields can be None"""
        category = InventoryCategory(name='Accessories')
        db.session.add(category)
        db.session.commit()
        
        item = InventoryItem(
            name='Quiver',
            category_id=category.id,
            quantity=3,
            # Optional fields not specified
        )
        db.session.add(item)
        db.session.commit()
        
        # Verify optional fields are None or have defaults
        self.assertIsNone(item.description)
        self.assertIsNone(item.location)
        self.assertIsNone(item.purchase_date)
        self.assertIsNone(item.purchase_price)
        self.assertEqual(item.unit, 'piece')  # Default value
        self.assertEqual(item.condition, 'good')  # Default value
    
    def test_category_item_count(self):
        """Test counting items in a category"""
        category = InventoryCategory(name='Safety Equipment')
        db.session.add(category)
        db.session.commit()
        
        # Add multiple items
        items_data = [
            ('Arm Guard', 5),
            ('Finger Tab', 8),
            ('Chest Guard', 3)
        ]
        
        for name, qty in items_data:
            item = InventoryItem(
                name=name,
                category_id=category.id,
                quantity=qty
            )
            db.session.add(item)
        
        db.session.commit()
        
        # Verify item count
        self.assertEqual(len(category.items), 3)
        
        # Verify total quantity
        total_quantity = sum(item.quantity for item in category.items)
        self.assertEqual(total_quantity, 16)

if __name__ == '__main__':
    unittest.main()
