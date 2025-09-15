# Events System Documentation

## Overview

The events system manages shooting events, attendance tracking, and payment processing. It provides comprehensive event management capabilities including calendar views, attendance recording, and financial tracking.

**Blueprint**: `app/events/`  
**Models**: `ShootingEvent`, `EventAttendance`, `MemberCharge` in `app/models.py`  
**Forms**: `ShootingEventForm`, `AttendanceForm`, `PaymentUpdateForm` in `app/forms.py`

## Database Models

### ShootingEvent Model

**Purpose**: Represents shooting events organized by the club  
**Table**: `shooting_event`

```python
class ShootingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration_hours = db.Column(db.Integer, default=2)
    price = db.Column(db.Numeric(10, 2), default=0.00)
    max_participants = db.Column(db.Integer)  # NULL = unlimited
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_events')
    attendances = db.relationship('EventAttendance', backref='event', lazy=True, cascade='all, delete-orphan')
    charges = db.relationship('MemberCharge', backref='event', lazy=True)
```

**Computed Properties**:
```python
@property
def end_time(self):
    """Calculate end time based on start time and duration"""
    return (datetime.combine(date.today(), self.start_time) + 
            timedelta(hours=self.duration_hours)).time()

@property
def is_past(self):
    """Check if event date has passed"""
    return self.date < date.today()

def attendance_count(self):
    """Get number of attendees"""
    return len(self.attendances)
```

### EventAttendance Model

**Purpose**: Tracks member attendance at events  
**Table**: `event_attendance`

```python
class EventAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attended_at = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text)  # Optional notes about attendance
    
    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], backref='event_attendances')
    recorder = db.relationship('User', foreign_keys=[recorded_by])
    
    # Unique constraint to prevent duplicate attendance
    __table_args__ = (db.UniqueConstraint('event_id', 'member_id', name='unique_event_attendance'),)
```

**Key Features**:
- Unique constraint prevents duplicate registrations
- Records who marked attendance
- Automatic registration timestamp
- Optional notes for special circumstances

### MemberCharge Model

**Purpose**: Financial charges for members (events, fees, etc.)  
**Table**: `member_charge`

```python
class MemberCharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=True)  # Null for non-event charges
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    charge_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    paid_by_admin = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who marked as paid
    payment_notes = db.Column(db.Text)
    
    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], backref='charges')
    admin = db.relationship('User', foreign_keys=[paid_by_admin])
```

**Key Features**:
- Supports both event and non-event charges
- Payment tracking with admin attribution
- Payment notes for record keeping
- Automatic charge creation for paid events

## Forms

### ShootingEventForm

**Purpose**: Create and edit shooting events

```python
class ShootingEventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=200)])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    duration_hours = IntegerField('Duration (hours)', validators=[DataRequired(), NumberRange(min=1, max=24)])
    price = DecimalField('Price ($)', validators=[DataRequired(), NumberRange(min=0, max=999.99)], places=2)
    max_participants = IntegerField('Max Participants', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Event')
```

**Features**:
- HTML5 date and time pickers
- Decimal pricing with precision
- Optional participant limits
- Comprehensive validation

### AttendanceForm

**Purpose**: Add attendees to events

```python
class AttendanceForm(FlaskForm):
    member_id = SelectField('Member', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Attendee')
    
    def __init__(self, event_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if event_id:
            # Show only members not already registered
            already_registered = [a.member_id for a in EventAttendance.query.filter_by(event_id=event_id).all()]
            available_users = User.query.filter(~User.id.in_(already_registered)).all()
            self.member_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                                      for u in available_users]
```

### PaymentUpdateForm

**Purpose**: Update payment status and amounts

```python
class PaymentUpdateForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0, max=999.99)], places=2)
    notes = TextAreaField('Payment Notes')
    submit = SubmitField('Update Payment')
```

## Routes and Views

### Event Management

#### Event Calendar (`/events/`)

**Template**: `events/calendar.html`  
**Access**: All authenticated users

**Features**:
- Upcoming events (next 30 days)
- Past events (last 30 days)
- Event details with registration info
- Admin controls for event management

