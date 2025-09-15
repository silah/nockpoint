# Authentication System Documentation

## Overview

The authentication system provides secure user login, registration, and role-based access control using Flask-Login. It supports both member and administrator roles with appropriate permissions.

**Blueprint**: `app/auth/`  
**Models**: `User` in `app/models.py`  
**Forms**: `LoginForm`, `RegistrationForm` in `app/forms.py`

## User Model

### Database Schema
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')  # 'member' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Key Features

**Flask-Login Integration**:
- Inherits from `UserMixin` for Flask-Login compatibility
- Automatic user session management
- Built-in authentication state tracking

**Password Security**:
- Passwords hashed using Werkzeug's `generate_password_hash()`
- Salted hashing prevents rainbow table attacks
- Never stores plain text passwords

**Role-Based Access**:
- Two roles: `member` (default) and `admin`
- Role-based permission checking
- Hierarchical access control

### User Methods

**Password Management**:
```python
def set_password(self, password):
    """Hash and store password"""
    self.password_hash = generate_password_hash(password)

def check_password(self, password):
    """Verify password against hash"""
    return check_password_hash(self.password_hash, password)
```

**Role Checking**:
```python
def is_admin(self):
    """Check if user has admin role"""
    return self.role == 'admin'
```

**User Representation**:
```python
def __repr__(self):
    return f'<User {self.username}>'
```

## Authentication Routes

### Login (`/auth/login`)

**Template**: `auth/login.html`  
**Form**: `LoginForm`  
**Methods**: GET, POST

**Functionality**:
- Displays login form on GET request
- Processes authentication on POST
- Validates credentials against database
- Creates user session on success
- Supports "Remember Me" functionality
- Redirects to intended page or dashboard

**Implementation**:
```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'error')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)
```

**Security Features**:
- CSRF protection via Flask-WTF
- Password verification without timing attacks
- Safe redirect handling (prevents open redirects)
- Session fixation protection

### Registration (`/auth/register`)

**Template**: `auth/register.html`  
**Form**: `RegistrationForm`  
**Methods**: GET, POST

**Functionality**:
- User self-registration
- Form validation and error handling
- Duplicate username/email prevention
- Password confirmation validation
- Automatic user activation

**Form Validation**:
```python
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
```

### Logout (`/auth/logout`)

**Methods**: GET  
**Functionality**:
- Terminates user session
- Clears authentication state
- Redirects to homepage
- Secure session cleanup

```python
@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
```

## Authorization System

### Access Control Decorators

**Login Required**:
```python
from flask_login import login_required

@bp.route('/protected')
@login_required
def protected_route():
    return "This requires authentication"
```

**Admin Required** (Custom Decorator):
```python
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/admin-only')
@login_required
@admin_required
def admin_route():
    return "This requires admin privileges"
```

### Template-Based Access Control

**Navigation Menu**:
```html
{% if current_user.is_authenticated %}
    <li class="nav-item">
        <a class="nav-link" href="{{ url_for('main.dashboard') }}">Dashboard</a>
    </li>
    {% if current_user.is_admin() %}
        <li class="nav-item">
            <a class="nav-link" href="{{ url_for('inventory.new_item') }}">Add Item</a>
        </li>
    {% endif %}
{% endif %}
```

**Conditional Content**:
```html
{% if current_user.is_admin() %}
    <div class="admin-controls">
        <button class="btn btn-danger">Delete</button>
    </div>
{% endif %}
```

## Session Management

### Flask-Login Configuration

**Application Setup**:
```python
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Session Features**:
- Automatic user loading from session
- Session timeout and renewal
- Remember me cookie support
- Secure session storage

### Remember Me Functionality

**Implementation**:
- Optional checkbox on login form
- Extended session duration
- Secure cookie storage
- Automatic session renewal

**Security Considerations**:
- Secure cookie flags (HttpOnly, Secure)
- Session token rotation
- Logout clears remember me tokens

## User Role Management

### Role Assignment

**During Registration**:
- All new users default to 'member' role
- Admin privileges must be granted by existing admin
- No self-promotion to admin status

**Admin Management**:
```python
# In member management form
class MemberForm(FlaskForm):
    is_admin = BooleanField('Administrator')
    
    def save_member(self, user):
        user.role = 'admin' if self.is_admin.data else 'member'
