#!/usr/bin/env python
"""
Simple test runner for Nockpoint.
Alternative to run_all_tests.py with minimal options.
"""
import sys
import pytest


def main():
    """Run tests with basic configuration."""
    args = [
        'tests/',
        '-v',
        '--tb=short',
    ]
    
    # Add any command line arguments
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    return pytest.main(args)


if __name__ == '__main__':
    sys.exit(main())
