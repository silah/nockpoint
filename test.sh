#!/bin/bash
# Simple test runner script for Nockpoint Archery Club Management System

echo "🏹 Nockpoint Test Suite Runner 🏹"
echo "=================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found"
    exit 1
fi

# Change to script directory
cd "$(dirname "$0")"

# Check if tests directory exists
if [ ! -d "tests" ]; then
    echo "❌ Tests directory not found"
    exit 1
fi

# Run the tests
echo "Starting test execution..."
echo

python3 run_tests.py "$@"
exit_code=$?

echo
if [ $exit_code -eq 0 ]; then
    echo "🎯 All tests completed successfully!"
else
    echo "💥 Some tests failed. Check output above for details."
fi

exit $exit_code
