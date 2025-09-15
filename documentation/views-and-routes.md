# Views and Routes Documentation

## Overview

The application uses Flask blueprints to organize routes into logical modules. Each blueprint handles specific functionality and includes proper authentication and authorization.

## Blueprint Architecture

### Main Blueprint (`app/main/__init__.py`)
**Prefix**: `/`

Handles core application routes and dashboard.

#### Routes

**`/` (GET)**
- **Function**: `index()`
- **Template**: `index.html`
- **Purpose**: Landing page for unauthenticated users
- **Access**: Public

**`/dashboard` (GET)**
- **Function**: `dashboard()`
- **Template**: `dashboard.html`
- **Purpose**: Main dashboard with statistics and quick actions
- **Access**: `@login_required`
- **Data Provided**:
  - Total inventory items and categories
  - Total members and active member count
  - Recent inventory items
  - Upcoming events count

```python
@main_bp.route('/dashboard')
@login_required
def dashboard():
    total_items = InventoryItem.query.count()
    total_categories = InventoryCategory.query.count()
    total_members = User.query.count()
    active_members = User.query.filter_by(is_active=True).count()
    recent_items = InventoryItem.query.order_by(InventoryItem.created_at.desc()).limit(5).all()
    upcoming_events_count = ShootingEvent.query.filter(
        ShootingEvent.date >= datetime.now().date(),
        ShootingEvent.date <= thirty_days_from_now
    ).count()
    
    return render_template('dashboard.html', ...)
```

### Authentication Blueprint (`app/auth/__init__.py`)
**Prefix**: `/auth`

Handles user authentication and registration.

#### Routes

**`/auth/login` (GET, POST)**
- **Function**: `login()`
- **Template**: `auth/login.html`
- **Purpose**: User login
- **Form**: `LoginForm`
- **Redirects**: Dashboard on success, back to login on failure

**`/auth/register` (GET, POST)**
- **Function**: `register()`
- **Template**: `auth/register.html`
- **Purpose**: New user registration
- **Form**: `RegistrationForm`
- **Features**: Duplicate username/email validation

**`/auth/logout` (GET)**
- **Function**: `logout()`
- **Purpose**: User logout and session cleanup
- **Redirects**: Homepage

### Inventory Blueprint (`app/inventory/__init__.py`)
**Prefix**: `/inventory`

Manages equipment inventory and categories.

#### Routes

**`/inventory/` (GET)**
- **Function**: `index()`
- **Template**: `inventory/index.html`
- **Purpose**: List all inventory items with search/filter
- **Access**: `@login_required`
- **Features**: Pagination, search, category filtering

**`/inventory/new` (GET, POST)**
- **Function**: `new_item()`
- **Template**: `inventory/item_form.html`
- **Purpose**: Create new inventory item
- **Access**: `@login_required`, `@admin_required`
- **Form**: `InventoryItemForm`

**`/inventory/<int:id>` (GET)**
- **Function**: `view_item(id)`
- **Template**: `inventory/view_item.html`
- **Purpose**: View detailed item information
- **Access**: `@login_required`

**`/inventory/<int:id>/edit` (GET, POST)**
- **Function**: `edit_item(id)`
- **Template**: `inventory/item_form.html`
- **Purpose**: Edit existing inventory item
- **Access**: `@login_required`, `@admin_required`

**`/inventory/<int:id>/delete` (POST)**
- **Function**: `delete_item(id)`
- **Purpose**: Delete inventory item
- **Access**: `@admin_required`
- **Response**: JSON success/error

**`/inventory/categories` (GET)**
- **Function**: `categories()`
- **Template**: `inventory/categories.html`
- **Purpose**: List all categories
- **Access**: `@admin_required`

**`/inventory/categories/new` (GET, POST)**
- **Function**: `new_category()`
- **Template**: `inventory/category_form.html`
- **Purpose**: Create new category
- **Access**: `@admin_required`

### Members Blueprint (`app/members/__init__.py`)
**Prefix**: `/members`