**Implementation**:
```python
@events_bp.route('/')
@login_required
def calendar():
    now = datetime.now().date()
    thirty_days_ago = now - timedelta(days=30)
    thirty_days_from_now = now + timedelta(days=30)
    
    upcoming_events = ShootingEvent.query.filter(
        ShootingEvent.date >= now,
        ShootingEvent.date <= thirty_days_from_now
    ).order_by(ShootingEvent.date, ShootingEvent.start_time).all()
    
    past_events = ShootingEvent.query.filter(
        ShootingEvent.date >= thirty_days_ago,
        ShootingEvent.date < now
    ).order_by(ShootingEvent.date.desc(), ShootingEvent.start_time.desc()).all()
    
    return render_template('events/calendar.html',
                         upcoming_events=upcoming_events,
                         past_events=past_events)
```

#### Create Event (`/events/create`)

**Template**: `events/event_form.html`  
**Access**: Admin only  
**Form**: `ShootingEventForm`

**Process**:
1. Display event creation form
2. Validate event details
3. Create new ShootingEvent record
4. Associate with current admin user
5. Redirect to event calendar

#### View Event (`/events/<int:id>`)

**Template**: `events/view_event.html`  
**Access**: All authenticated users

**Information Displayed**:
- Complete event details
- Attendee list with status
- Registration statistics
- Payment information
- Admin controls

**Data Aggregation**:
```python
@events_bp.route('/<int:id>')
@login_required
def view_event(id):
    event = ShootingEvent.query.get_or_404(id)
    attendees = EventAttendance.query.filter_by(event_id=id).all()
    attendance_count = len(attendees)
    attended_count = sum(1 for a in attendees if hasattr(a, 'attended') and a.attended)
    
    # Calculate revenue for paid events
    total_revenue = 0
    if event.price > 0:
        paid_charges = MemberCharge.query.filter_by(
            event_id=id, is_paid=True
        ).all()
        total_revenue = sum(charge.amount for charge in paid_charges)
    
    return render_template('events/view_event.html',
                         event=event,
                         attendees=attendees,
                         attendance_count=attendance_count,
                         attended_count=attended_count,
                         total_revenue=total_revenue)
```

#### Edit Event (`/events/<int:id>/edit`)

**Template**: `events/event_form.html`  
**Access**: Admin only  
**Form**: `ShootingEventForm` (pre-populated)

**Considerations**:
- Existing registrations preserved
- Price changes don't affect existing charges
- Date/time changes notify attendees (future enhancement)

#### Delete Event (`/events/<int:id>/delete`)

**Method**: POST only  
**Access**: Admin only  
**Action**: Cascade delete with confirmation

**Implementation**:
```python
@events_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_event(id):
    event = ShootingEvent.query.get_or_404(id)
    
    # Check for existing registrations
    attendance_count = EventAttendance.query.filter_by(event_id=id).count()
    
    if attendance_count > 0:
        return jsonify({
            'success': False, 
            'error': f'Cannot delete event with {attendance_count} registered attendees'
        })
    
    try:
        # Delete associated charges first
        MemberCharge.query.filter_by(event_id=id).delete()
        db.session.delete(event)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

### Attendance Management

#### Manage Attendance (`/events/<int:id>/attendance`)

**Template**: `events/manage_attendance.html`  
**Access**: Admin only

**Features**:
- Real-time attendance tracking
- Bulk attendance operations
- Add walk-in attendees
- Payment status integration
- Attendance statistics

**Key Functionality**:
```python
@events_bp.route('/<int:id>/attendance', methods=['GET', 'POST'])
@admin_required
def manage_attendance(id):
    event = ShootingEvent.query.get_or_404(id)
    form = AttendanceForm(event_id=id)
    
    # Get all attendees with their details
    all_attendees = db.session.query(EventAttendance).filter_by(event_id=id).all()
    
    # Calculate statistics
    attended_count = sum(1 for a in all_attendees if hasattr(a, 'attended') and a.attended)
    total_collected = 0
    
    if event.price > 0:
        for attendee in all_attendees:
            charge = MemberCharge.query.filter_by(
                member_id=attendee.member_id, 
                event_id=id, 
                is_paid=True
            ).first()
            if charge:
                total_collected += charge.amount
    
    # Get available users for walk-in registration
    registered_member_ids = [a.member_id for a in all_attendees]
    available_users = User.query.filter(
        ~User.id.in_(registered_member_ids),
        User.is_active == True
    ).all()
    
    return render_template('events/manage_attendance.html',
                         event=event,
                         form=form,
                         all_attendees=all_attendees,
                         attended_count=attended_count,
                         total_collected=total_collected,
                         available_users=available_users)
