# Templates Documentation

## Overview

The application uses Jinja2 templating engine with Bootstrap 5 for responsive, modern UI. Templates are organized by functionality and follow a consistent structure with base template inheritance.

**Template Directory**: `app/templates/`

## Base Template Architecture

### Base Template (`base.html`)
The foundation template that all other templates extend.

**Key Components**:
- HTML5 document structure
- Bootstrap 5 CSS and JavaScript
- Navigation bar with authentication-aware menu
- Flash message display system
- Footer with copyright information

**Navigation Structure**:
```html
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="{{ url_for('main.index') }}">
            <i class="bi bi-bullseye"></i> Nockpoint
        </a>
        
        <!-- Authenticated user menu -->
        {% if current_user.is_authenticated %}
            <ul class="navbar-nav me-auto">
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('main.dashboard') }}">Dashboard</a>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('inventory.index') }}">Inventory</a>
                </li>
                <!-- Events dropdown menu -->
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="eventsDropdown" role="button" data-bs-toggle="dropdown">
                        <i class="bi bi-calendar3"></i> Events
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="{{ url_for('events.calendar') }}">Calendar</a></li>
                        <li><a class="dropdown-item" href="{{ url_for('events.my_charges') }}">My Charges</a></li>
                        {% if current_user.is_admin() %}
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('events.create_event') }}">Create Event</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('events.outstanding_payments') }}">Manage Payments</a></li>
                        {% endif %}
                    </ul>
                </li>
            </ul>
        {% endif %}
    </div>
</nav>
```

**Flash Message System**:
```html
{% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
        {% for category, message in messages %}
            <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}
{% endwith %}
```

## Core Templates

### Landing Page (`index.html`)
Homepage for unauthenticated users.

**Features**:
- Hero section with club branding
- Feature highlights
- Call-to-action buttons for login/register
- Responsive design with Bootstrap grid

### Dashboard (`dashboard.html`)
Main dashboard for authenticated users.

**Sections**:
- **Statistics Cards**: Total items, categories, members, upcoming events
- **Recent Activity**: Latest inventory items
- **Quick Actions**: Context-sensitive action buttons
- **System Status**: User role, member since date, version info

**Statistics Display**:
```html
<div class="row mb-4">
    <div class="col-md-3 mb-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <div class="d-flex justify-content-between">
                    <div>
                        <h4>{{ total_items }}</h4>
                        <p class="mb-0">Total Items</p>
                    </div>
                    <div class="align-self-center">
                        <i class="bi bi-box-seam display-6"></i>
                    </div>
                </div>
            </div>
        </div>
    </div>
    <!-- More cards... -->
</div>
```

## Authentication Templates

### Login Page (`auth/login.html`)
User authentication interface.

**Features**:
- Centered login form with validation
- Remember me checkbox
- Links to registration page
- Error message display
- CSRF protection

**Form Structure**:
```html
<form method="POST">
    {{ form.hidden_tag() }}
    
    <div class="mb-3">
        {{ form.username.label(class="form-label") }}
        {{ form.username(class="form-control") }}
        {% if form.username.errors %}
            <div class="text-danger small">
                {% for error in form.username.errors %}
                    <div>{{ error }}</div>
                {% endfor %}
            </div>
        {% endif %}
    </div>
    
    <!-- More fields... -->
    
    {{ form.submit(class="btn btn-primary") }}
</form>
```

### Registration Page (`auth/register.html`)
New user registration interface.

**Features**:
- Multi-field registration form
- Password confirmation validation
- Real-time client-side validation
- Server-side error display

## Inventory Templates

### Inventory Index (`inventory/index.html`)
List view of all inventory items.

**Features**:
- Searchable and filterable item table
- Category-based filtering
- Pagination for large datasets
- Admin action buttons (Edit, Delete)
- Responsive table design

**Table Structure**:
```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Quantity</th>
                <th>Created</th>
                {% if current_user.is_admin() %}
                    <th>Actions</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for item in items %}
                <tr>
                    <td>
                        <a href="{{ url_for('inventory.view_item', id=item.id) }}">
                            {{ item.name }}
                        </a>
                    </td>
                    <td>{{ item.category.name }}</td>
                    <td>
                        <span class="badge bg-{% if item.quantity > 0 %}success{% else %}danger{% endif %}">
                            {{ item.quantity }}
                        </span>
                    </td>
                    <td>{{ item.created_at.strftime('%Y-%m-%d') }}</td>
                    {% if current_user.is_admin() %}
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="{{ url_for('inventory.edit_item', id=item.id) }}" class="btn btn-outline-primary">Edit</a>
                                <button class="btn btn-outline-danger" onclick="deleteItem({{ item.id }})">Delete</button>
                            </div>
                        </td>
                    {% endif %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### Item Form (`inventory/item_form.html`)
Create and edit inventory items.

**Features**:
- Dynamic category selection
- Quantity validation
- Rich text description
- Form validation display

### Item Detail (`inventory/view_item.html`)
Detailed view of individual inventory item.

**Features**:
- Complete item information display
- Edit/delete actions for admins
- Creation history and metadata
- Related category information

## Member Management Templates

### Members Index (`members/index.html`)
List of all club members.

**Features**:
- Member search and filtering
- Role-based display (Admin badges)
- Member status indicators
- Admin management actions

### Member Profile (`members/view_member.html`)
Individual member profile view.

**Features**:
- Complete member information
- Role and status display
- Activity history
- Admin edit controls

### Profile Edit (`members/profile.html`)
Self-service profile editing.

**Features**:
- Personal information update
- Email change validation
- Security restrictions (can't change role)
- Success/error feedback

## Events System Templates

### Event Calendar (`events/calendar.html`)
Main events calendar interface.

**Sections**:
- **Upcoming Events**: Next 30 days with registration info
- **Past Events**: Historical events with attendance data
- **Quick Stats**: Event counts and summaries
- **Admin Actions**: Create event, manage payments

**Event Display**:
```html
<div class="card">
    <div class="card-body">
        <div class="d-flex justify-content-between">
            <div>
                <h5 class="card-title">{{ event.name }}</h5>
                <p class="card-text">
                    <i class="bi bi-geo-alt text-primary"></i> {{ event.location }}<br>
                    <i class="bi bi-calendar text-primary"></i> {{ event.date.strftime('%B %d, %Y') }}<br>
                    <i class="bi bi-clock text-primary"></i> {{ event.start_time.strftime('%I:%M %p') }}
                </p>
            </div>
            <div class="text-end">
                {% if event.price > 0 %}
                    <div class="h5 text-success">${{ "%.2f"|format(event.price) }}</div>
                {% else %}
                    <div class="h5 text-success">FREE</div>
                {% endif %}
                <small class="text-muted">{{ event.attendance_count }} registered</small>
            </div>
        </div>
    </div>
