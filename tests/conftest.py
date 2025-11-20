"""
Pytest configuration and fixtures for Nockpoint tests.
Provides comprehensive fixtures for multi-tenancy testing.
"""
import os
import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (User, Club, ClubMembership, InventoryCategory, InventoryItem, 
                        ShootingEvent, Competition, ClubSettings, BeginnersStudent,
                        EventAttendance, MemberCharge, CompetitionRegistration, 
                        CompetitionGroup, CompetitionTeam, ArrowScore)
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create and configure a test app instance."""
    # Set test configuration before creating app
    os.environ['TESTING'] = 'True'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'SERVER_NAME': 'localhost.localdomain'
    })
    
    # Create tables
    with app.app_context():
        db.drop_all()  # Ensure clean start
        db.create_all()
    
    yield app
    
    # Cleanup
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def _db(app):
    """Provide a clean database for each test."""
    with app.app_context():
        # Recreate all tables for each test for complete isolation
        db.create_all()
        
        yield db
        
        # Drop all tables after test
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def club_alpha(_db):
    """Create a test club 'Alpha Archery'."""
    club = Club(
        name='Alpha Archery',
        slug='alpha-archery',
        description='First test club',
        email='alpha@example.com',
        phone='555-0001',
        address='123 Alpha St, Alpha City, AC 12345',
        website_url='https://alpha.example.com',
        default_location='Alpha Range'
    )
    _db.session.add(club)
    _db.session.flush()
    return club


@pytest.fixture
def club_beta(_db):
    """Create a test club 'Beta Bowmen'."""
    club = Club(
        name='Beta Bowmen',
        slug='beta-bowmen',
        description='Second test club',
        email='beta@example.com',
        phone='555-0002',
        address='456 Beta Ave, Beta City, BC 67890',
        website_url='https://beta.example.com',
        default_location='Beta Range'
    )
    _db.session.add(club)
    _db.session.flush()
    return club


@pytest.fixture
def admin_alpha(_db, club_alpha):
    """Create an admin user for club Alpha."""
    user = User(
        email='admin.alpha@example.com',
        username='admin_alpha',
        first_name='Alice',
        last_name='Admin',
        is_admin=False  # Club admin, not global admin
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.flush()
    
    # Add club membership
    membership = ClubMembership(
        user_id=user.id,
        club_id=club_alpha.id,
        role='admin',
        is_active=True
    )
    _db.session.add(membership)
    _db.session.flush()
    return user


@pytest.fixture
def admin_beta(_db, club_beta):
    """Create an admin user for club Beta."""
    user = User(
        email='admin.beta@example.com',
        username='admin_beta',
        first_name='Bob',
        last_name='Boss',
        is_admin=False
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.flush()
    
    membership = ClubMembership(
        user_id=user.id,
        club_id=club_beta.id,
        role='admin',
        is_active=True
    )
    _db.session.add(membership)
    _db.session.flush()
    return user


@pytest.fixture
def member_alpha(_db, club_alpha):
    """Create a regular member for club Alpha."""
    user = User(
        email='member.alpha@example.com',
        username='member_alpha',
        first_name='Charlie',
        last_name='Member',
        is_admin=False
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.flush()
    
    membership = ClubMembership(
        user_id=user.id,
        club_id=club_alpha.id,
        role='member',
        is_active=True
    )
    _db.session.add(membership)
    _db.session.flush()
    return user


@pytest.fixture
def member_beta(_db, club_beta):
    """Create a regular member for club Beta."""
    user = User(
        email='member.beta@example.com',
        username='member_beta',
        first_name='Dana',
        last_name='Doe',
        is_admin=False
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.flush()
    
    membership = ClubMembership(
        user_id=user.id,
        club_id=club_beta.id,
        role='member',
        is_active=True
    )
    _db.session.add(membership)
    _db.session.flush()
    return user


@pytest.fixture
def multi_club_user(_db, club_alpha, club_beta):
    """Create a user who is a member of multiple clubs."""
    user = User(
        email='multi@example.com',
        username='multi_user',
        first_name='Emma',
        last_name='Everywhere',
        is_admin=False
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.flush()
    
    # Member of Alpha
    membership1 = ClubMembership(
        user_id=user.id,
        club_id=club_alpha.id,
        role='member',
        is_active=True
    )
    _db.session.add(membership1)
    
    # Admin of Beta
    membership2 = ClubMembership(
        user_id=user.id,
        club_id=club_beta.id,
        role='admin',
        is_active=True
    )
    _db.session.add(membership2)
    _db.session.flush()
    return user


@pytest.fixture
def global_admin(_db):
    """Create a global admin user (not tied to specific clubs)."""
    user = User(
        email='global.admin@example.com',
        username='global_admin',
        first_name='Global',
        last_name='Admin',
        is_admin=True
    )
    user.set_password('password123')
    _db.session.add(user)
    _db.session.flush()
    return user


@pytest.fixture
def inventory_alpha(_db, club_alpha):
    """Create inventory items for club Alpha."""
    category = InventoryCategory(
        name='Bows',
        description='Recurve bows',
        club_id=club_alpha.id
    )
    _db.session.add(category)
    _db.session.flush()
    
    item1 = InventoryItem(
        name='Recurve Bow 25#',
        category_id=category.id,
        club_id=club_alpha.id,
        quantity=5,
        unit='piece',
        condition='good',
        location='Storage Room A'
    )
    item2 = InventoryItem(
        name='Recurve Bow 30#',
        category_id=category.id,
        club_id=club_alpha.id,
        quantity=3,
        unit='piece',
        condition='excellent',
        location='Storage Room A'
    )
    _db.session.add_all([item1, item2])
    _db.session.flush()
    return {'category': category, 'items': [item1, item2]}


@pytest.fixture
def inventory_beta(_db, club_beta):
    """Create inventory items for club Beta."""
    category = InventoryCategory(
        name='Arrows',
        description='Carbon arrows',
        club_id=club_beta.id
    )
    _db.session.add(category)
    _db.session.flush()
    
    item = InventoryItem(
        name='Carbon Arrow 500',
        category_id=category.id,
        club_id=club_beta.id,
        quantity=50,
        unit='piece',
        condition='good',
        location='Arrow Rack'
    )
    _db.session.add(item)
    _db.session.flush()
    return {'category': category, 'items': [item]}


@pytest.fixture
def event_alpha(_db, club_alpha, admin_alpha):
    """Create a shooting event for club Alpha."""
    from datetime import date, time
    event = ShootingEvent(
        name='Alpha Weekly Practice',
        event_type='regular',
        date=date.today() + timedelta(days=1),
        start_time=time(10, 0),
        duration_hours=2,
        location='Alpha Range',
        max_participants=20,
        club_id=club_alpha.id,
        created_by=admin_alpha.id
    )
    _db.session.add(event)
    _db.session.flush()
    return event


@pytest.fixture
def event_beta(_db, club_beta, admin_beta):
    """Create a shooting event for club Beta."""
    from datetime import date, time
    event = ShootingEvent(
        name='Beta Open Shoot',
        event_type='regular',
        date=date.today() + timedelta(days=2),
        start_time=time(14, 0),
        duration_hours=3,
        location='Beta Field',
        max_participants=30,
        club_id=club_beta.id,
        created_by=admin_beta.id
    )
    _db.session.add(event)
    _db.session.flush()
    return event


@pytest.fixture
def competition_alpha(_db, club_alpha, admin_alpha):
    """Create a competition for club Alpha."""
    from datetime import date, time
    # First create an event for the competition
    event = ShootingEvent(
        name='Alpha Spring Tournament',
        description='Spring championship',
        event_type='regular',
        date=date.today() + timedelta(days=30),
        start_time=time(9, 0),
        duration_hours=6,
        location='Alpha Range',
        club_id=club_alpha.id,
        created_by=admin_alpha.id
    )
    _db.session.add(event)
    _db.session.flush()
    
    # Now create the competition linked to the event
    comp = Competition(
        club_id=club_alpha.id,
        event_id=event.id,
        number_of_rounds=6,
        target_size_cm=122,
        arrows_per_round=6,
        max_team_size=4,
        created_by=admin_alpha.id
    )
    _db.session.add(comp)
    _db.session.flush()
    return comp


@pytest.fixture
def authenticated_client(client, app):
    """
    Create a client with an authenticated session.
    Usage: authenticated_client(user, club_id)
    """
    def _authenticate(user, club_id=None):
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            if club_id:
                sess['current_club_id'] = club_id
        return client
    return _authenticate


@pytest.fixture
def runner(app):
    """Create a CLI test runner."""
    return app.test_cli_runner()