```

#### Update Attendance (`/events/<int:id>/update-attendance`)

**Method**: POST only (AJAX)  
**Access**: Admin only  
**Response**: JSON

**Real-time Attendance Updates**:
```python
@events_bp.route('/<int:id>/update-attendance', methods=['POST'])
@admin_required
def update_attendance(id):
    data = request.get_json()
    attendee_id = data.get('attendee_id')
    attended = data.get('attended', False)
    
    try:
        attendance = EventAttendance.query.filter_by(
            event_id=id, member_id=attendee_id
        ).first()
        
        if not attendance:
            return jsonify({'success': False, 'error': 'Attendance record not found'})
        
        # Update attended status (stored as timestamp for attended_at)
        attendance.attended_at = datetime.utcnow() if attended else None
        attendance.recorded_by = current_user.id
        
        # Create charge if attending and event is paid
        event = ShootingEvent.query.get(id)
        if attended and event.price > 0:
            existing_charge = MemberCharge.query.filter_by(
                member_id=attendee_id, event_id=id
            ).first()
            
            if not existing_charge:
                charge = MemberCharge(
                    member_id=attendee_id,
                    event_id=id,
                    description=f"Charge for {event.name}",
                    amount=event.price,
                    is_paid=False
                )
                db.session.add(charge)
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

#### Add Attendee (`/events/<int:event_id>/add-attendee`)

**Method**: POST only  
**Access**: Admin only  
**Purpose**: Add walk-in attendees during events

**Implementation**:
```python
@events_bp.route('/<int:event_id>/add-attendee', methods=['POST'])
@admin_required
def add_attendee(event_id):
    event = ShootingEvent.query.get_or_404(event_id)
    
    member_id = request.form.get('member_id', type=int)
    mark_attended = request.form.get('mark_attended') == '1'
    
    if not member_id:
        flash('Please select a member', 'error')
        return redirect(url_for('events.manage_attendance', id=event_id))
    
    # Check if already registered
    existing = EventAttendance.query.filter_by(
        event_id=event_id, member_id=member_id
    ).first()
    
    if existing:
        flash('Member is already registered for this event', 'error')
        return redirect(url_for('events.manage_attendance', id=event_id))
    
    try:
        # Create attendance record
        attendance = EventAttendance(
            event_id=event_id,
            member_id=member_id,
            recorded_by=current_user.id
        )
        
        if mark_attended:
            attendance.attended_at = datetime.utcnow()
        
        db.session.add(attendance)
        
        # Create charge if event is paid and member attended
        if mark_attended and event.price > 0:
            member = User.query.get(member_id)
            charge = MemberCharge(
                member_id=member.id,
                event_id=event.id,
                description=f"Charge for {event.name}",
                amount=event.price,
                is_paid=False
            )
            db.session.add(charge)
        
        db.session.commit()
        
        member = User.query.get(member_id)
        flash(f'{member.first_name} {member.last_name} has been added to the event', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding attendee: {str(e)}', 'error')
    
    return redirect(url_for('events.manage_attendance', id=event_id))
```

### Payment Management

#### Outstanding Payments (`/events/payments`)

**Template**: `events/outstanding_payments.html`  
**Access**: Admin only

**Features**:
- All charges overview (paid and unpaid)
- Search and filter capabilities
- Payment status updates
- Charge amount editing
- Member communication tools

