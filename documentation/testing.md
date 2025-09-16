# Testing Documentation

## Testing Strategy

The Nockpoint application employs a comprehensive testing strategy covering unit tests, integration tests, and manual testing procedures to ensure reliability and maintainability.

## Test Structure

### Test Configuration
```python
# tests/conftest.py
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
```

### Base Test Case
```python
class BaseTestCase(unittest.TestCase):
    def setUp(self):
        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False
        }
        self.app = create_app(config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
```

## Test Categories

### 1. Model Tests (`tests/test_models_*.py`)

#### User Model Tests
- Password hashing and verification
- Role checking (admin/member)
- User authentication flow

#### Inventory Model Tests
- Category-item relationships
- JSON attribute storage and retrieval
- Inventory tracking calculations

#### Event Model Tests
- Event creation and validation
- Attendance tracking
- Charge generation and payment tracking

#### Competition Model Tests
- Competition lifecycle management
- Team generation algorithms
- Scoring calculations and validation
- Results generation and ranking

### 2. Integration Tests

#### Competition Workflow Tests (`tests/test_complete_competition.py`)
```python
def test_complete_competition_with_partial_scores(self):
    """Test completing competition when some participants have partial scores"""
    # Creates competition with partial scoring
    # Tests auto-fill of missing arrows with 0-point scores
    # Verifies final completion status and statistics
```

#### Authentication Flow Tests
- Login/logout functionality
- Role-based access control
- Session management

#### Form Processing Tests
- Input validation
- CSRF protection
- Error handling and user feedback

### 3. API Endpoint Tests

#### Competition API Tests
- Competition CRUD operations
- Team generation endpoints
- Scoring submission and validation
- Results retrieval and formatting

#### Event Management Tests
- Event creation and modification
- Attendance management
- Payment processing integration

### 4. Frontend Tests

#### JavaScript Functionality
- Real-time score calculations
- Form validation and user feedback
- Dynamic UI updates

#### Template Rendering
- Jinja2 template processing
- Data presentation accuracy
- Responsive design validation

## Test Data Fixtures

### User Fixtures
```python
def create_admin_user():
    admin = User(
        username='admin',
        email='admin@test.com',
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password('password')
    return admin

def create_member_user():
    member = User(
        username='member',
        email='member@test.com',
        first_name='Member',
        last_name='User',
        role='member'
    )
    member.set_password('password')
    return member
```

### Competition Fixtures
```python
def create_test_competition():
    event = ShootingEvent(
        name='Test Competition Event',
        location='Test Range',
        date=date.today(),
        start_time=time(10, 0),
        created_by=1
    )
    
    competition = Competition(
        event_id=1,
        number_of_rounds=3,
        arrows_per_round=6,
        status='in_progress',
        created_by=1
    )
    
    return event, competition
```

## Running Tests

### Command Line Execution
```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_complete_competition

# Run with verbose output
python -m unittest tests.test_models_competitions -v

# Run specific test method
python -m unittest tests.test_complete_competition.CompleteCompetitionTestCase.test_complete_competition_with_partial_scores
```

### Test Coverage Analysis
```bash
# Install coverage tool
pip install coverage

# Run tests with coverage
coverage run -m unittest discover tests/
coverage report
coverage html  # Generate HTML coverage report
```

## Test Scenarios

### Critical Path Testing

#### 1. User Registration and Authentication
- New user registration
- Login with valid credentials
- Login with invalid credentials
- Password reset functionality
- Session timeout handling

#### 2. Competition Lifecycle
- Competition creation by admin
- Group setup and configuration
- Member registration for competition
- Team generation and target assignment
- Scoring process with multiple participants
- Competition completion with partial scores
- Results calculation and display

#### 3. Event Management
- Event creation and scheduling
- Member registration for events
- Attendance tracking
- Payment processing and charge management

#### 4. Inventory Management
- Category creation and management
- Item addition with custom attributes
- Stock tracking and updates
- Search and filtering functionality

### Edge Case Testing

#### Competition Edge Cases
- Competition with zero participants
- Incomplete scoring scenarios
- Maximum team size boundary conditions
- Multiple competitions on same event
- Competition deletion with existing data

#### Scoring Edge Cases
- Invalid score values (negative, > 10)
- Duplicate arrow score submissions
- Network interruption during scoring
- Multiple admins scoring simultaneously

#### Data Integrity Tests
- Foreign key constraint enforcement
- Cascade deletion behavior
- Unique constraint violations
- Data migration scenarios

## Performance Testing

### Database Performance
- Query optimization for large datasets
- Bulk operations efficiency
- Index effectiveness
- Connection pooling under load

### UI Responsiveness
- Page load times with large competition lists
- Real-time calculation performance
- Mobile device compatibility
- Concurrent user scenarios

## Security Testing

### Authentication Security
- Password strength requirements
- Session hijacking prevention
- CSRF token validation
- SQL injection prevention

### Authorization Testing
- Role-based access control enforcement
- Admin-only functionality protection
- Data access restrictions by user role

### Input Validation
- Form input sanitization
- File upload security
- XSS prevention
- Data type validation

## Continuous Integration

### Automated Test Execution
```yaml
# .github/workflows/tests.yml (if using GitHub Actions)
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.12
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m unittest discover tests/
```

### Test Environment Management
- Isolated test database per test run
- Environment variable configuration
- Test data cleanup procedures
- Parallel test execution support

## Debugging Test Failures

### Common Issues and Solutions

#### Database State Issues
```python
# Ensure proper cleanup in tearDown
def tearDown(self):
    db.session.remove()
    db.drop_all()
    self.app_context.pop()
```

#### Authentication Context
```python
# Mock login for protected routes
def login_as_admin(self):
    return self.client.post('/auth/login', data={
        'username': 'admin',
        'password': 'password'
    }, follow_redirects=True)
```

#### Template Rendering Issues
```python
# Check template context variables
with self.app.test_request_context():
    response = self.client.get('/competitions/1')
    self.assertEqual(response.status_code, 200)
```

## Test Documentation Standards

### Test Method Naming
```python
def test_[action]_[scenario]_[expected_result](self):
    """Clear docstring describing test purpose"""
    # Arrange - Set up test data
    # Act - Perform the action being tested
    # Assert - Verify expected outcomes
```

### Assertion Best Practices
- Use specific assertions (assertEqual, assertIn, assertTrue)
- Provide meaningful failure messages
- Test both positive and negative cases
- Verify side effects and state changes

### Test Data Management
- Use fixtures for common test data
- Avoid hard-coded values where possible
- Clean up test data after each test
- Use factory patterns for complex object creation

## Manual Testing Procedures

### User Acceptance Testing
1. Complete user journey testing
2. Cross-browser compatibility verification
3. Mobile responsiveness validation
4. Accessibility compliance checking

### Regression Testing Checklist
- [ ] User authentication flow
- [ ] Competition creation and management
- [ ] Scoring system functionality
- [ ] Results calculation accuracy
- [ ] Event management features
- [ ] Inventory tracking
- [ ] Payment processing
- [ ] Admin panel functionality

### Production Deployment Testing
- [ ] Environment configuration validation
- [ ] Database migration verification
- [ ] Static file serving
- [ ] Email notification functionality
- [ ] Backup and recovery procedures
- [ ] Performance monitoring setup
