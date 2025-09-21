#!/usr/bin/env python3
"""
Test script to verify the Flask app can be imported correctly
"""
import sys
import os

print("Python path:", sys.path)
print("Working directory:", os.getcwd())
print("Files in current directory:", os.listdir('.'))

try:
    print("Attempting to import app...")
    from app import create_app
    print("✅ Successfully imported create_app")
    
    app = create_app()
    print("✅ Successfully created Flask app")
    print("App name:", app.name)
    
    # Test if we can import app.py directly
    import app as app_module
    print("✅ Successfully imported app module")
    print("App instance exists:", hasattr(app_module, 'app'))
    
except Exception as e:
    print("❌ Error:", str(e))
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ All imports successful!")