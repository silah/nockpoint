#!/usr/bin/env python
"""
Test runner for Nockpoint multi-tenancy tests.
Runs all tests with coverage reporting.
"""
import sys
import pytest


def main():
    """Run all tests with pytest."""
    
    # pytest arguments
    args = [
        'tests/',  # Test directory
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--color=yes',  # Colored output
        '--durations=10',  # Show 10 slowest tests
    ]
    
    # Add coverage if available
    try:
        import pytest_cov
        args.extend([
            '--cov=app',  # Coverage for app directory
            '--cov-report=term-missing',  # Show missing lines
            '--cov-report=html:htmlcov',  # Generate HTML report
        ])
        print("Running tests with coverage...")
    except ImportError:
        print("pytest-cov not installed. Running tests without coverage.")
        print("Install with: pip install pytest-cov")
    
    # Run tests
    exit_code = pytest.main(args)
    
    if exit_code == 0:
        print("\n" + "="*70)
        print("✅ All tests passed!")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("❌ Some tests failed. See output above for details.")
        print("="*70)
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
