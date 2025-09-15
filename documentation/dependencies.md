# Dependencies Documentation

## Overview

The Nockpoint Archery Club Management System uses carefully selected Python packages to provide robust functionality while maintaining security and performance.

**Requirements File**: `requirements.txt`

## Core Dependencies

### Flask Framework
```
Flask==2.3.3
```

**Purpose**: Main web framework  
**Why This Version**: Stable release with security patches  
**Features Used**:
- Application factory pattern
- Blueprint architecture
- Request/response handling
- Session management
- Template rendering with Jinja2

**Key Components**:
- `Flask` - Main application class
- `render_template` - Template rendering
- `request` - HTTP request data
- `redirect`, `url_for` - Navigation
- `flash` - User messaging
- `jsonify` - JSON responses

### Database Layer

#### Flask-SQLAlchemy
```
Flask-SQLAlchemy==3.0.5
```

**Purpose**: Database ORM and Flask integration  
**Features Used**:
- Model definition with declarative base
- Relationship mapping
- Query interface
- Session management
- Database connection handling

**Key Classes**:
- `db.Model` - Base model class
- `db.Column` - Column definitions
- `db.relationship` - Model relationships
- `db.ForeignKey` - Foreign key constraints

#### Flask-Migrate
```
Flask-Migrate==4.0.5
```

**Purpose**: Database schema versioning  
**Features Used**:
- Automatic migration generation
- Schema upgrade/downgrade
- Version control integration
- Production deployment support

**CLI Commands**:
- `flask db init` - Initialize migrations
- `flask db migrate` - Generate migration
- `flask db upgrade` - Apply migrations
- `flask db downgrade` - Rollback migrations

### Authentication & Authorization

#### Flask-Login
```
Flask-Login==0.6.3
```

**Purpose**: User session management  
**Features Used**:
- User authentication state
- Login/logout functionality
- Remember me functionality
- Session protection

**Key Components**:
- `UserMixin` - User model integration
- `login_user()`, `logout_user()` - Session management
- `login_required` - Route protection decorator
- `current_user` - Current user proxy

### Form Handling

#### Flask-WTF
```
Flask-WTF==1.2.1
```

**Purpose**: Flask integration for WTForms  
**Features Used**:
- CSRF protection
- File upload handling
- Form validation integration
- Secure form rendering

**Key Classes**:
- `FlaskForm` - Base form class
- `CSRFProtect` - CSRF protection

#### WTForms
```
WTForms==3.1.1
```

**Purpose**: Form definition and validation  
**Features Used**:
- Field types (StringField, IntegerField, etc.)
- Validation rules
- Form rendering helpers
- Custom validation methods

**Field Types Used**:
- `StringField` - Text input
- `PasswordField` - Password input
- `IntegerField` - Numeric input
- `DecimalField` - Currency/precision numbers
- `DateField` - Date picker
- `TimeField` - Time picker
- `SelectField` - Dropdown selection
- `TextAreaField` - Multi-line text
- `BooleanField` - Checkboxes
- `SubmitField` - Form submission

**Validators Used**:
- `DataRequired()` - Required field validation
- `Email()` - Email format validation
- `Length()` - String length validation
- `NumberRange()` - Numeric range validation
- `EqualTo()` - Field comparison validation
- `Optional()` - Optional field validation

#### Email Validator
```
email-validator
```

**Purpose**: Email address validation  
**Integration**: Used by WTForms Email() validator  
**Features**: RFC-compliant email validation

### Security

#### Werkzeug
```
Werkzeug==2.3.7
```

**Purpose**: WSGI utilities and security functions  
**Features Used**:
- Password hashing (`generate_password_hash`, `check_password_hash`)
- Secure filename handling
- HTTP exception handling
- Development server

**Security Functions**:
```python
from werkzeug.security import generate_password_hash, check_password_hash

# In User model
def set_password(self, password):
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    return check_password_hash(self.password_hash, password)
```

### Database Drivers

#### PostgreSQL Support
```
psycopg2-binary==2.9.7
```

**Purpose**: PostgreSQL database adapter  
**When Used**: Production deployments with PostgreSQL  
**Features**: Binary distribution for easier installation  
**Note**: SQLite used for development, PostgreSQL for production

### Configuration Management

#### Python-dotenv
```
python-dotenv==1.0.0
```

**Purpose**: Environment variable loading  
**Features Used**:
- `.env` file support
- Environment-specific configuration
- Secret key management
- Database URL configuration

