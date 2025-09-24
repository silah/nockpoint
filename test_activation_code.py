#!/usr/bin/env python3
"""
Test script for activation code functionality
"""
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models import User, ClubSettings
from app.forms import RegistrationForm

def test_activation_code():
    """Test the activation code system"""
    
    # Set test environment
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("=== Testing Activation Code System ===")
        
        # Test 1: ClubSettings model has activation_code field
        print("✓ Testing ClubSettings model...")
        settings = ClubSettings.get_settings()
        settings.activation_code = "TEST123"
        db.session.commit()
        
        # Retrieve and verify
        settings = ClubSettings.get_settings()
        assert settings.activation_code == "TEST123"
        print("✓ ClubSettings.activation_code field working")
        
        # Test 2: Registration form validation
        print("✓ Testing form validation...")
        
        with app.test_request_context():
            # Test with correct activation code
            form_data = {
                'username': 'testuser',
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'membership_type': 'monthly',
                'activation_code': 'TEST123',
                'password': 'password123',
                'password2': 'password123',
                'csrf_token': 'test'
            }
            
            form = RegistrationForm(data=form_data)
            # Manually set CSRF token to avoid validation error in test
            form.csrf_token.data = 'test'
            
            # Test validation without CSRF for our specific field
            try:
                form.validate_activation_code(form.activation_code)
                print("✓ Valid activation code passes validation")
            except Exception as e:
                print(f"✗ Valid activation code failed: {e}")
                return False
            
            # Test with invalid activation code
            form_data['activation_code'] = 'WRONG'
            form = RegistrationForm(data=form_data)
            form.csrf_token.data = 'test'
            
            try:
                form.validate_activation_code(form.activation_code)
                print("✗ Invalid activation code should fail validation")
                return False
            except Exception as e:
                if "Invalid activation code" in str(e):
                    print("✓ Invalid activation code correctly rejected")
                else:
                    print(f"✗ Wrong error message: {e}")
                    return False
        
        # Test 3: No activation code set (registration disabled)
        print("✓ Testing disabled registration...")
        settings.activation_code = None
        db.session.commit()
        
        with app.test_request_context():
            form_data['activation_code'] = 'ANYTHING'
            form = RegistrationForm(data=form_data)
            form.csrf_token.data = 'test'
            
            try:
                form.validate_activation_code(form.activation_code)
                print("✗ Should fail when no activation code is set")
                return False
            except Exception as e:
                if "Registration is currently disabled" in str(e):
                    print("✓ Registration correctly disabled when no code set")
                else:
                    print(f"✗ Wrong error message: {e}")
                    return False
        
        print("\n✅ All activation code tests passed!")
        return True

if __name__ == '__main__':
    success = test_activation_code()
    sys.exit(0 if success else 1)