Handles member management and profiles.

#### Routes

**`/members/` (GET)**
- **Function**: `index()`
- **Template**: `members/index.html`
- **Purpose**: List all club members
- **Access**: `@login_required`
- **Features**: Admin/member filtering, search

**`/members/new` (GET, POST)**
- **Function**: `new_member()`
- **Template**: `members/member_form.html`
- **Purpose**: Add new member (admin only)
- **Access**: `@admin_required`
- **Form**: `MemberForm`

**`/members/<int:id>` (GET)**
- **Function**: `view_member(id)`
- **Template**: `members/view_member.html`
- **Purpose**: View member profile
- **Access**: `@login_required`

**`/members/<int:id>/edit` (GET, POST)**
- **Function**: `edit_member(id)`
- **Template**: `members/member_form.html`
- **Purpose**: Edit member information
- **Access**: `@admin_required`

**`/members/<int:id>/delete` (POST)**
- **Function**: `delete_member(id)`
- **Purpose**: Deactivate member
- **Access**: `@admin_required`

**`/members/profile` (GET, POST)**
- **Function**: `profile()`
- **Template**: `members/profile.html`
- **Purpose**: Edit own profile
- **Access**: `@login_required`
- **Form**: `ProfileForm`

### Events Blueprint (`app/events/__init__.py`)
**Prefix**: `/events`

Handles shooting events, attendance, and payments.

#### Event Management Routes

**`/events/` (GET)**
- **Function**: `calendar()`
- **Template**: `events/calendar.html`
- **Purpose**: Event calendar view
- **Access**: `@login_required`
- **Data**: Upcoming and past events

**`/events/create` (GET, POST)**
- **Function**: `create_event()`
- **Template**: `events/event_form.html`
- **Purpose**: Create new shooting event
- **Access**: `@admin_required`
- **Form**: `ShootingEventForm`

**`/events/<int:id>` (GET)**
- **Function**: `view_event(id)`
- **Template**: `events/view_event.html`
- **Purpose**: View event details and attendee list
- **Access**: `@login_required`

**`/events/<int:id>/edit` (GET, POST)**
- **Function**: `edit_event(id)`
- **Template**: `events/event_form.html`
- **Purpose**: Edit existing event
- **Access**: `@admin_required`

**`/events/<int:id>/delete` (POST)**
- **Function**: `delete_event(id)`
- **Purpose**: Delete event and related records
- **Access**: `@admin_required`

#### Attendance Management Routes

**`/events/<int:id>/attendance` (GET, POST)**
- **Function**: `manage_attendance(id)`
- **Template**: `events/manage_attendance.html`
- **Purpose**: Admin interface for attendance management
- **Access**: `@admin_required`
- **Features**: Real-time attendance tracking, add walk-ins

**`/events/<int:event_id>/add-attendee` (POST)**
- **Function**: `add_attendee(event_id)`
- **Purpose**: Add new attendee to event
- **Access**: `@admin_required`
- **Response**: Redirect with flash message

**`/events/<int:id>/update-attendance` (POST)**
- **Function**: `update_attendance(id)`
- **Purpose**: AJAX endpoint for attendance updates
- **Access**: `@admin_required`
- **Response**: JSON success/error

**`/events/<int:id>/remove-attendee` (POST)**
- **Function**: `remove_attendee(id)`
- **Purpose**: Remove attendee from event
- **Access**: `@admin_required`
- **Response**: JSON success/error

#### Payment Management Routes

**`/events/payments` (GET)**
- **Function**: `outstanding_payments()`
- **Template**: `events/outstanding_payments.html`
- **Purpose**: Admin dashboard for payment management
- **Access**: `@admin_required`
- **Features**: Search, filter, payment status updates

**`/events/my-charges` (GET)**
- **Function**: `my_charges()`
- **Template**: `events/my_charges.html`
- **Purpose**: Member view of their charges
- **Access**: `@login_required`

