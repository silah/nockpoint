# Member Management Documentation

## Overview

The member management system handles club member administration, profiles, and role management. It provides both self-service capabilities for members and comprehensive administrative tools.

**Blueprint**: `app/members/`  
**Models**: `User` in `app/models.py`  
**Forms**: `MemberForm`, `ProfileForm` in `app/forms.py`

## Member Model

The member system uses the `User` model with role-based functionality:

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

**Key Features**:
- Unique username and email constraints
- Role-based access control
- Soft delete with `is_active` flag
- Automatic timestamping
- Secure password hashing

## Forms

### MemberForm

**Purpose**: Admin form for creating and editing members

```python
class MemberForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    is_admin = BooleanField('Administrator')
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Save Member')
```

**Features**:
- Admin role assignment via checkbox
- Optional password (for editing existing members)
- Conditional validation based on create vs. edit mode
- Duplicate checking for username and email

**Custom Validation**:
```python
def __init__(self, original_username=None, original_email=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.original_username = original_username
    self.original_email = original_email

def validate_username(self, username):
    if self.original_username != username.data:
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

def validate_email(self, email):
    if self.original_email != email.data:
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
```

### ProfileForm

**Purpose**: Self-service profile editing for all users

```python
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
```

**Security Restrictions**:
- Users cannot change their username
- Users cannot change their role
- Users cannot change their active status
- Email changes require validation

## Routes and Views

### Member Directory

#### View All Members (`/members/`)

**Template**: `members/index.html`  
**Access**: All authenticated users

**Features**:
- Paginated member listing
- Search by name or username
- Filter by role (All/Members/Admins)
- Member status indicators
- Admin management controls

**Implementation**:
```python
@members_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    role_filter = request.args.get('role', 'all', type=str)
    
    query = User.query.filter_by(is_active=True)
    
    # Apply search filter
    if search:
        query = query.filter(
            db.or_(
                User.first_name.contains(search),
                User.last_name.contains(search),
                User.username.contains(search)
            )
        )
    
    # Apply role filter
    if role_filter == 'admin':
        query = query.filter(User.role == 'admin')
    elif role_filter == 'member':
        query = query.filter(User.role == 'member')
    
    members = query.order_by(User.last_name, User.first_name).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('members/index.html',
                         members=members,
                         current_search=search,
                         current_role=role_filter)
```

### Member Profiles

#### View Member Profile (`/members/<int:id>`)

**Template**: `members/view_member.html`  
**Access**: All authenticated users

**Information Displayed**:
- Complete member information
- Role and status badges
- Member since date
- Activity statistics (future enhancement)
- Contact information

**Admin Features**:
- Edit member button
- Role change options
- Account status management

#### Create Member (`/members/new`)

**Template**: `members/member_form.html`  
**Access**: Admin only  
**Form**: `MemberForm`

**Process**:
1. Display empty member form
2. Validate all required fields
3. Check for duplicate username/email
4. Hash password if provided
5. Set role based on admin checkbox
6. Create new user record
7. Send welcome notification (future enhancement)

**Implementation**:
```python
@members_bp.route('/new', methods=['GET', 'POST'])
@admin_required
def new_member():
    form = MemberForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role='admin' if form.is_admin.data else 'member'
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        flash(f'Member {user.username} has been created.', 'success')
        return redirect(url_for('members.index'))
    
    return render_template('members/member_form.html', form=form, title='Add New Member')
```

#### Edit Member (`/members/<int:id>/edit`)

**Template**: `members/member_form.html`  
**Access**: Admin only  
**Form**: `MemberForm` (pre-populated)

**Features**:
- Form pre-filled with existing member data
- Optional password update
- Role changes with confirmation
- Username/email change validation

**Special Considerations**:
- Password field optional for edits
- Admin cannot demote themselves
- Username changes affect login
- Email changes may require verification

#### Self-Service Profile (`/members/profile`)

**Template**: `members/profile.html`  
**Access**: All authenticated users  
**Form**: `ProfileForm`

**Restrictions**:
- Cannot change username
- Cannot change role
- Cannot change account status
- Email changes validated for uniqueness

### Member Management

#### Deactivate Member (`/members/<int:id>/delete`)

**Method**: POST only  
**Access**: Admin only  
**Action**: Soft delete (sets `is_active = False`)

