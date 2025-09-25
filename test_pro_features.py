#!/usr/bin/env python3
"""
Test script for Pro Feature System
"""
from app import create_app, db
from app.models import ClubSettings
from app.pro_features import *

def test_pro_features():
    app = create_app()
    
    with app.app_context():
        print("=== Testing Pro Feature System ===\n")
        
        # Get club settings
        settings = ClubSettings.get_settings()
        
        print(f"Initial pro status: {settings.is_pro_active()}")
        print(f"Pro expires at: {settings.pro_expires_at}")
        
        # Test checking a feature when pro is disabled
        print(f"\nTesting feature 'advanced_inventory' when pro disabled:")
        print(f"Has feature: {settings.has_pro_feature('advanced_inventory')}")
        
        # Enable pro
        print("\n--- Enabling Pro Subscription ---")
        settings.is_pro_enabled = True
        # Enable specific features
        settings.pro_features_enabled = ['advanced_inventory', 'member_analytics', 'advanced_competitions']
        db.session.commit()
        
        print(f"Pro active: {settings.is_pro_active()}")
        print(f"Has 'advanced_inventory': {settings.has_pro_feature('advanced_inventory')}")
        print(f"Has 'member_analytics': {settings.has_pro_feature('member_analytics')}")
        print(f"Has 'financial_reporting': {settings.has_pro_feature('financial_reporting')}")
        
        # Test pro status
        status = settings.get_pro_status()
        print(f"\nPro Status: {status}")
        
        # Test feature constants
        print(f"\n--- Available Pro Features ---")
        for feature_key, feature_info in PRO_FEATURES.items():
            print(f"- {feature_info['name']} ({feature_key})")
            print(f"  Category: {feature_info['category']}")
            print(f"  Description: {feature_info['description'][:50]}...")
            print()
        
        # Test template functions (simulate)
        print("--- Testing Helper Functions ---")
        print(f"check_pro_feature('advanced_inventory'): {check_pro_feature('advanced_inventory')}")
        print(f"is_pro_feature_available('advanced_inventory'): {is_pro_feature_available('advanced_inventory')}")
        print(f"is_pro_feature_available('fake_feature'): {is_pro_feature_available('fake_feature')}")
        
        print("\n=== Pro Feature System Test Complete ===")

if __name__ == '__main__':
    test_pro_features()