```

### Permission Levels

**Member Permissions**:
- View inventory and categories
- View other members
- View events calendar
- View own charges
- Edit own profile

**Admin Permissions**:
- All member permissions PLUS:
- Create/edit/delete inventory items
- Create/edit/delete categories
- Create/edit/delete members
- Create/edit/delete events
- Manage event attendance
- Manage member payments
- Access admin dashboards

## Security Features

### Password Security

**Hashing Algorithm**:
- Uses Werkzeug's `generate_password_hash()`
- PBKDF2 with SHA-256
- Automatic salt generation
- Configurable iteration count

**Password Requirements**:
- Minimum length enforced by form validation
- No maximum length (hash handles any size)
- Special characters allowed
- No complexity requirements (user choice)

### Session Security

**CSRF Protection**:
- All forms include CSRF tokens
- Automatic validation on submission
- Invalid tokens reject requests
- Session-specific token generation

**Session Fixation Prevention**:
- New session ID on login
- Session regeneration
- Old session invalidation

**Secure Cookies**:
```python
app.config['SESSION_COOKIE_SECURE'] = True      # HTTPS only
app.config['SESSION_COOKIE_HTTPONLY'] = True    # No JavaScript access
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'   # CSRF protection
```

### Brute Force Protection

**Rate Limiting** (recommended addition):
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    # Login logic
```

**Account Lockout** (future enhancement):
- Track failed login attempts
- Temporary account lockout
- Admin unlock capability

## Error Handling

### Authentication Errors

**Invalid Credentials**:
- Generic error message (no user enumeration)
- Flash message display
- Form field clearing
- Redirect to login page

**Access Denied**:
- 403 Forbidden response
- Custom error page
- Login prompt for unauthenticated users
- Role requirement explanation

### Form Validation Errors

**Client-Side Validation**:
- HTML5 form validation
- JavaScript enhancement
- Real-time feedback
- User-friendly messages

**Server-Side Validation**:
- WTForms validation rules
- Custom validation methods
- Database constraint checking
- Error message display

## User Management

### Profile Management

**Self-Service Profile Edit**:
- Users can update personal information
- Email change with validation
- No role or username changes
- Success/error feedback

**Admin User Management**:
- View all users
- Edit any user profile
- Change user roles
- Activate/deactivate accounts
- Cannot delete users (soft delete)

### Account States

**Active Users**:
- `is_active = True`
- Can log in and use system
- Default state for new users

**Inactive Users**:
- `is_active = False`
- Cannot log in
- Preserves user data
- Can be reactivated by admin

## Testing Authentication

### Unit Tests

**User Model Tests**:
```python
def test_password_hashing():
    user = User(username='test')
    user.set_password('secret')
    assert user.password_hash != 'secret'
    assert user.check_password('secret') == True
    assert user.check_password('wrong') == False

def test_admin_check():
    user = User(username='test', role='admin')
    assert user.is_admin() == True
    
    user.role = 'member'
    assert user.is_admin() == False
```

**Route Tests**:
```python
def test_login_required(client):
    response = client.get('/dashboard')
    assert response.status_code == 302  # Redirect to login

def test_admin_required(client, auth):
    auth.login()  # Login as regular user
    response = client.get('/admin-route')
    assert response.status_code == 403  # Forbidden
```

### Integration Tests

**Authentication Flow**:
```python
def test_login_logout_flow(client, auth):
    # Test login
    response = auth.login()
    assert 'Dashboard' in response.data
    
    # Test logout
    response = auth.logout()
    assert 'Login' in response.data
```

**Registration Flow**:
```python
def test_register_flow(client):
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'new@example.com',
        'first_name': 'New',
        'last_name': 'User',
        'password': 'password123',
        'password2': 'password123'
    })
    assert response.status_code == 302  # Redirect after registration
```

## Future Enhancements

### Planned Features

**Two-Factor Authentication**:
- TOTP support with apps like Google Authenticator
- SMS backup codes
- Recovery codes for account access

**OAuth Integration**:
- Google OAuth for simplified login
- Facebook/Microsoft integration
- Social login options

**Advanced Password Policy**:
- Configurable password requirements
- Password history tracking
- Password expiration policies

**Audit Logging**:
- Login/logout tracking
- Failed login attempts
- Permission changes
- Administrative actions

### Security Improvements

**Enhanced Session Security**:
- Session timeout configuration
- Concurrent session limits
- Device tracking and management

**Account Security**:
- Email verification for new accounts
- Password reset via email
- Account lockout policies
- Security question recovery
