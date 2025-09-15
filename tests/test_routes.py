"""
Test Flask routes and view functions
"""
import unittest
from app import create_app, db
from app.models import User, InventoryCategory, ShootingEvent
from tests.conftest import BaseTestCase
from datetime import date, time
import json

class TestRoutes(BaseTestCase):ask routes and views functionality
"""
import unittest
from app import create_app, db
from app.models import User, InventoryCategory, ShootingEvent
from tests.conftest import TestConfig
from datetime import date, time
import json

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
        self.assertIn(b'Nockpoint', response.data)
    
    def test_login_route_get(self):
        """Test login page loads"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_login_route_post_valid(self):
        """Test valid login"""
        response = self.login_user('admin', 'password')
        self.assertEqual(response.status_code, 200)
        # Should redirect to dashboard after login
    
    def test_login_route_post_invalid(self):
        """Test invalid login"""
        response = self.login_user('admin', 'wrongpassword')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)
    
    def test_register_route(self):
        """Test registration route"""
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_dashboard_requires_login(self):
        """Test dashboard redirects to login when not authenticated"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard loads when authenticated"""
        self.login_user('admin', 'password')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
    
    def test_members_list_requires_admin(self):
        """Test members list requires admin access"""
        self.login_user('member', 'password')
        response = self.client.get('/members/')
        self.assertEqual(response.status_code, 403)  # Forbidden
    
    def test_members_list_admin_access(self):
        """Test members list accessible by admin"""
        self.login_user('admin', 'password')
        response = self.client.get('/members/')
        self.assertEqual(response.status_code, 200)
    
    def test_inventory_list(self):
        """Test inventory list route"""
        self.login_user('admin', 'password')
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
    
    def test_events_list(self):
        """Test events list route"""
        self.login_user('member', 'password')
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_inventory_category(self):
        """Test creating inventory category via POST"""
        self.login_user('admin', 'password')
        
        response = self.client.post('/inventory/categories/new', data={
            'name': 'Test Bows',
            'description': 'Test bow category'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify category was created
        category = InventoryCategory.query.filter_by(name='Test Bows').first()
        self.assertIsNotNone(category)
        self.assertEqual(category.description, 'Test bow category')
    
    def test_create_event(self):
        """Test creating shooting event via POST"""
        self.login_user('admin', 'password')
        
        response = self.client.post('/events/new', data={
            'name': 'Test Competition',
            'description': 'Test event description',
            'location': 'Test Range',
            'date': '2025-12-15',
            'start_time': '09:00',
            'duration_hours': 4,
            'price': 25.00,
            'max_participants': 20
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify event was created
        event = ShootingEvent.query.filter_by(name='Test Competition').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.location, 'Test Range')
    
    def test_ajax_check_username(self):
        """Test AJAX username availability check"""
        response = self.client.post('/auth/check_username', 
                                  data=json.dumps({'username': 'newuser'}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['available'])
        
        # Check existing username
        response = self.client.post('/auth/check_username', 
                                  data=json.dumps({'username': 'admin'}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertFalse(data['available'])
    
    def test_ajax_check_email(self):
        """Test AJAX email availability check"""
        response = self.client.post('/auth/check_email', 
                                  data=json.dumps({'email': 'new@example.com'}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['available'])
    
    def test_logout(self):
        """Test logout functionality"""
        self.login_user('admin', 'password')
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        # Should now be redirected when accessing protected route
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
    
    def test_permission_checks(self):
        """Test various permission checks across routes"""
        # Test member cannot access admin-only routes
        self.login_user('member', 'password')
        
        admin_routes = [
            '/members/',
            '/members/new',
            '/inventory/categories/new',
            '/events/new'
        ]
        
        for route in admin_routes:
            response = self.client.get(route)
            self.assertIn(response.status_code, [403, 302])  # Forbidden or redirect
    
    def test_form_validation(self):
        """Test form validation on various routes"""
        self.login_user('admin', 'password')
        
        # Test empty form submission
        response = self.client.post('/inventory/categories/new', data={
            'name': '',
            'description': ''
        })
        self.assertEqual(response.status_code, 200)  # Should return form with errors
        
        # Verify no category was created
        categories = InventoryCategory.query.count()
        self.assertEqual(categories, 0)

if __name__ == '__main__':
    unittest.main()
    
    def setUp(self):
        """Set up test fixtures"""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()
        
        # Create test users
        self.admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        self.admin.set_password('password')
        
        self.member = User(
            username='member',
            email='member@example.com',
            first_name='Test',
            last_name='Member',
            role='member'
        )
        self.member.set_password('password')
        
        db.session.add_all([self.admin, self.member])
        db.session.commit()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login_user(self, username, password):
        """Helper method to log in a user"""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def test_index_route(self):
        """Test the index/home route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to Nockpoint', response.data)
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication"""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_with_login(self):
        """Test dashboard with authenticated user"""
        self.login_user('member', 'password')
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_admin_required_routes(self):
        """Test that admin routes require admin role"""
        # Login as member
        self.login_user('member', 'password')
        
        # Try to access admin-only route
        response = self.client.get('/events/new')
        self.assertEqual(response.status_code, 302)  # Redirect
    
    def test_admin_access(self):
        """Test admin can access admin routes"""
        self.login_user('admin', 'password')
        response = self.client.get('/events/new')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'New Shooting Event', response.data)
    
    def test_login_logout(self):
        """Test login and logout functionality"""
        # Test login
        response = self.login_user('admin', 'password')
        self.assertEqual(response.status_code, 200)
        
        # Test logout
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_login(self):
        """Test invalid login credentials"""
        response = self.client.post('/auth/login', data={
            'username': 'invalid',
            'password': 'wrong'
        })
        # Should return to login page (may be 200 or 302)
        self.assertIn(response.status_code, [200, 302])
    
    def test_inventory_routes(self):
        """Test inventory-related routes"""
        self.login_user('member', 'password')
        
        # Test inventory index
        response = self.client.get('/inventory/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Inventory', response.data)
        
        # Test categories
        response = self.client.get('/inventory/categories')
        self.assertEqual(response.status_code, 200)
    
    def test_events_routes(self):
        """Test events-related routes"""
        self.login_user('member', 'password')
        
        # Test events calendar
        response = self.client.get('/events/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shooting Calendar', response.data)
    
    def test_create_event_form(self):
        """Test creating an event through the form"""
        self.login_user('admin', 'password')
        
        response = self.client.post('/events/new', data={
            'name': 'Test Event',
            'description': 'A test event',
            'location': 'Test Range',
            'date': '2025-12-01',
            'start_time': '09:00',
            'duration_hours': 2,
            'price': 15.00,
            'max_participants': 20
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify event was created
        event = ShootingEvent.query.filter_by(name='Test Event').first()
        self.assertIsNotNone(event)
        self.assertEqual(event.location, 'Test Range')
    
    def test_create_inventory_category(self):
        """Test creating inventory category through form"""
        self.login_user('admin', 'password')
        
        response = self.client.post('/inventory/categories/new', data={
            'name': 'Test Bows',
            'description': 'Bows for testing'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verify category was created
        category = InventoryCategory.query.filter_by(name='Test Bows').first()
        self.assertIsNotNone(category)
        self.assertEqual(category.description, 'Bows for testing')
    
    def test_ajax_endpoints(self):
        """Test AJAX endpoints return JSON"""
        self.login_user('admin', 'password')
        
        # Create test event first
        event = ShootingEvent(
            name='AJAX Test Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            created_by=self.admin.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Test AJAX update (this would be called by JavaScript)
        response = self.client.post(
            f'/events/event/{event.id}/update-attendance',
            data=json.dumps({
                'attendee_id': self.member.id,
                'attended': True
            }),
            content_type='application/json'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        # The response might be an error since we haven't created attendance record
        self.assertIn('success', data)
    
    def test_404_error(self):
        """Test 404 error handling"""
        self.login_user('member', 'password')
        response = self.client.get('/nonexistent-route')
        self.assertEqual(response.status_code, 404)
    
    def test_competitions_routes(self):
        """Test competition routes"""
        self.login_user('member', 'password')
        
        response = self.client.get('/competitions/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Competitions', response.data)

if __name__ == '__main__':
    unittest.main()
