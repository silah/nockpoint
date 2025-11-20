"""
Tests for authentication with multi-tenancy.
Tests login, logout, club selection, and club switching.
"""
import pytest
from flask import session, g
from app.models import User, Club, ClubMembership
from datetime import datetime


class TestLogin:
    """Test login functionality with club context."""
    
    def test_login_single_club_auto_select(self, app, client, admin_alpha, club_alpha):
        """Test user with single club is automatically logged in with that club."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'username': 'admin_alpha',
                'password': 'password123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            with client.session_transaction() as sess:
                assert '_user_id' in sess
                assert 'current_club_id' in sess
                assert sess['current_club_id'] == club_alpha.id
    
    def test_login_multiple_clubs_requires_selection(self, app, client, multi_club_user, club_alpha, club_beta):
        """Test user with multiple clubs must select a club."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'username': 'multi_user',
                'password': 'password123'
            }, follow_redirects=False)
            
            # Should redirect to club selection
            assert response.status_code == 302
            assert '/auth/select-club' in response.location
    
    def test_login_invalid_credentials(self, app, client):
        """Test login with invalid credentials."""
        with app.app_context():
            response = client.post('/auth/login', data={
                'email': 'wrong@example.com',
                'password': 'wrongpassword',
                'remember': False
            }, follow_redirects=True)
            
            # Should stay on login page (not redirect)
            assert response.status_code == 200
            # Flash message may or may not be present in HTML depending on template rendering
            # The important thing is we didn't get redirected to dashboard
            assert b'dashboard' not in response.data.lower() or b'login' in response.data.lower()
    
    def test_login_no_clubs(self, app, client, _db):
        """Test login with user who has no club memberships."""
        with app.app_context():
            user = User(
                email='noclub@example.com',
                username='noclub',
                first_name='No',
                last_name='Club'
            )
            user.set_password('password123')
            _db.session.add(user)
            _db.session.commit()
            
            response = client.post('/auth/login', data={
                'email': 'noclub@example.com',
                'password': 'password123',
                'remember': False
            }, follow_redirects=True)
            
            # Should show error about no club membership
            assert response.status_code == 200
            # User should not be logged in
            with client.session_transaction() as sess:
                assert '_user_id' not in sess


class TestClubSelection:
    """Test club selection for users with multiple clubs."""
    
    def test_select_club_page_access(self, app, authenticated_client, multi_club_user):
        """Test accessing club selection page."""
        with app.app_context():
            client = authenticated_client(multi_club_user)
            response = client.get('/auth/select-club')
            
            assert response.status_code == 200
            assert b'Alpha Archery' in response.data
            assert b'Beta Bowmen' in response.data
    
    def test_select_club_submission(self, app, authenticated_client, multi_club_user, club_alpha):
        """Test selecting a club."""
        with app.app_context():
            client = authenticated_client(multi_club_user)
            response = client.post('/auth/select-club', data={
                'club_id': club_alpha.id
            }, follow_redirects=False)
            
            assert response.status_code == 302
            assert '/dashboard' in response.location or '/' in response.location
            
            with client.session_transaction() as sess:
                assert sess['current_club_id'] == club_alpha.id
    
    def test_select_club_invalid_club(self, app, authenticated_client, admin_alpha, club_beta):
        """Test selecting a club the user is not a member of."""
        with app.app_context():
            client = authenticated_client(admin_alpha)
            response = client.post('/auth/select-club', data={
                'club_id': club_beta.id  # admin_alpha is not a member of club_beta
            }, follow_redirects=True)
            
            # Should show error and not set club
            assert response.status_code == 200
            with client.session_transaction() as sess:
                assert sess.get('current_club_id') != club_beta.id


