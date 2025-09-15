#!/usr/bin/env python3
"""
Test runner for Nockpoint Archery Club Management System

This script runs all tests and provides a summary of results.
Usage: python run_tests.py [--verbose] [--specific-test]
"""

import sys
import os
import unittest
import importlib
from io import StringIO
import argparse
from datetime import datetime

# Add the parent directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ColoredTextTestResult(unittest.TextTestResult):
    """Custom test result class that adds color coding"""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.success_count = 0
        self.verbosity = verbosity
    
    def addSuccess(self, test):
        super().addSuccess(test)
        self.success_count += 1
        if self.verbosity > 1:
            self.stream.writeln(f"\033[92m✓ {self.getDescription(test)}\033[0m")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.verbosity > 1:
            self.stream.writeln(f"\033[91m✗ {self.getDescription(test)} - ERROR\033[0m")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.verbosity > 1:
            self.stream.writeln(f"\033[91m✗ {self.getDescription(test)} - FAIL\033[0m")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.verbosity > 1:
            self.stream.writeln(f"\033[93m~ {self.getDescription(test)} - SKIPPED: {reason}\033[0m")

class ColoredTextTestRunner(unittest.TextTestRunner):
    """Custom test runner with colored output"""
    
    resultclass = ColoredTextTestResult
    
    def run(self, test):
        result = super().run(test)
        
        # Print summary with colors
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        
        total_tests = result.testsRun
        errors = len(result.errors)
        failures = len(result.failures)
        skipped = len(result.skipped)
        successful = result.success_count
        
        print(f"Total Tests Run: {total_tests}")
        print(f"\033[92mSuccessful: {successful}\033[0m")
        
        if failures > 0:
            print(f"\033[91mFailures: {failures}\033[0m")
        if errors > 0:
            print(f"\033[91mErrors: {errors}\033[0m")
        if skipped > 0:
            print(f"\033[93mSkipped: {skipped}\033[0m")
        
        if errors > 0 or failures > 0:
            print(f"\n\033[91m❌ TESTS FAILED\033[0m")
            return_code = 1
        else:
            print(f"\n\033[92m✅ ALL TESTS PASSED\033[0m")
            return_code = 0
        
        print("="*70)
        return result, return_code

def discover_tests(test_dir="tests", pattern="test_*.py"):
    """Discover all test files"""
    loader = unittest.TestLoader()
    start_dir = test_dir
    suite = loader.discover(start_dir, pattern=pattern)
    return suite

def run_specific_test(test_name):
    """Run a specific test module or test case"""
    try:
        # Try to import the test module
        if not test_name.startswith('tests.'):
            test_name = f'tests.{test_name}'
        
        module = importlib.import_module(test_name)
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        return suite
    except ImportError as e:
        print(f"Error importing test module '{test_name}': {e}")
        return None

def check_dependencies():
    """Check if all required modules can be imported"""
    print("Checking dependencies...")
    
    required_modules = [
        'app',
        'app.models',
        'app.forms',
        'flask',
        'flask_sqlalchemy',
        'flask_login',
        'flask_wtf',
        'flask_migrate'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            importlib.import_module(module)
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing required modules: {', '.join(missing_modules)}")
        print("Please install missing dependencies before running tests.")
        return False
    
    print("✅ All dependencies available\n")
    return True

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run Nockpoint tests')
    parser.add_argument('--verbose', '-v', action='count', default=1,
                       help='Increase verbosity (use -vv for more verbose)')
    parser.add_argument('--specific', '-s', type=str,
                       help='Run specific test module (e.g., test_models_user)')
    parser.add_argument('--list', '-l', action='store_true',
                       help='List available test modules')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    
    args = parser.parse_args()
    
    # Header
    print("="*70)
    print("NOCKPOINT ARCHERY CLUB MANAGEMENT SYSTEM - TEST SUITE")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # List available tests if requested
    if args.list:
        print("Available test modules:")
        test_files = [f for f in os.listdir('tests') if f.startswith('test_') and f.endswith('.py')]
        for test_file in sorted(test_files):
            module_name = test_file[:-3]  # Remove .py extension
            print(f"  - {module_name}")
        return 0
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Determine which tests to run
    if args.specific:
        print(f"Running specific test: {args.specific}")
        suite = run_specific_test(args.specific)
        if suite is None:
            return 1
    else:
        print("Discovering and running all tests...")
        suite = discover_tests()
    
    # Choose runner based on color preference
    if args.no_color:
        runner = unittest.TextTestRunner(verbosity=args.verbose)
        result = runner.run(suite)
        return_code = 0 if result.wasSuccessful() else 1
    else:
        runner = ColoredTextTestRunner(verbosity=args.verbose)
        result, return_code = runner.run(suite)
    
    return return_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