**Usage**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fallback-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
```

## Development Dependencies

### Testing Framework
While not included in requirements.txt, the system supports testing with:
- `pytest` - Testing framework
- `pytest-flask` - Flask testing utilities
- `coverage` - Code coverage analysis

### Development Tools
Recommended development tools:
- `flask-shell-ipython` - Enhanced Flask shell
- `flask-debugtoolbar` - Debug information
- `watchdog` - File watching for auto-reload

## Frontend Dependencies

### CSS Framework
```html
<!-- Bootstrap 5.1.3 via CDN -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
```

**Features Used**:
- Responsive grid system
- Form styling
- Navigation components
- Modal dialogs
- Alert messages
- Card layouts
- Utility classes

### Icons
```html
<!-- Bootstrap Icons 1.7.2 via CDN -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css" rel="stylesheet">
```

**Icons Used**:
- `bi-bullseye` - Logo/brand
- `bi-calendar3` - Events
- `bi-people` - Members
- `bi-box-seam` - Inventory
- `bi-currency-dollar` - Payments
- `bi-person-circle` - User profile
- `bi-gear` - Settings/admin

### JavaScript
```html
<!-- Bootstrap JS 5.1.3 via CDN -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
```

**Features Used**:
- Modal dialogs
- Dropdown menus
- Collapsible navigation
- Alert dismissal
- Form validation feedback

## Security Considerations

### Package Security
- All packages pinned to specific versions
- Regular security updates required
- Vulnerability scanning recommended

### Critical Security Packages
1. **Werkzeug**: Password hashing and security utilities
2. **Flask-WTF**: CSRF protection
3. **Flask-Login**: Session security
4. **Flask-SQLAlchemy**: SQL injection prevention

### Environment Variables
Sensitive configuration stored in environment variables:
```bash
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:pass@localhost/dbname
FLASK_ENV=production
```

## Production Considerations

### WSGI Server
Production deployment requires a WSGI server:
- **Gunicorn** (recommended): `gunicorn -w 4 -b 0.0.0.0:8000 app:app`
- **uWSGI**: Alternative WSGI server
- **Waitress**: Windows-compatible option

### Reverse Proxy
Use nginx or Apache as reverse proxy:
- SSL termination
- Static file serving
- Load balancing
- Request buffering

### Database
Production database recommendations:
- **PostgreSQL**: Primary recommendation
- **MySQL**: Alternative option
- Connection pooling
- Regular backups

### Caching
Consider adding caching layers:
- **Redis**: Session storage and caching
- **Memcached**: Alternative caching solution
- **Flask-Caching**: Application-level caching

## Version Compatibility

### Python Version
- **Minimum**: Python 3.8+
- **Recommended**: Python 3.10+
- **Tested**: Python 3.9, 3.10, 3.11

### Browser Support
Frontend components support:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Installation

### Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Production Setup
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql postgresql-contrib nginx

# Create application user
sudo useradd -m -s /bin/bash nockpoint

# Setup application
sudo -u nockpoint python -m venv /home/nockpoint/venv
sudo -u nockpoint /home/nockpoint/venv/bin/pip install -r requirements.txt

# Configure database
sudo -u postgres createdb nockpoint
sudo -u postgres createuser nockpoint

# Setup environment
echo "SECRET_KEY=$(openssl rand -base64 32)" | sudo tee /home/nockpoint/.env
echo "DATABASE_URL=postgresql://nockpoint:password@localhost/nockpoint" | sudo tee -a /home/nockpoint/.env
```

## Dependency Management

### Updating Dependencies
```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade flask

# Update all packages (carefully)
pip install --upgrade -r requirements.txt

# Generate new requirements
pip freeze > requirements.txt
```

### Security Updates
Regular security monitoring:
- Subscribe to security advisories for all dependencies
- Use tools like `safety` to check for vulnerabilities
- Update dependencies promptly when security issues are discovered

### Version Pinning Strategy
- **Exact versions** for production stability
- **Compatible versions** (`~=2.3.0`) for patch updates
- **Minimum versions** (`>=2.3.0`) for development flexibility

## Troubleshooting

### Common Issues

**ImportError for email_validator**
```bash
pip install email-validator
```

**Database connection errors**
- Check DATABASE_URL environment variable
- Verify database server is running
- Confirm connection credentials

**CSRF token errors**
- Ensure forms include `{{ form.hidden_tag() }}`
- Check CSRF token in AJAX requests
- Verify SECRET_KEY is set

**Permission errors**
- Check file permissions on application directory
- Verify database user permissions
- Confirm environment variable access
