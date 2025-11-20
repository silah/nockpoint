# Multi-Tenancy Implementation Guide

This document provides step-by-step instructions for implementing multi-tenancy in Nockpoint.

## Implementation Status

### ✅ Completed
- [x] Architecture design and documentation
- [x] Club and ClubMembership models created
- [x] User model updated with club relationship methods
- [x] Foreign keys added to all models (InventoryCategory, InventoryItem, ShootingEvent, Competition, BeginnersStudent)
- [x] Data migration script created

### 🔄 In Progress
- [ ] Database migration generation
- [ ] Authentication flow updates
- [ ] Club registration flow
- [ ] Middleware and context management
- [ ] Views and routes updates
- [ ] Template updates
- [ ] Testing

## Step-by-Step Implementation

### Phase 1: Database Migration (CURRENT)

#### 1.1 Generate Migration

```bash
# Make sure you're in the virtual environment
source venv/bin/activate  # or appropriate activation command

# Generate migration
flask db migrate -m "Add multi-tenancy support with Club and ClubMembership models"

# Review the generated migration file in migrations/versions/
# Make any necessary adjustments
```

#### 1.2 Update Migration (if needed)

The auto-generated migration might need adjustments:

- Ensure `club_id` columns are created with proper defaults
- Add indexes on `club_id` columns
- Handle nullable constraints properly during transition

Example migration adjustments:

```python
def upgrade():
    # Create Club table first
    op.create_table('club', ...)
    
    # Create ClubMembership table
    op.create_table('club_membership', ...)
    
    # Add club_id columns as nullable first
    op.add_column('inventory_category', sa.Column('club_id', sa.Integer(), nullable=True))
    op.add_column('inventory_item', sa.Column('club_id', sa.Integer(), nullable=True))
    # ... repeat for all tables
    
    # Create indexes
    op.create_index(op.f('ix_inventory_category_club_id'), 'inventory_category', ['club_id'])
    # ... repeat for all tables

def downgrade():
    # Reverse all changes
    pass
```

#### 1.3 Apply Migration

```bash
# Apply the migration
flask db upgrade

# If any errors occur, rollback and fix:
# flask db downgrade
```

#### 1.4 Run Data Migration

```bash
# Run the data migration script
python migrate_to_multitenancy.py

# Follow the prompts
# Verify the output
```

### Phase 2: Application Code Updates

#### 2.1 Add Club Context Middleware

Update `app/__init__.py`:

```python
from flask import g, session

def create_app(config=None):
    # ... existing code ...
    
    @app.before_request
    def load_club_context():
        """Load current club into request context"""
        from flask_login import current_user
        from app.models import Club, ClubMembership
        
        g.current_club = None
        
        if current_user.is_authenticated:
            club_id = session.get('current_club_id')
            
            if club_id:
                # Load club and verify user has access
                club = Club.query.get(club_id)
                if club:
                    membership = ClubMembership.query.filter_by(
                        user_id=current_user.id,
                        club_id=club_id,
                        is_active=True
                    ).first()
                    
                    if membership:
                        g.current_club = club
                        g.current_membership = membership
                    else:
                        # User doesn't have access, clear session
                        session.pop('current_club_id', None)
    
    @app.context_processor
    def inject_club_context():
        """Make club available in all templates"""
        return dict(
            current_club=getattr(g, 'current_club', None),
            current_membership=getattr(g, 'current_membership', None)
        )
    
    return app
```

#### 2.2 Create Club Helper Functions

Create `app/club_utils.py`:

```python
from flask import g, session, abort
from app.models import Club, ClubMembership
from flask_login import current_user
from functools import wraps

def get_current_club():
    """Get current club from request context"""
    return getattr(g, 'current_club', None)

def get_current_membership():
    """Get current user's membership in current club"""
    return getattr(g, 'current_membership', None)

def require_club_context(f):
    """Decorator to ensure club context is set"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_club():
            abort(400, "No club context")
        return f(*args, **kwargs)
    return decorated_function

def require_club_admin(f):
    """Decorator to require admin role in current club"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        club = get_current_club()
        if not club:
            abort(400, "No club context")
        
        if not current_user.is_authenticated:
            abort(401)
        
        if not current_user.is_admin_of_club(club.id):
            abort(403, "Admin access required")
        
        return f(*args, **kwargs)
    return decorated_function

def club_query(model_class):
    """Helper to filter queries by current club"""
    club = get_current_club()
    if club and hasattr(model_class, 'club_id'):
        return model_class.query.filter_by(club_id=club.id)
    return model_class.query
```

#### 2.3 Update Authentication Routes

Update `app/auth/__init__.py`:

Add club selection after login:

```python
@auth_bp.route('/select-club', methods=['GET', 'POST'])
@login_required
def select_club():
    """Allow user to select which club to access"""
    clubs = current_user.get_clubs()
    
    if not clubs:
        flash('You are not a member of any clubs.', 'warning')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        club_id = request.form.get('club_id', type=int)
        if club_id:
            # Verify user has access
            if current_user.is_member_of_club(club_id):
                session['current_club_id'] = club_id
                flash('Club selected successfully!', 'success')
                return redirect(url_for('main.dashboard'))
        flash('Invalid club selection.', 'error')
    
    return render_template('auth/select_club.html', clubs=clubs)

@auth_bp.route('/switch-club/<int:club_id>')
@login_required
def switch_club(club_id):
    """Quick club switching"""
    if current_user.is_member_of_club(club_id):
        session['current_club_id'] = club_id
        flash('Switched club successfully!', 'success')
    else:
        flash('Access denied to this club.', 'error')
    
    return redirect(request.referrer or url_for('main.dashboard'))
```

Update login route to handle club selection:

```python
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Check clubs
            clubs = user.get_clubs()
            if not clubs:
                flash('You are not a member of any clubs. Please contact support.', 'warning')
                logout_user()
                return redirect(url_for('auth.login'))
            elif len(clubs) == 1:
                # Auto-select the only club
                session['current_club_id'] = clubs[0].id
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                # Multiple clubs, show selection
                return redirect(url_for('auth.select_club'))
        
        flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)
```

#### 2.4 Create Club Registration

Create new blueprint `app/clubs/__init__.py`:

```python
from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user
from app import db
from app.models import Club, User, ClubMembership
from app.forms import ClubRegistrationForm
from slugify import slugify  # pip install python-slugify

clubs_bp = Blueprint('clubs', __name__)

@clubs_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Public club registration"""
    form = ClubRegistrationForm()
    
    if form.validate_on_submit():
        # Generate slug from club name
        slug = slugify(form.club_name.data)
        
        # Check if slug exists
        if Club.query.filter_by(slug=slug).first():
            flash('A club with this name already exists.', 'error')
            return render_template('clubs/register.html', form=form)
        
        # Create club
        club = Club(
            name=form.club_name.data,
            slug=slug,
            description=form.description.data,
            email=form.email.data,
            is_active=True
        )
        db.session.add(club)
        db.session.flush()
        
        # Create admin user
        admin = User(
            username=form.admin_username.data,
            email=form.admin_email.data,
            first_name=form.admin_first_name.data,
            last_name=form.admin_last_name.data,
            is_active=True
        )
        admin.set_password(form.admin_password.data)
        db.session.add(admin)
        db.session.flush()
        
        # Create membership
        membership = ClubMembership(
            user_id=admin.id,
            club_id=club.id,
            role='admin',
            is_active=True
        )
        db.session.add(membership)
        
        db.session.commit()
        
        # Auto-login and set club context
        login_user(admin)
        session['current_club_id'] = club.id
        
        flash(f'Club "{club.name}" created successfully! Welcome!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('clubs/register.html', form=form)
```

### Phase 3: Update Views

All blueprint views need updates:

#### Inventory Views
- Add club context check
- Filter queries by club_id
- Ensure new items get club_id

#### Events Views
- Add club context check
- Filter queries by club_id
- Ensure new events get club_id

#### Members Views
- Show only club members (via ClubMembership)
- Update role checks to use club-specific roles

#### Competitions Views
- Add club context check
- Filter queries by club_id
- Ensure competitions get club_id

### Phase 4: Update Templates

#### Base Template Updates

Add club switcher to `app/templates/base.html`:

```html
{% if current_user.is_authenticated and current_club %}
<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="clubDropdown" 
       role="button" data-bs-toggle="dropdown">
        <i class="bi bi-building"></i> {{ current_club.name }}
    </a>
    <ul class="dropdown-menu">
        {% for club in current_user.get_clubs() %}
        <li>
            <a class="dropdown-item {% if club.id == current_club.id %}active{% endif %}" 
               href="{{ url_for('auth.switch_club', club_id=club.id) }}">
                {{ club.name }}
            </a>
        </li>
        {% endfor %}
    </ul>
</li>
{% endif %}
```

### Phase 5: Testing

1. Unit tests for models
2. Integration tests for club isolation
3. E2E tests for club switching
4. Security tests for unauthorized access

## Next Steps After Implementation

1. Deploy to staging environment
2. Comprehensive QA testing
3. Documentation updates
4. Training materials for existing users
5. Migration announcement
6. Production deployment

## Rollback Plan

If issues arise:

```bash
# Rollback database
flask db downgrade

# Restore from backup if needed
# Remove multi-tenancy code changes
```

## Support

For questions or issues during implementation, refer to:
- MULTI_TENANCY_ARCHITECTURE.md for design decisions
- This file for step-by-step instructions
- Test suite for expected behavior
