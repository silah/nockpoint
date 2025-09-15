# Nockpoint Test Suite

This directory contains comprehensive tests for the Nockpoint Archery Club Management System to verify that all fields work and can be populated using the intended methods.

## Test Structure

### Test Files

- **`conftest.py`** - Test configuration and shared fixtures
- **`test_models_user.py`** - Tests for User model, authentication, roles
- **`test_models_inventory.py`** - Tests for InventoryCategory and InventoryItem models
- **`test_models_events.py`** - Tests for Event, EventAttendance, and EventCharge models
- **`test_models_competitions.py`** - Tests for Competition-related models
- **`test_routes.py`** - Tests for Flask routes and view functions

### Test Coverage

Each test file covers:
- **Model Creation**: Can instances be created with required fields?
- **Field Validation**: Do validation rules work correctly?
- **Relationships**: Are model relationships properly configured?
- **Business Logic**: Do custom methods and properties work as intended?
- **Database Operations**: Can records be saved, updated, and retrieved?

## Running Tests

### Quick Start

```bash
# Run all tests with simple output
./test.sh

# Run all tests with verbose output
./test.sh -v

# Run all tests with maximum verbosity
./test.sh -vv
```

### Using Python Directly

```bash
# Run all tests
python3 run_tests.py

# Run with verbose output
python3 run_tests.py --verbose

# Run specific test module
python3 run_tests.py --specific test_models_user

# List available test modules
python3 run_tests.py --list

# Disable colored output
python3 run_tests.py --no-color
```

### Test Output

The test runner provides:
- ✅ **Colored output** for easy identification of passed/failed tests
- 📊 **Summary statistics** showing total tests, successes, failures, errors
- 🔍 **Detailed failure information** when tests don't pass
- 📋 **Dependency checking** to ensure all required modules are available

## Test Categories

### User Model Tests (`test_models_user.py`)
- User creation and validation
- Password hashing and verification
- Role assignment and permissions
- Email uniqueness constraints
- User profile management

### Inventory Tests (`test_models_inventory.py`)
- Category creation with custom attributes
- Item creation and management
- Category-item relationships
- JSON field handling for flexible attributes
- Search and filtering capabilities

### Events Tests (`test_models_events.py`)
- Event creation and scheduling
- Attendance tracking and registration
- Charge calculation and management
- Event capacity and limits
- Admin and member permissions

### Competition Tests (`test_models_competitions.py`)
- Competition setup and configuration
- Division and class management
- Registration and participation
- Scoring and ranking systems
- Results calculation

### Route Tests (`test_routes.py`)
- Authentication and authorization
- CRUD operations via web interface
- Form validation and error handling
- AJAX endpoints
- Permission-based access control

## Writing New Tests

When adding new functionality, follow this pattern:

```python
import unittest
from tests.conftest import TestConfig
from app import create_app, db
from app.models import YourModel

class TestYourModel(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_your_functionality(self):
        # Your test code here
        pass

if __name__ == '__main__':
    unittest.main()
```

## Continuous Integration

These tests are designed to:
- Run in isolated environments (using in-memory SQLite)
- Not interfere with production data
- Provide clear pass/fail indicators
- Be easily integrated into CI/CD pipelines

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're running tests from the project root directory
2. **Database Errors**: Tests use in-memory SQLite, no external database needed
3. **Missing Dependencies**: Run `pip install -r requirements.txt` to install dependencies
4. **Permission Errors**: Ensure test files have proper permissions

### Getting Help

If tests fail:
1. Check the detailed error output in the test results
2. Verify all dependencies are installed
3. Ensure you're running from the correct directory
4. Check that the Flask app configuration is correct

## Best Practices

- Run tests before committing changes
- Add tests for new functionality
- Keep tests focused and independent
- Use descriptive test method names
- Document complex test scenarios