**Implementation**:
```python
@members_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_member(id):
    user = User.query.get_or_404(id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot delete your own account'})
    
    try:
        user.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

**Safety Features**:
- Admins cannot delete themselves
- Soft delete preserves data
- Confirmation required
- Activity logs (future enhancement)

## User Interface

### Member Directory Template

**Features**:
- Responsive card layout for mobile
- Table layout for desktop
- Search and filter controls
- Role badges and status indicators
- Admin action buttons

**Search and Filter Interface**:
```html
<div class="row mb-4">
    <div class="col-md-8">
        <form method="GET" class="d-flex">
            <input type="text" class="form-control me-2" 
                   name="search" value="{{ current_search }}" 
                   placeholder="Search members...">
            <button type="submit" class="btn btn-outline-secondary">Search</button>
        </form>
    </div>
    <div class="col-md-4">
        <select class="form-select" onchange="filterByRole(this.value)">
            <option value="all" {% if current_role == 'all' %}selected{% endif %}>All Members</option>
            <option value="admin" {% if current_role == 'admin' %}selected{% endif %}>Administrators</option>
            <option value="member" {% if current_role == 'member' %}selected{% endif %}>Members</option>
        </select>
    </div>
</div>
```

**Member Display Cards**:
```html
{% for member in members.items %}
    <div class="col-lg-4 col-md-6 mb-4">
        <div class="card h-100">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title mb-0">{{ member.first_name }} {{ member.last_name }}</h5>
                    {% if member.role == 'admin' %}
                        <span class="badge bg-warning text-dark">Admin</span>
                    {% endif %}
                </div>
                <p class="card-text">
                    <i class="bi bi-person-circle text-muted"></i> {{ member.username }}<br>
                    <i class="bi bi-envelope text-muted"></i> {{ member.email }}<br>
                    <i class="bi bi-calendar text-muted"></i> Member since {{ member.created_at.strftime('%B %Y') }}
                </p>
            </div>
            <div class="card-footer bg-transparent">
                <div class="btn-group w-100">
                    <a href="{{ url_for('members.view_member', id=member.id) }}" 
                       class="btn btn-outline-primary btn-sm">View</a>
                    {% if current_user.is_admin() %}
                        <a href="{{ url_for('members.edit_member', id=member.id) }}" 
                           class="btn btn-outline-secondary btn-sm">Edit</a>
                        {% if member.id != current_user.id %}
                            <button class="btn btn-outline-danger btn-sm" 
                                    onclick="deactivateMember({{ member.id }})">Deactivate</button>
                        {% endif %}
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
{% endfor %}
```

### Member Profile Template

**Sections**:
- **Personal Information**: Name, username, email
- **Account Details**: Role, status, member since
- **Activity Summary**: Recent actions, statistics
- **Admin Controls**: Edit, role change, status management

**Profile Display**:
```html
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center mb-4">
                    <div>
                        <h2>{{ member.first_name }} {{ member.last_name }}</h2>
                        <p class="text-muted mb-0">@{{ member.username }}</p>
                    </div>
                    <div>
                        {% if member.role == 'admin' %}
                            <span class="badge bg-warning text-dark fs-6">Administrator</span>
                        {% else %}
                            <span class="badge bg-primary fs-6">Member</span>
                        {% endif %}
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-sm-6">
                        <p><strong>Email:</strong> {{ member.email }}</p>
                        <p><strong>Username:</strong> {{ member.username }}</p>
                    </div>
                    <div class="col-sm-6">
                        <p><strong>Member Since:</strong> {{ member.created_at.strftime('%B %d, %Y') }}</p>
                        <p><strong>Status:</strong> 
                            {% if member.is_active %}
                                <span class="badge bg-success">Active</span>
                            {% else %}
                                <span class="badge bg-secondary">Inactive</span>
                            {% endif %}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Admin sidebar controls -->
    {% if current_user.is_admin() %}
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h6>Admin Actions</h6>
                </div>
                <div class="card-body d-grid gap-2">
                    <a href="{{ url_for('members.edit_member', id=member.id) }}" 
                       class="btn btn-primary">Edit Profile</a>
                    {% if member.role == 'admin' %}
                        <button class="btn btn-outline-warning" 
                                onclick="changeRole({{ member.id }}, 'member')">Remove Admin</button>
                    {% else %}
                        <button class="btn btn-outline-success" 
                                onclick="changeRole({{ member.id }}, 'admin')">Make Admin</button>
                    {% endif %}
                    {% if member.id != current_user.id %}
                        <button class="btn btn-outline-danger" 
                                onclick="deactivateMember({{ member.id }})">Deactivate Account</button>
                    {% endif %}
                </div>
            </div>
        </div>
    {% endif %}