</div>
```

### Event Form (`events/event_form.html`)
Create and edit shooting events.

**Features**:
- Comprehensive event details form
- Date and time pickers
- Price and participant limit fields
- Location and description inputs
- Validation error display

### Event Detail (`events/view_event.html`)
Detailed event information and management.

**Sections**:
- **Event Information**: Date, time, location, pricing
- **Participant List**: Registered attendees with status
- **Admin Controls**: Edit, attendance management, delete
- **Statistics Sidebar**: Registration counts, revenue

### Attendance Management (`events/manage_attendance.html`)
Admin interface for attendance tracking.

**Features**:
- **Real-time Attendance Tracking**: AJAX-powered checkboxes
- **Bulk Actions**: Mark all attended, clear all
- **Walk-in Registration**: Add new attendees on-the-fly
- **Payment Integration**: Payment status display
- **Statistics Dashboard**: Attendance counts, revenue

**Attendance Controls**:
```html
<div class="form-check form-switch">
    <input class="form-check-input attendance-checkbox" 
           type="checkbox" 
           name="attendee_{{ attendee.id }}"
           {% if attendee.attended %}checked{% endif %}
           onchange="updateAttendanceStatus({{ attendee.id }}, this.checked)">
    <label class="form-check-label">
        <span class="attended-label {% if not attendee.attended %}d-none{% endif %}">Attended</span>
        <span class="not-attended-label {% if attendee.attended %}d-none{% endif %}">Not Attended</span>
    </label>
</div>
```

### Payment Management (`events/outstanding_payments.html`)
Admin dashboard for payment tracking.

**Features**:
- **Payment Overview**: Outstanding vs. paid charges
- **Search and Filter**: Find specific charges
- **Bulk Operations**: Mark multiple payments
- **Charge Editing**: Modify amounts and notes
- **Member Communication**: Payment contact information

### Member Charges (`events/my_charges.html`)
Member view of personal charges.

**Features**:
- **Charge History**: All event charges and payments
- **Payment Status**: Clear outstanding balance display
- **Event Links**: Navigate to related events
- **Payment Instructions**: Contact information for payment

## Template Features

### Responsive Design
All templates use Bootstrap 5 responsive grid system:
- Mobile-first approach
- Collapsible navigation
- Responsive tables
- Flexible card layouts

### Accessibility
Templates include accessibility features:
- Proper semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility

### Icon Integration
Bootstrap Icons used throughout:
```html
<i class="bi bi-calendar3"></i> <!-- Calendar icon -->
<i class="bi bi-person-circle"></i> <!-- User icon -->
<i class="bi bi-box-seam"></i> <!-- Inventory icon -->
<i class="bi bi-currency-dollar"></i> <!-- Payment icon -->
```

### Form Validation Display
Consistent validation error display:
```html
{% if form.field.errors %}
    <div class="text-danger small">
        {% for error in form.field.errors %}
            <div>{{ error }}</div>
        {% endfor %}
    </div>
{% endif %}
```

### JavaScript Integration
Templates include JavaScript for dynamic functionality:
- AJAX form submissions
- Real-time updates
- Interactive confirmations
- Dynamic content loading

**Example AJAX Integration**:
```html
<script>
function updateAttendanceStatus(attendeeId, attended) {
    fetch('{{ url_for("events.update_attendance", id=event.id) }}', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
        },
        body: JSON.stringify({
            attendee_id: attendeeId,
            attended: attended
        })
    }).then(response => {
        if (!response.ok) {
            // Handle error
        }
    });
}
</script>
```

## Template Inheritance

### Block Structure
Templates use consistent block inheritance:
```html
{% extends "base.html" %}

{% block title %}Page Title - {{ super() }}{% endblock %}

{% block content %}
    <!-- Page content -->
{% endblock %}

{% block scripts %}
    <!-- Page-specific JavaScript -->
{% endblock %}
```

### Reusable Components
Common components extracted to macros and includes:
- Form field rendering
- Table pagination
- Button groups
- Modal dialogs

## Performance Optimization

### Template Caching
- Jinja2 template compilation caching
- Static asset versioning
- CDN integration for external resources

### Minimization
- CSS and JavaScript minification in production
- Image optimization
- Gzip compression

### SEO Optimization
- Proper meta tags
- Structured data markup
- Semantic HTML structure
- Fast loading times
