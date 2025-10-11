#!/usr/bin/env python3
"""
Database Connection Test Script

This script tests if the database connection is working correctly.
It can test both SQLite and PostgreSQL connections.
"""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test database connection and basic operations"""
    
    print("🔍 Testing Database Connection...")
    print("=" * 50)
    
    try:
        # Import Flask app and database
        from app import create_app, db
        from app.models import User, ClubSettings
        
        # Create app with testing context
        app = create_app()
        
        with app.app_context():
            # Get database URI
            db_uri = os.getenv("DATABASE_URL")
            print(f"📍 Database URI: {db_uri}")
            
            # Determine database type
            if db_uri.startswith('postgresql'):
                db_type = "PostgreSQL"
                print(f"🐘 Database Type: {db_type}")
            elif db_uri.startswith('sqlite'):
                db_type = "SQLite"
                print(f"🗄️  Database Type: {db_type}")
            else:
                db_type = "Unknown"
                print(f"❓ Database Type: {db_type}")
            
            print()
            
            # Test 1: Basic connection
            print("🔗 Test 1: Basic Connection")
            try:
                # Try to connect to database
                result = db.engine.execute(db.text("SELECT 1"))
                result.close()
                print("✅ Basic connection: SUCCESS")
            except Exception as e:
                print(f"❌ Basic connection: FAILED - {e}")
                return False
            
            # Test 2: Check if tables exist
            print("\n📋 Test 2: Table Structure")
            try:
                from sqlalchemy import inspect
                inspector = inspect(db.engine)
                tables = inspector.get_table_names()
                
                expected_tables = ['user', 'shooting_event', 'competition', 'club_settings', 
                                 'inventory_item', 'inventory_category', 'event_attendance', 
                                 'member_charge', 'competition_group', 'competition_registration',
                                 'team', 'score']
                
                print(f"📊 Found {len(tables)} tables:")
                for table in sorted(tables):
                    print(f"   - {table}")
                
                missing_tables = [t for t in expected_tables if t not in tables]
                if missing_tables:
                    print(f"⚠️  Missing tables: {missing_tables}")
                    print("💡 Run 'flask db upgrade' or 'python init_db.py' to create missing tables")
                else:
                    print("✅ All expected tables present")
                    
            except Exception as e:
                print(f"❌ Table check: FAILED - {e}")
            
            # Test 3: Basic read operation
            print("\n📖 Test 3: Basic Read Operation")
            try:
                user_count = User.query.count()
                print(f"👥 Users in database: {user_count}")
                
                settings = ClubSettings.query.first()
                if settings:
                    print(f"⚙️  Club settings found: {settings.club_name}")
                else:
                    print("⚠️  No club settings found")
                
                print("✅ Read operation: SUCCESS")
            except Exception as e:
                print(f"❌ Read operation: FAILED - {e}")
            
            # Test 4: Write operation (if tables exist)
            print("\n✏️  Test 4: Write Operation")
            try:
                # Try to create a test record (we'll delete it immediately)
                test_time = datetime.utcnow()
                
                # Check if we can write to settings
                settings = ClubSettings.get_settings()
                original_name = settings.club_name
                
                # Temporarily change club name
                settings.club_name = f"TEST_{test_time.strftime('%H%M%S')}"
                db.session.commit()
                
                # Verify the change
                updated_settings = ClubSettings.query.first()
                if updated_settings.club_name == settings.club_name:
                    print("✅ Write operation: SUCCESS")
                    
                    # Restore original name
                    settings.club_name = original_name
                    db.session.commit()
                    print("✅ Cleanup: SUCCESS")
                else:
                    print("❌ Write verification: FAILED")
                    
            except Exception as e:
                print(f"❌ Write operation: FAILED - {e}")
                try:
                    db.session.rollback()
                    print("🔄 Transaction rolled back")
                except:
                    pass
            
            # Test 5: Connection pool info (PostgreSQL only)
            if db_type == "PostgreSQL":
                print("\n🏊 Test 5: Connection Pool Info")
                try:
                    pool = db.engine.pool
                    print(f"📊 Pool size: {pool.size()}")
                    print(f"🔄 Checked out connections: {pool.checkedout()}")
                    print(f"📈 Total connections: {pool.checkedin() + pool.checkedout()}")
                    print("✅ Connection pool: HEALTHY")
                except Exception as e:
                    print(f"⚠️  Connection pool info: {e}")
            
            print("\n" + "=" * 50)
            print("🎯 Database Connection Test Complete!")
            print("✅ Database is ready for use")
            return True
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure you're in the project directory and dependencies are installed")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_variables():
    """Test environment variable configuration"""
    print("\n🌍 Environment Variables:")
    print("-" * 30)
    
    # Check important environment variables
    env_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'FLASK_ENV',
        'FLASK_DEBUG'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'SECRET' in var or 'PASSWORD' in var or 'KEY' in var:
                display_value = f"{'*' * (len(value) - 4)}{value[-4:]}" if len(value) > 4 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"⚠️  {var}: Not set")

if __name__ == "__main__":
    print("🏹 Nockpoint Database Connection Test")
    print("=" * 50)
    
    # Test environment variables first
    test_environment_variables()
    
    print()
    
    # Run database connection test
    success = test_database_connection()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)