</div>
```

### Form Templates

**Member Form Features**:
- Conditional password fields (required for new, optional for edit)
- Admin role checkbox with confirmation
- Form validation display
- Success/error messaging

**Profile Form Features**:
- Read-only username display
- Editable personal information
- Email change validation
- Simple, focused interface

## JavaScript Functionality

### Member Deactivation

**AJAX Implementation**:
```javascript
function deactivateMember(memberId) {
    if (confirm('Are you sure you want to deactivate this member? They will no longer be able to log in.')) {
        fetch(`/members/${memberId}/delete`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to deactivate member'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deactivating the member.');
        });
    }
}
```

### Role Management

**Role Change Function**:
```javascript
function changeRole(memberId, newRole) {
    const action = newRole === 'admin' ? 'promote to administrator' : 'remove administrator privileges from';
    const message = `Are you sure you want to ${action} this member?`;
    
    if (confirm(message)) {
        fetch(`/members/${memberId}/change-role`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ role: newRole })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to update member role'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while updating the member role.');
        });
    }
}
```

### Search and Filter

**Client-side Filter Updates**:
```javascript
function filterByRole(role) {
    const currentUrl = new URL(window.location);
    if (role === 'all') {
        currentUrl.searchParams.delete('role');
    } else {
        currentUrl.searchParams.set('role', role);
    }
    currentUrl.searchParams.delete('page'); // Reset pagination
    window.location.href = currentUrl.toString();
}

// Auto-submit search form on Enter
document.querySelector('input[name="search"]').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        this.closest('form').submit();
    }
});
```

## Access Control

### Permission Matrix

| Action | Member | Admin |
|--------|--------|-------|
| View member directory | ✓ | ✓ |
| View member profiles | ✓ | ✓ |
| Edit own profile | ✓ | ✓ |
| Create new members | ✗ | ✓ |
| Edit other members | ✗ | ✓ |
| Change member roles | ✗ | ✓ |
| Deactivate members | ✗ | ✓ |
| View admin controls | ✗ | ✓ |

### Template Access Control

**Admin-Only Content**:
```html
{% if current_user.is_admin() %}
    <div class="mb-3">
        <a href="{{ url_for('members.new_member') }}" class="btn btn-primary">
            <i class="bi bi-person-plus"></i> Add New Member
        </a>
    </div>
{% endif %}
```

**Self-Service Restrictions**:
```html
{% if current_user.id == member.id or current_user.is_admin() %}
    <a href="{{ url_for('members.edit_member', id=member.id) }}" class="btn btn-outline-primary">
        Edit Profile
    </a>
{% endif %}
```

## Dashboard Integration

### Member Statistics

**Dashboard Metrics**:
```python
def get_member_stats():
    total_members = User.query.filter_by(is_active=True).count()
    active_members = User.query.filter_by(is_active=True, role='member').count()
    admin_count = User.query.filter_by(is_active=True, role='admin').count()
    new_members_this_month = User.query.filter(
        User.created_at >= datetime.now().replace(day=1)
    ).count()
    
    return {
        'total_members': total_members,
        'active_members': active_members, 
        'admin_count': admin_count,
        'new_members_this_month': new_members_this_month
    }
```

**Dashboard Display**:
- Total member count with growth indicators
- Active vs. inactive member ratios
- Admin count and recent promotions
- New member registration trends
- Quick access to member management

## Security Features

### Data Protection

**Sensitive Information Handling**:
- Passwords never displayed in forms or logs
- Email changes require confirmation
- Personal information protected by login requirement
- Admin actions logged (future enhancement)

**Access Validation**:
- Route-level permission checking
- Template-level content filtering
- CSRF protection on all forms
- Session-based authentication

### Audit Trail

**Future Enhancement - Activity Logging**:
```python
class MemberActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(100))  # 'created', 'edited', 'role_changed', etc.
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
```

## Reporting

### Member Reports

**Basic Reports Available**:
- Member directory export
- Role distribution
- Registration trends
- Activity summaries

**Future Reporting Features**:
- Attendance tracking
- Payment history
- Engagement metrics
- Custom report builder

## Integration Points

### Events System Integration

**Member-Event Relationships**:
- Event attendance tracking
- Member charge management
- Registration history
- Payment status

### Authentication Integration

**Seamless Auth Flow**:
- Login redirects to member profile
- Registration creates member records
- Role changes affect permissions immediately
- Profile updates sync with authentication

## Future Enhancements

### Planned Features

**Enhanced Profiles**:
- Profile photos
- Contact preferences
- Emergency contacts
- Skills and certifications

**Communication Tools**:
- Member messaging system
- Group notifications
- Email integration
- SMS alerts

**Advanced Administration**:
- Bulk operations
- Import/export capabilities
- Advanced search filters
- Custom fields

**Member Portal**:
- Personal dashboard
- Activity history
- Document library
- Online forms

### Technical Improvements

**Performance Optimization**:
- Database indexing
- Search optimization
- Caching strategies
- Mobile performance

**User Experience**:
- Progressive web app features
- Offline capability
- Push notifications
- Advanced UI components
