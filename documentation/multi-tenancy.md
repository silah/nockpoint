# Multi-Tenancy Architecture

## Overview

Nockpoint is a multi-tenant platform supporting multiple independent archery clubs. Each club operates with complete data isolation, and users can be members of multiple clubs.

## Core Features

### Club Independence
- Each club has its own members, events, inventory, and competitions
- Complete data segregation between clubs
- Club-specific settings and customization
- Per-club admin roles

### User Management
- Users can belong to multiple clubs
- Role-based permissions per club (admin or member)
- Club selection on login for multi-club users
- Automatic context switching

### Club Registration
- Public club registration flow
- First user automatically becomes admin
- Customizable club settings and pricing
- Optional activation codes for member registration

## Database Architecture

### Core Models

#### Club Model
Represents an archery club in the system:
- Basic info: name, slug, description
- Contact details: email, phone, address, website
- Social media links
- Club settings (location, activation code)
- Membership pricing (annual, quarterly, monthly, per-event)
- Pro subscription status

#### ClubMembership Model
Links users to clubs with roles:
- `user_id` and `club_id` (unique constraint)
- `role`: 'admin' or 'member'
- `membership_type`: monthly, quarterly, annual, per_event
- `is_active`: membership status
- `joined_at`: membership date

### Data Scoping

All club-specific models include `club_id` foreign key:
- **Inventory**: InventoryCategory, InventoryItem
- **Events**: ShootingEvent, EventAttendance, MemberCharge
- **Competitions**: Competition, CompetitionGroup, CompetitionTeam, etc.
- **Members**: Via ClubMembership

## Authentication Flow

### Login Process
1. User enters credentials
2. System validates user
3. If user has multiple clubs: show club selection
4. If user has one club: auto-select
5. Club context stored in session (`g.current_club`)

### Registration Options

**Club Registration** (`/auth/register-club`):
- Creates new club and admin user
- Generates unique club slug
- Sets up default settings

**Member Registration** (`/auth/register`):
- User selects club from dropdown
- Optional activation code verification
- Creates user and club membership

## Developer Guide

### Authorization Decorators

Use these decorators for route protection:

```python
from app.decorators import require_club_context, require_club_admin, require_club_member

# Any authenticated club member
@require_club_context
def member_route():
    pass

# Club admin only
@require_club_admin
def admin_route():
    pass

# Specific member verification
@require_club_member
def specific_member_route():
    pass
```

### Accessing Current Club

```python
from flask import g

# In route handlers
@require_club_context
def my_route():
    club = g.current_club  # Current club object
    membership = g.current_membership  # User's membership in club
    
    # Query club-specific data
    items = InventoryItem.query.filter_by(club_id=club.id).all()
```

### Creating Records

**ALWAYS** set `club_id` when creating club-specific records:

```python
@require_club_admin
def create_item():
    item = InventoryItem(
        club_id=g.current_club.id,  # Required!
        name=form.name.data,
        quantity=form.quantity.data
    )
    db.session.add(item)
    db.session.commit()
```

### Querying Records

**ALWAYS** filter by `club_id` to prevent cross-club data leakage:

```python
# ✅ CORRECT
items = InventoryItem.query.filter_by(
    club_id=g.current_club.id
).all()

# ❌ WRONG - exposes data from all clubs!
items = InventoryItem.query.all()
```

### Viewing/Editing Records

Verify ownership by filtering on both ID and club_id:

```python
@require_club_context
def view_item(id):
    item = InventoryItem.query.filter_by(
        id=id,
        club_id=g.current_club.id
    ).first_or_404()  # 404 if wrong club
    
    return render_template('view.html', item=item)
```

### Forms with Relationships

Filter dropdown choices by current club:

```python
class EventForm(FlaskForm):
    category_id = SelectField('Category', coerce=int)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if hasattr(g, 'current_club') and g.current_club:
            self.category_id.choices = [
                (c.id, c.name) 
                for c in InventoryCategory.query
                    .filter_by(club_id=g.current_club.id)
                    .all()
            ]
```