**Data Aggregation**:
```python
@events_bp.route('/payments')
@admin_required
def outstanding_payments():
    # Get all charges ordered by date
    all_charges = MemberCharge.query.order_by(
        MemberCharge.is_paid.asc(),  # Unpaid first
        MemberCharge.charge_date.desc()
    ).all()
    
    # Calculate statistics
    outstanding_charges = [c for c in all_charges if not c.is_paid]
    total_outstanding = sum(c.amount for c in outstanding_charges)
    total_paid = sum(c.amount for c in all_charges if c.is_paid)
    
    # Get unique members with outstanding charges
    unique_members = len(set(c.member_id for c in outstanding_charges))
    
    return render_template('events/outstanding_payments.html',
                         all_charges=all_charges,
                         outstanding_charges=outstanding_charges,
                         total_outstanding=total_outstanding,
                         total_paid=total_paid,
                         unique_members=unique_members)
```

#### Member Charges (`/events/my-charges`)

**Template**: `events/my_charges.html`  
**Access**: All authenticated users

**Features**:
- Personal charge history
- Payment status tracking
- Event links
- Outstanding balance summary

```python
@events_bp.route('/my-charges')
@login_required
def my_charges():
    charges = MemberCharge.query.filter_by(member_id=current_user.id).order_by(
        MemberCharge.charge_date.desc()
    ).all()
    
    outstanding_charges = [c for c in charges if not c.is_paid]
    paid_charges = [c for c in charges if c.is_paid]
    
    total_outstanding = sum(c.amount for c in outstanding_charges)
    total_paid = sum(c.amount for c in paid_charges)
    
    return render_template('events/my_charges.html',
                         my_charges=charges,
                         outstanding_charges=outstanding_charges,
                         paid_charges=paid_charges,
                         total_outstanding=total_outstanding,
                         total_paid=total_paid)
```

#### Payment Status Updates

**Mark as Paid (`/events/mark-paid`)**:
```python
@events_bp.route('/mark-paid', methods=['POST'])
@admin_required
def mark_paid():
    data = request.get_json()
    charge_id = data.get('charge_id')
    
    try:
        charge = MemberCharge.query.get_or_404(charge_id)
        charge.is_paid = True
        charge.paid_date = datetime.utcnow()
        charge.paid_by_admin = current_user.id
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

**Update Payment Status**:
```python
@events_bp.route('/update-payment-status', methods=['POST'])
@admin_required
def update_payment_status():
    data = request.get_json()
    charge_id = data.get('charge_id')
    paid = data.get('paid', False)
    
    try:
        charge = MemberCharge.query.get_or_404(charge_id)
        charge.is_paid = paid
        
        if paid:
            charge.paid_date = datetime.utcnow()
            charge.paid_by_admin = current_user.id
        else:
            charge.paid_date = None
            charge.paid_by_admin = None
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

## User Interface

### Calendar Template

**Monthly Calendar View**:
The calendar template displays events in an organized, chronological format:

```html
<!-- Upcoming Events Section -->
<div class="row">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
                <h5><i class="bi bi-calendar-plus text-success"></i> Upcoming Events</h5>
                {% if current_user.is_admin() %}
                    <a href="{{ url_for('events.create_event') }}" class="btn btn-success btn-sm">
                        <i class="bi bi-plus-circle"></i> Create Event
                    </a>
                {% endif %}
            </div>
            <div class="card-body">
                {% if upcoming_events %}
                    {% for event in upcoming_events %}
                        <div class="card mb-3 border-start border-3 border-success">
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start">
                                    <div class="flex-grow-1">
                                        <h6 class="card-title">
                                            <a href="{{ url_for('events.view_event', id=event.id) }}" class="text-decoration-none">
                                                {{ event.name }}
                                            </a>
                                        </h6>
                                        <p class="card-text mb-2">
                                            <i class="bi bi-geo-alt text-primary"></i> {{ event.location }}<br>
                                            <i class="bi bi-calendar text-primary"></i> {{ event.date.strftime('%A, %B %d, %Y') }}<br>
                                            <i class="bi bi-clock text-primary"></i> {{ event.start_time.strftime('%I:%M %p') }} - {{ event.end_time.strftime('%I:%M %p') }}
                                        </p>
                                        {% if event.description %}
                                            <p class="card-text text-muted">{{ event.description[:150] }}...</p>
                                        {% endif %}
                                    </div>
                                    <div class="text-end ms-3">
                                        {% if event.price > 0 %}
                                            <div class="h5 text-success mb-1">${{ "%.2f"|format(event.price) }}</div>
                                        {% else %}
                                            <div class="h5 text-success mb-1">FREE</div>
                                        {% endif %}
                                        <div class="text-muted small">
                                            {{ event.attendance_count() }} registered
                                            {% if event.max_participants %}
                                                / {{ event.max_participants }}
                                            {% endif %}
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="mt-3">
                                    <div class="btn-group btn-group-sm">
                                        <a href="{{ url_for('events.view_event', id=event.id) }}" class="btn btn-outline-primary">
                                            <i class="bi bi-eye"></i> View Details
                                        </a>
                                        {% if current_user.is_admin() %}
                                            <a href="{{ url_for('events.edit_event', id=event.id) }}" class="btn btn-outline-secondary">
                                                <i class="bi bi-pencil"></i> Edit
                                            </a>
                                            <a href="{{ url_for('events.manage_attendance', id=event.id) }}" class="btn btn-outline-success">
                                                <i class="bi bi-person-check"></i> Attendance
                                            </a>
                                        {% endif %}
                                    </div>
                                </div>
                            </div>
                        </div>
                    {% endfor %}
                {% else %}
                    <div class="text-center py-4">
                        <i class="bi bi-calendar-x display-3 text-muted"></i>
                        <h6 class="mt-3 text-muted">No Upcoming Events</h6>
                        <p class="text-muted">Check back later for new shooting events.</p>
                        {% if current_user.is_admin() %}
                            <a href="{{ url_for('events.create_event') }}" class="btn btn-primary">
                                <i class="bi bi-plus-circle"></i> Create First Event
                            </a>
                        {% endif %}
                    </div>
                {% endif %}
            </div>
        </div>
    </div>
    
    <!-- Sidebar with quick stats and actions -->
    <div class="col-md-4">
        <div class="card">
            <div class="card-header">
                <h6><i class="bi bi-graph-up text-info"></i> Event Statistics</h6>
            </div>
            <div class="card-body">
                <div class="row text-center">
                    <div class="col-6">
                        <div class="h4 text-primary">{{ upcoming_events|length }}</div>
                        <div class="small text-muted">Upcoming</div>
                    </div>
                    <div class="col-6">
                        <div class="h4 text-secondary">{{ past_events|length }}</div>
                        <div class="small text-muted">Past (30 days)</div>
                    </div>
                </div>
            </div>
        </div>
        
        {% if current_user.is_admin() %}
            <div class="card mt-3">
                <div class="card-header">
                    <h6><i class="bi bi-lightning text-warning"></i> Quick Actions</h6>
                </div>
                <div class="card-body d-grid gap-2">
                    <a href="{{ url_for('events.create_event') }}" class="btn btn-success">
                        <i class="bi bi-calendar-plus"></i> Create Event
                    </a>
                    <a href="{{ url_for('events.outstanding_payments') }}" class="btn btn-warning">
                        <i class="bi bi-currency-dollar"></i> Manage Payments
                    </a>
                </div>
            </div>
        {% endif %}
    </div>
</div>
```

### Attendance Management Interface

**Real-time Attendance Tracking**:
The attendance management interface provides real-time updates using AJAX:

