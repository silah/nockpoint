# Configuration Guide

## Overview

The Nockpoint application uses environment-based configuration to manage settings across different deployment environments (development, testing, production).

## Configuration Structure

### Environment Variables

The application reads configuration from environment variables defined in a `.env` file:

```bash
# .env file template
# Flask Core Settings
SECRET_KEY=your-secret-key-generate-a-strong-one
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
DATABASE_URL=sqlite:///instance/nockpoint.db
# For PostgreSQL: postgresql://username:password@localhost:5432/nockpoint_db

# Security Settings
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600

# Application Settings
ITEMS_PER_PAGE=20
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216

# Email Settings (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/nockpoint.log
```

### Configuration Classes

```python
# config.py (example structure)
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///nockpoint.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # WTForms CSRF Protection
    WTF_CSRF_ENABLED = os.environ.get('WTF_CSRF_ENABLED', 'True').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = int(os.environ.get('WTF_CSRF_TIME_LIMIT', '3600'))
    
    # File Upload Settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    
    # Pagination
    ITEMS_PER_PAGE = int(os.environ.get('ITEMS_PER_PAGE', '20'))
    
    # Email Settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///nockpoint_dev.db'
    WTF_CSRF_ENABLED = False  # Disable for easier development

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise RuntimeError('DATABASE_URL must be set for production')

class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    
    # Disable email during testing
    MAIL_SUPPRESS_SEND = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
```

## Application Settings

### Core Flask Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `SECRET_KEY` | Flask secret key for sessions/CSRF | Required | All |
| `FLASK_ENV` | Flask environment mode | `development` | All |
| `FLASK_DEBUG` | Enable Flask debug mode | `False` | Development |

### Database Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `DATABASE_URL` | Database connection string | `sqlite:///nockpoint.db` | All |
| `SQLALCHEMY_TRACK_MODIFICATIONS` | Track object modifications | `False` | All |

**Database URL Formats:**
- SQLite: `sqlite:///path/to/database.db`
- PostgreSQL: `postgresql://user:password@host:port/database`
- MySQL: `mysql://user:password@host:port/database`

### Security Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `WTF_CSRF_ENABLED` | Enable CSRF protection | `True` | Prod/Test |
| `WTF_CSRF_TIME_LIMIT` | CSRF token expiry (seconds) | `3600` | All |

### File Upload Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `UPLOAD_FOLDER` | Upload directory path | `uploads` | All |
| `MAX_CONTENT_LENGTH` | Max file size (bytes) | `16777216` (16MB) | All |

### Pagination Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `ITEMS_PER_PAGE` | Items per page in lists | `20` | All |

### Email Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `MAIL_SERVER` | SMTP server hostname | None | Optional |
| `MAIL_PORT` | SMTP server port | `587` | Optional |
| `MAIL_USE_TLS` | Use TLS encryption | `True` | Optional |
| `MAIL_USERNAME` | SMTP username | None | Optional |
| `MAIL_PASSWORD` | SMTP password | None | Optional |

### Logging Settings

| Setting | Description | Default | Environment |
|---------|-------------|---------|-------------|
| `LOG_LEVEL` | Logging level | `INFO` | All |
| `LOG_FILE` | Log file path | `logs/nockpoint.log` | All |

## Environment-Specific Configuration

### Development Environment

```bash
# .env for development
SECRET_KEY=dev-secret-key
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///instance/nockpoint_dev.db
WTF_CSRF_ENABLED=False
LOG_LEVEL=DEBUG
```

### Production Environment

```bash
# .env for production
SECRET_KEY=your-strong-production-secret-key
FLASK_ENV=production
FLASK_DEBUG=False
DATABASE_URL=postgresql://nockpoint:secure_password@localhost:5432/nockpoint_db
WTF_CSRF_ENABLED=True
WTF_CSRF_TIME_LIMIT=3600
LOG_LEVEL=INFO
LOG_FILE=/var/log/nockpoint/nockpoint.log

# Email configuration
MAIL_SERVER=smtp.your-domain.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=noreply@your-domain.com
MAIL_PASSWORD=your-email-password
```

### Testing Environment

```bash
# .env.testing for automated tests
SECRET_KEY=test-secret-key
FLASK_ENV=testing
DATABASE_URL=sqlite:///:memory:
WTF_CSRF_ENABLED=False
MAIL_SUPPRESS_SEND=True
LOG_LEVEL=ERROR
```

## Competition-Specific Settings

### Default Competition Parameters

These can be set as environment variables or modified in the admin interface:

| Setting | Description | Default |
|---------|-------------|---------|
| `DEFAULT_ROUNDS` | Default number of rounds | `6` |
| `DEFAULT_ARROWS_PER_ROUND` | Default arrows per round | `6` |
| `DEFAULT_TARGET_SIZE` | Default target size (cm) | `122` |
| `DEFAULT_TEAM_SIZE` | Default maximum team size | `4` |

