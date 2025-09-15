"""
Test Flask routes and view functions
"""
import unittest
from app import create_app, db
from app.models import User, InventoryCategory, ShootingEvent
from tests.conftest import BaseTestCase
from datetime import date, time
import json

class TestRoutes(BaseTestCase):
    """Test Flask routes and views functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        
        # Create test users
        self.admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        self.admin.set_password('password')
        
        self.member = User(
            username='member',
            email='member@example.com',
            first_name='Test',
            last_name='Member',
            is_admin=False
        )
        self.member.set_password('password')
        
        db.session.add_all([self.admin, self.member])
        db.session.commit()
    
    def login_user(self, username, password):
        """Helper method to log in a user"""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def test_index_route(self):
        """Test the main index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_login_route_get(self):
        """Test login page loads"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects to login when not authenticated"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login

if __name__ == '__main__':
    unittest.main()
