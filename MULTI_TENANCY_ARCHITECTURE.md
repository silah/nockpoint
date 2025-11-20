# Multi-Tenancy Architecture for Nockpoint

## Overview
This document outlines the architectural changes needed to transform Nockpoint from a single-club system to a multi-tenant platform supporting multiple independent archery clubs.

## Core Objectives

### Immediate Implementation
1. **Club Isolation**: Each club operates independently with its own members, events, inventory, and competitions
2. **Club Registration**: Public-facing club registration flow for new clubs to join the platform
3. **Club Selection**: Users can be members of multiple clubs and switch between them
4. **Data Segregation**: Complete data isolation between clubs (no cross-club data leakage)

### Future Extensions (Architecture Considerations)
1. **Open Invite Events**: Events that clubs can make visible to members of other clubs
2. **Global Events Board**: Cross-club event discovery and registration
3. **Community Board**: Twitter-style social feed for all clubs to participate in

## Database Schema Changes

### New Models

#### 1. Club Model
Primary entity representing an archery club in the system.

```python
class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    slug = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    
    # Contact information
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    website_url = db.Column(db.String(200))
    
    # Social media
    facebook_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    
    # Settings (migrated from ClubSettings)
    default_location = db.Column(db.String(200))
    activation_code = db.Column(db.String(50))
    
    # Pricing
    annual_membership_price = db.Column(db.Numeric(10, 2), default=0.00)
    quarterly_membership_price = db.Column(db.Numeric(10, 2), default=0.00)
    monthly_membership_price = db.Column(db.Numeric(10, 2), default=0.00)
    per_event_price = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Pro subscription (per club)
    is_pro_enabled = db.Column(db.Boolean, default=False)
    pro_subscription_id = db.Column(db.String(100))
    pro_expires_at = db.Column(db.DateTime)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('ClubMembership', backref='club', lazy=True)
```

#### 2. ClubMembership Model
Junction table allowing users to belong to multiple clubs with role per club.

```python
class ClubMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin' or 'member'
    membership_type = db.Column(db.String(20), default='monthly')
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'club_id', name='unique_user_club'),)
```

### Model Updates (Add club_id foreign key)

All club-specific data models need a `club_id` foreign key:

- **InventoryCategory**: `club_id` (each club has its own categories)
- **InventoryItem**: `club_id` (inherit from category or explicit)
- **ShootingEvent**: `club_id` (events belong to clubs)
- **EventAttendance**: Via event relationship
- **MemberCharge**: Via user/event relationships
- **Competition**: `club_id` (via event or explicit)
- **CompetitionGroup**: Via competition
- **CompetitionTeam**: Via group
- **CompetitionRegistration**: Via competition
- **ArrowScore**: Via registration
- **BeginnersStudent**: `club_id` (via event or explicit)

### User Model Changes

```python
class User(UserMixin, db.Model):
    # Remove role and membership_type (moved to ClubMembership)
    # Add relationship to clubs
    club_memberships = db.relationship('ClubMembership', backref='user', lazy=True)
    
    def get_clubs(self):
        """Get all clubs user is a member of"""
        return [m.club for m in self.club_memberships if m.is_active]
    
    def get_role_in_club(self, club_id):
        """Get user's role in a specific club"""
        membership = ClubMembership.query.filter_by(
            user_id=self.id, club_id=club_id
        ).first()
        return membership.role if membership else None
    
    def is_admin_of_club(self, club_id):
        """Check if user is admin of specific club"""
        return self.get_role_in_club(club_id) == 'admin'
```

## Authentication & Session Flow

### Registration Flow Changes

1. **Club Registration (New)**
   - Public route: `/register-club`
   - Form: Club name, slug, admin email, admin password, contact info
   - Creates new Club record
   - Creates first admin User
   - Creates ClubMembership linking them

2. **User Registration (Updated)**
   - Context-aware: Happens within a club context
   - Route: `/{club_slug}/auth/register`
   - Uses club's activation code (if set)
   - Creates User and ClubMembership for that club

### Login Flow Changes

1. User enters username/email and password
2. System validates credentials
3. If user belongs to multiple clubs:
   - Show club selection screen
   - User chooses which club to access
4. If user belongs to one club:
   - Automatically select that club
5. Store `current_club_id` in session
6. Redirect to club dashboard

### Session Management

```python
# Store in session
session['current_club_id'] = club_id

# Access current club
def get_current_club():
    club_id = session.get('current_club_id')
    if club_id:
        return Club.query.get(club_id)
    return None
```

## URL Structure

### Multi-Tenant URL Patterns

```
# Public routes (no club context)
/                           # Landing page with "Register New Club"
/register-club              # Club registration
/login                      # Initial login (club selection happens after)

# Club-scoped routes (all existing routes)
/{club_slug}/               # Club home/landing
/{club_slug}/dashboard      # Club dashboard
/{club_slug}/inventory/...  # Inventory management
/{club_slug}/events/...     # Events management
/{club_slug}/members/...    # Member management
/{club_slug}/competitions/... # Competition management
/{club_slug}/settings       # Club settings

# Club switching
/switch-club                # Show available clubs for user
/switch-club/{club_id}      # Switch to specific club
```

## Middleware & Request Context

### Club Context Middleware