```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Member</th>
                <th>Registration Time</th>
                <th>Attendance</th>
                <th>Payment Status</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for attendee in all_attendees %}
                <tr id="attendee-{{ attendee.id }}" class="{% if attendee.attended %}table-success{% endif %}">
                    <td>
                        <div class="d-flex align-items-center">
                            <i class="bi bi-person-circle text-muted me-2"></i>
                            <div>
                                <div class="fw-semibold">{{ attendee.member.first_name }} {{ attendee.member.last_name }}</div>
                                {% if attendee.member.is_admin() %}
                                    <small class="badge bg-primary">Admin</small>
                                {% endif %}
                            </div>
                        </div>
                    </td>
                    <td>
                        <small class="text-muted">{{ attendee.attended_at.strftime('%m/%d/%y %I:%M %p') if attendee.attended_at else 'Not recorded' }}</small>
                    </td>
                    <td>
                        <div class="form-check form-switch">
                            <input class="form-check-input attendance-checkbox" 
                                   type="checkbox" 
                                   name="attendee_{{ attendee.id }}"
                                   id="attendee_{{ attendee.id }}_check"
                                   value="1"
                                   {% if attendee.attended %}checked{% endif %}
                                   onchange="updateAttendanceStatus({{ attendee.id }}, this.checked)">
                            <label class="form-check-label" for="attendee_{{ attendee.id }}_check">
                                <span class="attended-label {% if not attendee.attended %}d-none{% endif %}">Attended</span>
                                <span class="not-attended-label {% if attendee.attended %}d-none{% endif %}">Not Attended</span>
                            </label>
                        </div>
                    </td>
                    <td>
                        {% if event.price == 0 %}
                            <span class="badge bg-success">Free Event</span>
                        {% else %}
                            {% set charge = attendee.charge %}
                            {% if charge %}
                                {% if charge.is_paid %}
                                    <span class="badge bg-success">
                                        <i class="bi bi-check-circle"></i> Paid (${{ "%.2f"|format(charge.amount) }})
                                    </span>
                                {% else %}
                                    <span class="badge bg-warning">
                                        <i class="bi bi-clock"></i> Outstanding (${{ "%.2f"|format(charge.amount) }})
                                    </span>
                                {% endif %}
                            {% else %}
                                <span class="badge bg-secondary">No Charge Created</span>
                            {% endif %}
                        {% endif %}
                    </td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            {% if event.price > 0 and attendee.charge and not attendee.charge.is_paid %}
                                <button type="button" class="btn btn-outline-success btn-sm" 
                                        onclick="markAsPaid({{ attendee.charge.id }})">
                                    <i class="bi bi-cash"></i> Mark Paid
                                </button>
                            {% endif %}
                            <button type="button" class="btn btn-outline-danger btn-sm"
                                    onclick="removeAttendee({{ attendee.id }})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

## JavaScript Functionality

### Real-time Attendance Updates

**AJAX Attendance Management**:
```javascript
function updateAttendanceStatus(attendeeId, attended) {
    const row = document.getElementById(`attendee-${attendeeId}`);
    const attendedLabel = row.querySelector('.attended-label');
    const notAttendedLabel = row.querySelector('.not-attended-label');
    
    // Update UI immediately for responsiveness
    if (attended) {
        row.classList.add('table-success');
        attendedLabel.classList.remove('d-none');
        notAttendedLabel.classList.add('d-none');
    } else {
        row.classList.remove('table-success');
        attendedLabel.classList.add('d-none');
        notAttendedLabel.classList.remove('d-none');
    }
    
    // Send AJAX request to update backend
    fetch(`{{ url_for('events.update_attendance', id=event.id) }}`, {
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
            // Revert UI changes if request failed
            const checkbox = document.getElementById(`attendee_${attendeeId}_check`);
            checkbox.checked = !attended;
            updateAttendanceStatus(attendeeId, !attended);
            alert('Failed to update attendance. Please try again.');
        }
    }).catch(error => {
        console.error('Error:', error);
        // Revert UI changes
        const checkbox = document.getElementById(`attendee_${attendeeId}_check`);
        checkbox.checked = !attended;
        updateAttendanceStatus(attendeeId, !attended);
        alert('Network error. Please check your connection and try again.');
    });
}
```

### Bulk Attendance Operations

**Mark All Attended**:
```javascript
function markAllAttended() {
    if (confirm('Mark all registered members as attended?')) {
        const checkboxes = document.querySelectorAll('.attendance-checkbox');
        let updateCount = 0;
        let totalToUpdate = 0;
        
        // Count unchecked boxes
        checkboxes.forEach(checkbox => {
            if (!checkbox.checked) totalToUpdate++;
        });
        
        if (totalToUpdate === 0) {
            alert('All members are already marked as attended.');
            return;
        }
        
        // Update each unchecked checkbox
        checkboxes.forEach(checkbox => {
            if (!checkbox.checked) {
                checkbox.checked = true;
                const attendeeId = parseInt(checkbox.name.replace('attendee_', ''));
                
                // Update UI
                updateAttendanceStatus(attendeeId, true);
                
                // Send AJAX request
                fetch(`{{ url_for('events.update_attendance', id=event.id) }}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
                    },
                    body: JSON.stringify({
                        attendee_id: attendeeId,
                        attended: true
                    })
                }).then(response => {
                    updateCount++;
                    if (updateCount === totalToUpdate) {
                        // All updates complete
                        location.reload(); // Refresh to show updated payment status
                    }
                }).catch(error => {
                    console.error('Error updating attendance:', error);
                });
            }
        });
    }
}
```

### Payment Management

**Mark Payment as Paid**:
```javascript
function markAsPaid(chargeId) {
    if (confirm('Mark this charge as paid?')) {
        fetch(`{{ url_for('events.mark_paid') }}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('input[name="csrf_token"]').value
            },
            body: JSON.stringify({
                charge_id: chargeId
            })
        }).then(response => response.json()).then(data => {
            if (data.success) {
                location.reload(); // Refresh to show updated payment status
            } else {
                alert(data.error || 'Failed to update payment status');
            }
        }).catch(error => {
            console.error('Error:', error);
            alert('Network error. Please try again.');
        });
    }
}
```

## Access Control

### Permission Levels

**All Users (Members and Admins)**:
- View events calendar
- View event details
- View own charges
- Access personal payment history

**Admin Only**:
- Create new events
- Edit existing events
- Delete events
- Manage event attendance
- Add walk-in attendees
- Update payment status
- View all member charges
- Access payment management dashboard

### Route Protection

**Admin-Required Routes**:
```python
@events_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_event():
    # Event creation logic
    pass

@events_bp.route('/<int:id>/attendance')
@login_required
@admin_required
def manage_attendance(id):
    # Attendance management logic
    pass

@events_bp.route('/payments')
@login_required
@admin_required
def outstanding_payments():
    # Payment management logic
    pass
```

**Template Access Control**:
```html
{% if current_user.is_admin() %}
    <div class="admin-controls">
        <a href="{{ url_for('events.create_event') }}" class="btn btn-success">Create Event</a>
        <a href="{{ url_for('events.manage_attendance', id=event.id) }}" class="btn btn-info">Manage Attendance</a>
    </div>
{% endif %}
```

## Business Logic

### Automatic Charge Creation

**Event Attendance → Charge Logic**:
When a member is marked as attended for a paid event, a charge is automatically created:

```python
def create_event_charge(member_id, event_id):
    """Create a charge when member attends paid event"""
    event = ShootingEvent.query.get(event_id)
    
    if event.price <= 0:
        return None  # No charge for free events
    
    # Check if charge already exists
    existing_charge = MemberCharge.query.filter_by(
        member_id=member_id,
        event_id=event_id
    ).first()
    
    if existing_charge:
        return existing_charge
    
    # Create new charge
    charge = MemberCharge(
        member_id=member_id,
        event_id=event_id,
        description=f"Charge for {event.name}",
        amount=event.price,
        is_paid=False
    )
    
    db.session.add(charge)
    db.session.commit()
    
    return charge
```

### Event Capacity Management

**Registration Limits**:
Events can have maximum participant limits:

```python
def can_register_for_event(event_id):
    """Check if event has capacity for new registrations"""
    event = ShootingEvent.query.get(event_id)
    
    if not event.max_participants:
        return True  # Unlimited capacity
    
    current_count = EventAttendance.query.filter_by(event_id=event_id).count()
    return current_count < event.max_participants
```

### Payment Status Tracking

**Member Outstanding Balance**:
```python
def get_member_outstanding_balance(member_id):
    """Calculate total outstanding charges for a member"""
    unpaid_charges = MemberCharge.query.filter_by(
        member_id=member_id,
        is_paid=False
    ).all()
    
    return sum(charge.amount for charge in unpaid_charges)
```

## Reporting and Analytics

### Event Statistics

**Dashboard Metrics**:
```python
def get_event_statistics():
    """Get comprehensive event statistics"""
    now = datetime.now().date()
    
    # Upcoming events count
    upcoming_count = ShootingEvent.query.filter(
        ShootingEvent.date >= now
    ).count()
    
    # This month's events
    this_month_start = now.replace(day=1)
    this_month_events = ShootingEvent.query.filter(
        ShootingEvent.date >= this_month_start,
        ShootingEvent.date <= now
    ).count()
    
    # Total revenue this month
    this_month_revenue = db.session.query(
        func.sum(MemberCharge.amount)
    ).filter(
        MemberCharge.charge_date >= this_month_start,
        MemberCharge.is_paid == True
    ).scalar() or 0
    
    # Outstanding payments
    outstanding_total = db.session.query(
        func.sum(MemberCharge.amount)
    ).filter(MemberCharge.is_paid == False).scalar() or 0
    
    return {
        'upcoming_events': upcoming_count,
        'this_month_events': this_month_events,
        'this_month_revenue': this_month_revenue,
        'outstanding_total': outstanding_total
    }
```

### Attendance Reports

**Event Attendance Summary**:
```python
def get_attendance_report(event_id):
    """Generate comprehensive attendance report for event"""
    event = ShootingEvent.query.get(event_id)
    attendances = EventAttendance.query.filter_by(event_id=event_id).all()
    
    total_registered = len(attendances)
    total_attended = sum(1 for a in attendances if a.attended_at)
    attendance_rate = (total_attended / total_registered * 100) if total_registered > 0 else 0
    
    # Payment statistics
    if event.price > 0:
        charges = MemberCharge.query.filter_by(event_id=event_id).all()
        total_charges = sum(c.amount for c in charges)
        paid_charges = sum(c.amount for c in charges if c.is_paid)
        payment_rate = (len([c for c in charges if c.is_paid]) / len(charges) * 100) if charges else 0
    else:
        total_charges = paid_charges = payment_rate = 0
    
    return {
        'event': event,
        'total_registered': total_registered,
        'total_attended': total_attended,
        'attendance_rate': attendance_rate,
        'total_charges': total_charges,
        'paid_charges': paid_charges,
        'payment_rate': payment_rate
    }
```

## Integration Points

### Dashboard Integration

**Event Statistics on Dashboard**:
The main dashboard displays key event metrics:
- Upcoming events count (next 30 days)
- Recent event activity
- Outstanding payment alerts
- Quick action buttons for admins

### Member Integration

**Member Event History**:
- Events attended by member
- Payment history for events
- Outstanding balances
- Registration activity

### Inventory Integration (Future)

**Equipment Tracking for Events**:
- Equipment check-out for events
- Usage tracking by event
- Equipment maintenance scheduling
- Inventory requirements planning

## Future Enhancements

### Planned Features

**Advanced Event Management**:
- Recurring events
- Event templates
- Waiting lists for full events
- Multi-day events
- Event categories and tags

**Enhanced Attendance**:
- QR code check-in
- Mobile attendance app
- Automated attendance reminders
- Guest registration system

**Payment Improvements**:
- Online payment integration (Stripe, PayPal)
- Automatic payment reminders
- Payment plans and installments
- Refund management

**Communication Features**:
- Event notifications (email/SMS)
- Member communication tools
- Event updates and announcements
- Calendar synchronization (Google, Outlook)

**Reporting Enhancements**:
- Advanced analytics dashboard
- Custom report builder
- Export capabilities (PDF, Excel)
- Trend analysis and forecasting

### Technical Improvements

**Performance Optimization**:
- Database query optimization
- Caching for frequently accessed data
- Pagination improvements
- Mobile app development

**User Experience**:
- Progressive web app features
- Offline functionality
- Real-time notifications
- Enhanced mobile interface

**Integration Capabilities**:
- API development for third-party integration
- Webhook support for external systems
- Calendar application synchronization
- Equipment management system integration