**`/events/mark-paid` (POST)**
- **Function**: `mark_paid()`
- **Purpose**: AJAX endpoint to mark charge as paid
- **Access**: `@admin_required`
- **Response**: JSON success/error

**`/events/update-payment-status` (POST)**
- **Function**: `update_payment_status()`
- **Purpose**: Update payment status (paid/unpaid)
- **Access**: `@admin_required`
- **Response**: JSON success/error

**`/events/update-charge-amount` (POST)**
- **Function**: `update_charge_amount()`
- **Purpose**: Modify charge amount with reason
- **Access**: `@admin_required`
- **Response**: JSON success/error

**`/events/delete-charge` (POST)**
- **Function**: `delete_charge()`
- **Purpose**: Delete a member charge
- **Access**: `@admin_required`
- **Response**: JSON success/error

## Route Security

### Authentication Decorators

**`@login_required`**
- Applied to all routes requiring authentication
- Redirects unauthenticated users to login page
- Provided by Flask-Login

**`@admin_required`**
- Custom decorator for admin-only routes
- Checks `current_user.is_admin()`
- Returns 403 Forbidden for non-admin users

```python
from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
```

### CSRF Protection
All POST routes are protected by Flask-WTF CSRF tokens:
- Forms include `{{ form.hidden_tag() }}`
- AJAX requests include CSRF token in headers
- Automatic validation on form submission

## Error Handling

### HTTP Error Pages
- **404**: Page not found
- **403**: Access forbidden (non-admin accessing admin routes)
- **500**: Internal server error

### Flash Messages
Routes use Flask's flash messaging for user feedback:

```python
flash('Success message', 'success')
flash('Error message', 'error')
flash('Warning message', 'warning')
flash('Info message', 'info')
```

### Form Validation Errors
- Field-level errors displayed inline
- Form-level errors shown as alerts
- Automatic re-population of valid fields

## AJAX Endpoints

Several routes handle AJAX requests for dynamic functionality:

### Attendance Updates
```javascript
fetch('/events/123/update-attendance', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    },
    body: JSON.stringify({
        attendee_id: 456,
        attended: true
    })
})
```

### Payment Management
```javascript
fetch('/events/mark-paid', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf_token
    },
    body: JSON.stringify({
        charge_id: 789
    })
})
```

## Request/Response Patterns

### Standard Form Routes
```python
@bp.route('/create', methods=['GET', 'POST'])
def create():
    form = MyForm()
    if form.validate_on_submit():
        # Process form data
        # Save to database
        flash('Success message', 'success')
        return redirect(url_for('.index'))
    return render_template('form.html', form=form)
```

### AJAX JSON Routes
```python
@bp.route('/api/update', methods=['POST'])
def api_update():
    data = request.get_json()
    try:
        # Process data
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```

### View Routes with Data
```python
@bp.route('/<int:id>')
def view(id):
    item = Model.query.get_or_404(id)
    related_data = get_related_data(item)
    return render_template('view.html', item=item, data=related_data)
```

## URL Generation

Routes use Flask's `url_for()` function for URL generation:

```python
# In Python
redirect(url_for('events.view_event', id=event.id))

# In templates
<a href="{{ url_for('inventory.edit_item', id=item.id) }}">Edit</a>
```

## Route Testing

### Unit Testing Routes
```python
def test_dashboard_authenticated(client, auth):
    auth.login()
    response = client.get('/dashboard')
    assert response.status_code == 200
    assert b'Dashboard' in response.data
```

### Authorization Testing
```python
def test_admin_required(client, auth):
    auth.login()  # Login as regular user
    response = client.get('/admin-route')
    assert response.status_code == 403
```

## Performance Considerations

### Database Queries
- Use eager loading with `joinedload()` for related data
- Implement pagination for large result sets
- Cache frequently accessed data

### Static Assets
- CSS/JS files served from CDN in production
- Static file caching headers
- Minification and compression

### Session Management
- Sessions stored server-side with Flask-Login
- Automatic session cleanup on logout
- Remember me functionality for convenience
