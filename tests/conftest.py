"""
Test configuration and fixtures for Nockpoint tests
"""
import os
import tempfile
import unittest
from app import create_app, db
from app.models import User, InventoryCategory, ShootingEvent
from datetime import datetime, date, time

class TestConfig:
    """Test configuration class"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False

class BaseTestCase(unittest.TestCase):
    """Base test case with common setup and teardown"""
    
    def setUp(self):
        """Set up test environment"""
        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False
        }
        self.app = create_app(config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_admin_user(self):
        """Create admin user for testing"""
        user = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

    def create_member_user(self):
        """Create regular member for testing"""
        user = User(
            username='member',
            email='member@test.com',
            first_name='Test',
            last_name='Member',
            is_admin=False
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

    def create_inventory_category(self):
        """Create test inventory category"""
        category = InventoryCategory(
            name='Test Bows',
            description='Bows for testing'
        )
        db.session.add(category)
        db.session.commit()
        return category

    def create_shooting_event(self, admin_user):
        """Create test shooting event"""
        event = ShootingEvent(
            name='Test Event',
            description='A test shooting event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            price=10.00,
            max_participants=20,
            created_by=admin_user.id
        )
        db.session.add(event)
        db.session.commit()
        return event