### Scoring Configuration

| Setting | Description | Default |
|---------|-------------|---------|
| `MAX_ARROW_SCORE` | Maximum points per arrow | `10` |
| `MIN_ARROW_SCORE` | Minimum points per arrow | `0` |
| `ENABLE_X_RING` | Enable X-ring scoring | `True` |

## Security Configuration

### CSRF Protection

```python
# CSRF settings
WTF_CSRF_ENABLED = True
WTF_CSRF_TIME_LIMIT = 3600  # 1 hour
WTF_CSRF_SSL_STRICT = True  # Require HTTPS in production

# Custom CSRF error handling
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400
```

### Session Security

```python
# Session configuration
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
```

### Password Security

```python
# Password hashing settings (using Werkzeug)
BCRYPT_LOG_ROUNDS = 12  # Adjust based on performance needs

# Password requirements (implement in forms)
PASSWORD_MIN_LENGTH = 8
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGITS = True
PASSWORD_REQUIRE_SYMBOLS = False
```

## Caching Configuration

### Simple Cache (Development)

```python
CACHE_TYPE = 'simple'
CACHE_DEFAULT_TIMEOUT = 300  # 5 minutes
```

### Redis Cache (Production)

```python
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = 'redis://localhost:6379/0'
CACHE_DEFAULT_TIMEOUT = 300
CACHE_KEY_PREFIX = 'nockpoint:'
```

### Cache Usage

```python
from flask_caching import Cache

cache = Cache()

@cache.cached(timeout=300, key_prefix='competitions')
def get_competitions():
    return Competition.query.all()

@cache.memoize(timeout=600)
def get_user_by_id(user_id):
    return User.query.get(user_id)
```

## Feature Flags

### Environment-Based Features

```bash
# Feature flags in .env
ENABLE_COMPETITIONS=True
ENABLE_INVENTORY=True
ENABLE_PAYMENTS=True
ENABLE_EMAIL_NOTIFICATIONS=False
ENABLE_API_ACCESS=True
ENABLE_BULK_IMPORTS=False
```

### Usage in Code

```python
import os

def is_feature_enabled(feature_name):
    return os.environ.get(f'ENABLE_{feature_name}', 'False').lower() == 'true'

# In views
if is_feature_enabled('COMPETITIONS'):
    # Competition-related code
    pass

# In templates
{% if config.get('ENABLE_COMPETITIONS') %}
    <li><a href="{{ url_for('competitions.index') }}">Competitions</a></li>
{% endif %}
```

## Configuration Validation

### Startup Validation

```python
def validate_config(app):
    """Validate critical configuration settings"""
    errors = []
    
    # Check required settings
    if not app.config.get('SECRET_KEY') or app.config['SECRET_KEY'] == 'dev-secret-key':
        errors.append('SECRET_KEY must be set to a secure value')
    
    if app.config.get('FLASK_ENV') == 'production':
        if not app.config.get('DATABASE_URL') or 'sqlite' in app.config['DATABASE_URL']:
            errors.append('Production environment requires PostgreSQL database')
        
        if app.config.get('DEBUG'):
            errors.append('DEBUG must be False in production')
    
    # Validate database connection
    try:
        with app.app_context():
            db.engine.connect()
    except Exception as e:
        errors.append(f'Database connection failed: {e}')
    
    if errors:
        raise RuntimeError(f'Configuration errors: {", ".join(errors)}')

# In app factory
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name or 'default'])
    
    validate_config(app)
    return app
```

## Configuration Loading Order

The application loads configuration in this order (later sources override earlier ones):

1. **Default values** in config classes
2. **Environment variables** from `.env` file
3. **System environment variables**
4. **Runtime configuration** (if applicable)

### Loading Process

```python
from dotenv import load_dotenv

# 1. Load .env file
load_dotenv()

# 2. Load configuration class
app.config.from_object(config[config_name])

# 3. Override with environment-specific file
if config_file := os.environ.get('CONFIG_FILE'):
    app.config.from_pyfile(config_file)

# 4. Override with instance configuration
app.config.from_pyfile('config.py', silent=True)
```

## Best Practices

### Security Best Practices

1. **Never commit secrets** to version control
2. **Use strong random SECRET_KEY** in production
3. **Enable CSRF protection** in production
4. **Use HTTPS** for production deployments
5. **Regularly rotate** database passwords and API keys

### Performance Best Practices

1. **Use connection pooling** for databases
2. **Configure caching** for frequently accessed data
3. **Set appropriate timeout values**
4. **Monitor and adjust** based on actual usage

### Maintenance Best Practices

1. **Document configuration changes**
2. **Use configuration management tools** for multiple environments
3. **Validate configuration** on application startup
4. **Monitor configuration drift** between environments