```python
@app.before_request
def load_club_context():
    """Load current club into g.current_club for all requests"""
    if current_user.is_authenticated:
        club_id = session.get('current_club_id')
        if club_id:
            g.current_club = Club.query.get(club_id)
            
            # Verify user has access to this club
            membership = ClubMembership.query.filter_by(
                user_id=current_user.id,
                club_id=club_id,
                is_active=True
            ).first()
            
            if not membership:
                # User doesn't have access, clear session
                session.pop('current_club_id', None)
                g.current_club = None
```

### Query Filtering Helper

```python
def club_filter(model_class):
    """Apply club filter to queries automatically"""
    if hasattr(g, 'current_club') and g.current_club:
        return model_class.query.filter_by(club_id=g.current_club.id)
    return model_class.query

# Usage:
items = club_filter(InventoryItem).all()
events = club_filter(ShootingEvent).filter(date >= today).all()
```

## Migration Strategy

### Phase 1: Add Club Infrastructure
1. Create Club and ClubMembership models
2. Add migration script
3. Create default club from existing ClubSettings
4. Migrate all existing users to default club

### Phase 2: Add Foreign Keys
1. Add club_id columns to all relevant models
2. Populate with default club ID
3. Make club_id NOT NULL
4. Add foreign key constraints

### Phase 3: Update Application Logic
1. Update all queries to filter by club
2. Update forms to include club context
3. Update templates
4. Update authentication flow

### Phase 4: Testing & Validation
1. Test data isolation
2. Test club switching
3. Test new club registration
4. Update unit tests

## Data Migration Script Example

```python
def migrate_to_multi_tenancy():
    """One-time migration from single-tenant to multi-tenant"""
    
    # Create default club from existing settings
    settings = ClubSettings.query.first()
    default_club = Club(
        name=settings.club_name if settings else "Default Club",
        slug="default",
        email=settings.email if settings else None,
        # ... copy other settings
    )
    db.session.add(default_club)
    db.session.flush()
    
    # Migrate all users to default club
    users = User.query.all()
    for user in users:
        membership = ClubMembership(
            user_id=user.id,
            club_id=default_club.id,
            role=user.role,  # Copy existing role
            membership_type=user.membership_type
        )
        db.session.add(membership)
    
    # Add club_id to all existing data
    for model in [InventoryCategory, InventoryItem, ShootingEvent, ...]:
        db.session.execute(
            model.__table__.update().values(club_id=default_club.id)
        )
    
    db.session.commit()
```

## Future Features Architecture

### 1. Open Invite Events

**Database Changes:**
```python
class ShootingEvent(db.Model):
    # Add fields
    is_open_invite = db.Column(db.Boolean, default=False)
    max_external_participants = db.Column(db.Integer)
    
class EventAttendance(db.Model):
    # Already has member_id linking to User
    # User's club_memberships will show which club they're from
    attending_as_club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
```

**Logic:**
- Events can be marked as "Open Invite"
- Visible on global events board
- Members from other clubs can register
- Track which club they're representing

### 2. Global Events Board

**New Model:**
```python
class GlobalEvent(db.Model):
    """View/aggregation of all open invite events across clubs"""
    # Could be a database view or materialized view
    # Includes events where is_open_invite=True
```

**Access:**
- Route: `/events/global` (no club slug)
- Shows all open invite events from all clubs
- Filterable by date, location, type
- Click through shows club-specific event page

### 3. Community Board

**New Models:**
```python
class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))  # Posted as member of this club
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
class CommunityPostReaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reaction_type = db.Column(db.String(20))  # like, helpful, etc.

class CommunityPoll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('community_post.id'))
    question = db.Column(db.String(500))
    # Poll options and votes
```

**Access:**
- Route: `/community` (no club slug)
- Global feed visible to all authenticated users
- Posts show user's name + club badge
- Reactions, polls, threading support

## Security Considerations

1. **Club Isolation**: All queries MUST filter by club_id
2. **Authorization**: Check club membership before granting access
3. **Session Security**: Validate current_club_id against user's memberships
4. **URL Tampering**: Verify club_slug matches session club
5. **CSRF Protection**: Maintain per-club CSRF tokens
6. **Data Leakage**: Never expose IDs or slugs of other clubs' data

## Performance Considerations

1. **Indexing**: Add indexes on all club_id foreign keys
2. **Caching**: Cache club information per session
3. **Query Optimization**: Use joins instead of multiple queries
4. **Club Switching**: Minimize database hits on switch

## Testing Strategy

1. **Unit Tests**: Test all models with multiple clubs
2. **Integration Tests**: Test club isolation
3. **E2E Tests**: Test complete user flows across clubs
4. **Security Tests**: Test unauthorized access attempts
5. **Migration Tests**: Verify data migration correctness

## Implementation Order

1. ✅ Create architecture document (this file)
2. Create Club and ClubMembership models
3. Create migration script
4. Update User model
5. Add club_id to all models
6. Update authentication flow
7. Add club registration flow
8. Update all views/routes with club filtering
9. Update templates
10. Add club switching UI
11. Update tests
12. Manual QA testing
13. Documentation updates

---

**Status**: Architecture Complete - Ready for Implementation
**Date**: November 16, 2025
**Branch**: multi-tenancy