### Template Helpers

Built-in template functions:

```html
<!-- Check if user is admin of current club -->
{% if is_club_admin() %}
    <a href="{{ url_for('admin.settings') }}">Settings</a>
{% endif %}

<!-- Display club info -->
<h1>{{ current_club.name }}</h1>
<p>Role: {{ current_membership.role }}</p>
```

### User Model Methods

```python
# Check admin status for specific club
if current_user.is_admin_of_club(club_id):
    # Admin actions

# Check membership
if current_user.is_member_of_club(club_id):
    # Member actions

# Get user's role in club
role = current_user.get_role_in_club(club_id)  # 'admin' or 'member' or None

# Get all clubs user belongs to
clubs = current_user.get_clubs()  # List of Club objects
```

## Common Patterns

### Creating a Member-Only Route

```python
@my_bp.route('/view')
@login_required
@require_club_context
def view_data():
    items = MyModel.query.filter_by(club_id=g.current_club.id).all()
    return render_template('view.html', items=items)
```

### Creating an Admin-Only Route

```python
@my_bp.route('/manage')
@login_required
@require_club_admin
def manage_data():
    items = MyModel.query.filter_by(club_id=g.current_club.id).all()
    return render_template('manage.html', items=items)
```

### Conditional Admin Features in Templates

```html
<div class="member-content">
    <!-- Everyone sees this -->
</div>

{% if is_club_admin() %}
<div class="admin-controls">
    <button>Delete</button>
    <button>Edit</button>
</div>
{% endif %}
```

## Security Considerations

### Critical Rules

1. **Never query without club filter** - Prevents cross-club data leakage
2. **Always use decorators** - Ensures proper authorization
3. **Filter on ID + club_id** - When accessing specific records
4. **Set club_id on creation** - All new records must belong to a club
5. **Use club-scoped helpers** - `is_club_admin()` not deprecated `is_admin()`

### Data Isolation Checklist

When working with any club-specific model:
- [ ] Does the query filter by `club_id`?
- [ ] Is `club_id` set on record creation?
- [ ] Are decorators applied for authorization?
- [ ] Does the route verify club ownership?
- [ ] Are form choices filtered by club?

## Testing Multi-Tenancy

### Test Multiple Clubs

```python
def test_club_isolation():
    club1 = Club(name="Club 1", slug="club1")
    club2 = Club(name="Club 2", slug="club2")
    db.session.add_all([club1, club2])
    
    # Create items for each club
    item1 = Item(club_id=club1.id, name="Item 1")
    item2 = Item(club_id=club2.id, name="Item 2")
    db.session.add_all([item1, item2])
    
    # Verify isolation
    club1_items = Item.query.filter_by(club_id=club1.id).all()
    assert len(club1_items) == 1
    assert club1_items[0].name == "Item 1"
```

### Test Cross-Club Access Prevention

```python
def test_cannot_access_other_club_data(client, club1, club2, user):
    # User is member of club1
    membership = ClubMembership(user_id=user.id, club_id=club1.id, role='member')
    db.session.add(membership)
    
    # Create item in club2
    item = Item(club_id=club2.id, name="Club 2 Item")
    db.session.add(item)
    db.session.commit()
    
    # Login and set club1 context
    login_user(user)
    with client.session_transaction() as sess:
        sess['current_club_id'] = club1.id
    
    # Try to access club2's item - should get 404
    response = client.get(f'/items/{item.id}')
    assert response.status_code == 404
```

## Migration Notes

The multi-tenancy system was implemented in January 2026. All existing data was migrated to use the new club-based structure. Key changes:

- Removed global `User.role` field (replaced with per-club roles in ClubMembership)
- Added `club_id` to all club-specific models
- Created `Club` and `ClubMembership` models
- Updated all routes and templates to use club context
- Replaced `current_user.is_admin()` with `is_club_admin()` throughout templates

For detailed migration history, see git commit logs from January 2026.
