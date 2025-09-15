"""
Test User model functionality including authentication and roles
"""
import unittest
from app import create_app, db
from app.models import User
from tests.conftest import BaseTestCase

class TestUserModel(BaseTestCase):
    """Test the User model"""
    
    def test_user_creation(self):
        """Test creating a user"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User',
            role='member'
        )
        user.set_password('testpassword')
        
        db.session.add(user)
        db.session.commit()
        
        # Verify user was created
        self.assertIsNotNone(user.id)
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.role, 'member')
        self.assertTrue(user.is_active)
        self.assertIsNotNone(user.created_at)
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Test password setting
        user.set_password('mypassword')
        self.assertIsNotNone(user.password_hash)
        self.assertNotEqual(user.password_hash, 'mypassword')
        
        # Test password checking
        self.assertTrue(user.check_password('mypassword'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_admin_role(self):
        """Test admin role functionality"""
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        
        member = User(
            username='member',
            email='member@example.com',
            first_name='Member',
            last_name='User',
            role='member'
        )
        
        self.assertTrue(admin.is_admin())
        self.assertFalse(member.is_admin())
    
    def test_user_repr(self):
        """Test user string representation"""
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        
        expected = '<User testuser>'
        self.assertEqual(str(user), expected)
    
    def test_unique_constraints(self):
        """Test that username and email must be unique"""
        user1 = User(
            username='testuser',
            email='test1@example.com',
            first_name='Test1',
            last_name='User1'
        )
        user1.set_password('password')
        db.session.add(user1)
        db.session.commit()
        
        # Try to create user with same username
        user2 = User(
            username='testuser',  # Same username
            email='test2@example.com',
            first_name='Test2',
            last_name='User2'
        )
        user2.set_password('password')
        db.session.add(user2)
        
        with self.assertRaises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # Try to create user with same email
        user3 = User(
            username='testuser3',
            email='test1@example.com',  # Same email
            first_name='Test3',
            last_name='User3'
        )
        user3.set_password('password')
        db.session.add(user3)
        
        with self.assertRaises(Exception):
            db.session.commit()

if __name__ == '__main__':
    unittest.main()
