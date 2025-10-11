# Database Models Documentation

## Overview

The application uses SQLAlchemy ORM to define database models with relationships. All models inherit from `db.Model` and include proper constraints and relationships.

## Core Models

### User Model
**File**: `app/models.py`  
**Table**: `user`

Represents system users (both members and administrators).

```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='member')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Key Features**:
- Flask-Login integration with `UserMixin`
- Password hashing with Werkzeug
- Role-based access control (admin/member)
- Unique constraints on username and email

**Relationships**:
- `inventory_items` - Items created by this user
- `event_attendances` - Events attended
- `charges` - Financial charges for this member

**Methods**:
- `set_password()` - Hash and store password
- `check_password()` - Verify password against hash
- `is_admin()` - Check if user has admin role

### InventoryCategory Model
**Table**: `inventory_category`

Categorizes inventory items for organization.

```python
class InventoryCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Relationships**:
- `items` - One-to-many with InventoryItem

### InventoryItem Model
**Table**: `inventory_item`

Individual items in the club's inventory.

```python
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_category.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Relationships**:
- `category` - Many-to-one with InventoryCategory
- `creator` - Many-to-one with User

## Events System Models

### ShootingEvent Model
**Table**: `shooting_event`

Represents shooting events organized by the club.

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
    max_participants = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Computed Properties**:
- `end_time` - Calculated from start_time + duration_hours
- `is_past` - Boolean indicating if event date has passed
- `attendance_count` - Number of registered attendees

**Relationships**:
- `creator` - Many-to-one with User
- `attendances` - One-to-many with EventAttendance
- `charges` - One-to-many with MemberCharge

### EventAttendance Model
**Table**: `event_attendance`

Tracks member attendance at shooting events.

```python
class EventAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    attended_at = db.Column(db.DateTime, default=datetime.utcnow)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    notes = db.Column(db.Text)
```

**Constraints**:
- Unique constraint on `(event_id, member_id)` prevents duplicate attendance

**Relationships**:
- `event` - Many-to-one with ShootingEvent
- `member` - Many-to-one with User (attendee)
- `recorder` - Many-to-one with User (admin who recorded)

### MemberCharge Model
**Table**: `member_charge`

Financial charges for members (events, fees, etc.).

```python
class MemberCharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=True)
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    charge_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    paid_by_admin = db.Column(db.Integer, db.ForeignKey('user.id'))
    payment_notes = db.Column(db.Text)
```

**Relationships**:
- `member` - Many-to-one with User (charged member)
- `event` - Many-to-one with ShootingEvent (nullable for non-event charges)
- `admin` - Many-to-one with User (admin who marked as paid)

## Model Interactions

### User-Centric Relationships
- **User** → **InventoryItem**: Users create inventory items
- **User** → **EventAttendance**: Users attend events
- **User** → **MemberCharge**: Users have financial charges
- **User** → **ShootingEvent**: Admin users create events

### Event Workflow
1. **ShootingEvent** created by admin
2. **EventAttendance** records created for participants
3. **MemberCharge** automatically created for paid events
4. **Admin** manages attendance and payment status

### Inventory Management
1. **InventoryCategory** provides organization
2. **InventoryItem** belongs to category
3. **User** (admin) manages both categories and items

## Database Constraints

### Primary Keys
All models use auto-incrementing integer primary keys.

### Foreign Keys
- Proper foreign key constraints maintain referential integrity
- Cascade deletion handled at application level for safety

### Unique Constraints
- User.username and User.email must be unique
- InventoryCategory.name must be unique
- EventAttendance has composite unique constraint on (event_id, member_id)

### Default Values
- Timestamps default to `datetime.utcnow`
- Boolean fields have appropriate defaults
- Numeric fields default to 0 or 0.00

## Migration Management

The application uses Flask-Migrate for database schema management:

```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade

# Downgrade migration
flask db downgrade
```

Migrations are stored in the `migrations/versions/` directory and should be version controlled.

## Best Practices

1. **Relationships**: Use SQLAlchemy relationships instead of manual joins
2. **Validation**: Database constraints complement form validation
3. **Timestamps**: All models include creation timestamps
4. **Soft Deletes**: Consider is_active flags instead of hard deletes
5. **Indexes**: Add indexes on frequently queried columns

## Testing Models

Use the provided `test_events.py` script to verify model functionality:

```bash
python test_events.py
```

This validates model creation, relationships, and basic CRUD operations.