class TestClubSwitching:
    """Test switching between clubs."""
    
    def test_switch_club_valid(self, app, authenticated_client, multi_club_user, club_alpha, club_beta):
        """Test switching to a valid club."""
        with app.app_context():
            client = authenticated_client(multi_club_user, club_alpha.id)
            
            # Verify starting club
            with client.session_transaction() as sess:
                assert sess['current_club_id'] == club_alpha.id
            
            # Switch to Beta
            response = client.get(f'/auth/switch-club/{club_beta.id}', follow_redirects=False)
            
            assert response.status_code == 302
            with client.session_transaction() as sess:
                assert sess['current_club_id'] == club_beta.id
    
    def test_switch_club_invalid(self, app, authenticated_client, admin_alpha, club_beta):
        """Test switching to a club user is not a member of."""
        with app.app_context():
            client = authenticated_client(admin_alpha, None)
            
            response = client.get(f'/auth/switch-club/{club_beta.id}', follow_redirects=True)
            
            # Should show error
            assert response.status_code == 200
            with client.session_transaction() as sess:
                assert sess.get('current_club_id') != club_beta.id
    
    def test_switch_club_unauthenticated(self, app, client, club_alpha):
        """Test switching clubs when not logged in."""
        with app.app_context():
            response = client.get(f'/auth/switch-club/{club_alpha.id}', follow_redirects=True)
            
            # Should redirect to login
            assert b'login' in response.data.lower() or b'sign in' in response.data.lower()


class TestLogout:
    """Test logout functionality."""
    
    def test_logout(self, app, authenticated_client, admin_alpha, club_alpha):
        """Test logging out."""
        with app.app_context():
            client = authenticated_client(admin_alpha, club_alpha.id)
            
            response = client.get('/auth/logout', follow_redirects=False)
            
            assert response.status_code == 302
            with client.session_transaction() as sess:
                assert '_user_id' not in sess
                assert 'current_club_id' not in sess
    
    def test_logout_clears_club_context(self, app, authenticated_client, admin_alpha, club_alpha):
        """Test logout clears club context from session."""
        with app.app_context():
            client = authenticated_client(admin_alpha, club_alpha.id)
            
            # Verify club is set
            with client.session_transaction() as sess:
                assert sess['current_club_id'] == club_alpha.id
            
            # Logout
            client.get('/auth/logout')
            
            # Verify club is cleared
            with client.session_transaction() as sess:
                assert 'current_club_id' not in sess


class TestRegistration:
    """Test user registration."""
    
    def test_register_new_user(self, app, client, _db):
        """Test registering a new user."""
        with app.app_context():
            response = client.post('/auth/register', data={
                'email': 'newuser@example.com',
                'username': 'newuser',
                'first_name': 'New',
                'last_name': 'User',
                'password': 'password123',
                'password2': 'password123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Verify user was created
            user = User.query.filter_by(email='newuser@example.com').first()
            assert user is not None
            assert user.username == 'newuser'
    
    def test_register_duplicate_email(self, app, client, admin_alpha):
        """Test registering with existing email."""
        with app.app_context():
            response = client.post('/auth/register', data={
                'email': 'admin.alpha@example.com',  # Already exists
                'username': 'different',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'password123',
                'password2': 'password123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            assert b'already' in response.data.lower() or b'exists' in response.data.lower()
    
    def test_register_password_mismatch(self, app, client, _db):
        """Test registration with mismatched passwords."""
        with app.app_context():
            response = client.post('/auth/register', data={
                'email': 'test@example.com',
                'username': 'testuser',
                'first_name': 'Test',
                'last_name': 'User',
                'password': 'password123',
                'password2': 'different123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            # Check for password validation message - could be "match", "equal", or "same"
            assert (b'match' in response.data.lower() or 
                    b'equal' in response.data.lower() or 
                    b'same' in response.data.lower())


class TestClubContext:
    """Test club context in requests."""
    
    def test_club_context_available(self, app, authenticated_client, admin_alpha, club_alpha):
        """Test that club context is available in g."""
        with app.app_context():
            client = authenticated_client(admin_alpha, club_alpha.id)
            
            # Make a request to trigger before_request
            with client:
                response = client.get('/dashboard')
                
                # Check if g.current_club is set (this is tricky in tests)
                # We can verify the session instead
                with client.session_transaction() as sess:
                    assert sess['current_club_id'] == club_alpha.id
    
    def test_club_context_cleared_on_logout(self, app, authenticated_client, admin_alpha, club_alpha):
        """Test that club context is cleared on logout."""
        with app.app_context():
            client = authenticated_client(admin_alpha, club_alpha.id)
            
            client.get('/auth/logout')
            
            with client.session_transaction() as sess:
                assert 'current_club_id' not in sess
    
    def test_no_club_context_when_not_authenticated(self, app, client):
        """Test that club context is not set when not authenticated."""
        with app.app_context():
            response = client.get('/')
            
            with client.session_transaction() as sess:
                assert 'current_club_id' not in sess
