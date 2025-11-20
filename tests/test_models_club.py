"""
Tests for Club and ClubMembership models.
Tests multi-tenancy core functionality.
"""
import pytest
from datetime import datetime, timedelta
from app.models import Club, ClubMembership, User


class TestClubModel:
    """Test the Club model."""
    
    def test_create_club(self, _db):
        """Test creating a basic club."""
        club = Club(
            name='Test Club',
            slug='test-club',
            email='test@example.com'
        )
        _db.session.add(club)
        _db.session.commit()
        
        assert club.id is not None
        assert club.name == 'Test Club'
        assert club.slug == 'test-club'
        assert club.email == 'test@example.com'
        assert club.created_at is not None
    
    def test_club_slug_unique(self, _db, club_alpha):
        """Test that club slugs must be unique."""
        duplicate_club = Club(
            name='Another Club',
            slug='alpha-archery',  # Same slug as club_alpha
            email='other@example.com'
        )
        _db.session.add(duplicate_club)
        
        with pytest.raises(Exception):  # IntegrityError
            _db.session.commit()
    
    def test_club_repr(self, club_alpha):
        """Test club string representation."""
        assert 'Alpha Archery' in repr(club_alpha)
    
    def test_club_members_relationship(self, _db, club_alpha, admin_alpha, member_alpha):
        """Test club can access its members."""
        memberships = ClubMembership.query.filter_by(club_id=club_alpha.id).all()
        assert len(memberships) == 2
        user_ids = [m.user_id for m in memberships]
        assert admin_alpha.id in user_ids
        assert member_alpha.id in user_ids
    
    def test_club_default_values(self, _db):
        """Test club default values."""
        club = Club(
            name='Minimal Club',
            slug='minimal',
            email='minimal@example.com'
        )
        _db.session.add(club)
        _db.session.commit()
        
        assert club.is_active is True
        assert club.is_pro_enabled is False
        assert club.pro_expires_at is None
    
    def test_club_pro_status(self, _db):
        """Test Pro subscription status checking."""
        club = Club(
            name='Pro Club',
            slug='pro-club',
            email='pro@example.com',
            is_pro_enabled=True,
            pro_expires_at=datetime.utcnow() + timedelta(days=30)
        )
        _db.session.add(club)
        _db.session.commit()
        
        assert club.is_pro_active() is True
    
    def test_club_pro_expired(self, _db):
        """Test expired Pro subscription."""
        club = Club(
            name='Expired Pro Club',
            slug='expired-pro',
            email='expired@example.com',
            is_pro_enabled=True,
            pro_expires_at=datetime.utcnow() - timedelta(days=1)
        )
        _db.session.add(club)
        _db.session.commit()
        
        assert club.is_pro_active() is False
    
    def test_club_not_pro(self, club_alpha):
        """Test non-Pro club."""
        assert club_alpha.is_pro_active() is False


class TestClubMembershipModel:
    """Test the ClubMembership junction model."""
    
    def test_create_membership(self, _db, club_alpha):
        """Test creating a club membership."""
        user = User(
            email='newmember@example.com',
            username='newmember',
            first_name='New',
            last_name='Member'
        )
        user.set_password('password')
        _db.session.add(user)
        _db.session.flush()
        
        membership = ClubMembership(
            user_id=user.id,
            club_id=club_alpha.id,
            role='member',
            is_active=True
        )
        _db.session.add(membership)
        _db.session.commit()
        
        assert membership.id is not None
        assert membership.user_id == user.id
        assert membership.club_id == club_alpha.id
        assert membership.role == 'member'
        assert membership.is_active == True
    
    def test_membership_roles(self, admin_alpha, member_alpha, club_alpha):
        """Test different membership roles."""
        admin_membership = ClubMembership.query.filter_by(
            user_id=admin_alpha.id,
            club_id=club_alpha.id
        ).first()
        
        member_membership = ClubMembership.query.filter_by(
            user_id=member_alpha.id,
            club_id=club_alpha.id
        ).first()
        
        assert admin_membership.role == 'admin'
        assert member_membership.role == 'member'
    
    def test_membership_status(self, _db, club_alpha):
        """Test membership status transitions."""
        user = User(
            email='pending@example.com',
            username='pending',
            first_name='Pending',
            last_name='User'
        )
        user.set_password('password')
        _db.session.add(user)
        _db.session.flush()
        
        # Create pending membership (inactive)
        membership = ClubMembership(
            user_id=user.id,
            club_id=club_alpha.id,
            role='member',
            is_active=False
        )
        _db.session.add(membership)
        _db.session.commit()
        
        assert membership.is_active == False
        
        # Activate membership
        membership.is_active = True
        _db.session.commit()
        
        assert membership.is_active == True
    
    def test_user_relationship(self, admin_alpha, club_alpha):
        """Test membership to user relationship."""
        membership = ClubMembership.query.filter_by(
            user_id=admin_alpha.id,
            club_id=club_alpha.id
        ).first()
        
        assert membership.user is not None
        assert membership.user.id == admin_alpha.id
        assert membership.user.email == 'admin.alpha@example.com'
    
    def test_club_relationship(self, admin_alpha, club_alpha):
        """Test membership to club relationship."""
        membership = ClubMembership.query.filter_by(
            user_id=admin_alpha.id,
            club_id=club_alpha.id
        ).first()
        
        assert membership.club is not None
        assert membership.club.id == club_alpha.id
        assert membership.club.name == 'Alpha Archery'
    
    def test_unique_user_club_constraint(self, _db, admin_alpha, club_alpha):
        """Test that a user can't have duplicate memberships in same club."""
        duplicate_membership = ClubMembership(
            user_id=admin_alpha.id,
            club_id=club_alpha.id,
            role='member',
            is_active=True
        )
        _db.session.add(duplicate_membership)
        
        with pytest.raises(Exception):  # IntegrityError
            _db.session.commit()
    
    def test_membership_repr(self, admin_alpha, club_alpha):
        """Test membership string representation."""
        membership = ClubMembership.query.filter_by(
            user_id=admin_alpha.id,
            club_id=club_alpha.id
        ).first()
        
        repr_str = repr(membership)
        # Just check that repr contains the user_id and club_id
        assert str(admin_alpha.id) in repr_str
        assert str(club_alpha.id) in repr_str

class TestMultiClubScenarios:
    """Test scenarios involving multiple clubs."""
    
    def test_user_multiple_clubs(self, multi_club_user, club_alpha, club_beta):
        """Test user membership in multiple clubs."""
        clubs = multi_club_user.get_clubs()
        assert len(clubs) == 2
        club_ids = [c.id for c in clubs]
        assert club_alpha.id in club_ids
        assert club_beta.id in club_ids
    
    def test_club_isolation(self, _db, club_alpha, club_beta, admin_alpha, admin_beta):
        """Test that clubs have separate member lists."""
        alpha_members = ClubMembership.query.filter_by(club_id=club_alpha.id).all()
        beta_members = ClubMembership.query.filter_by(club_id=club_beta.id).all()
        
        # Should have members in both clubs
        assert len(alpha_members) > 0
        assert len(beta_members) > 0
        
        # Get user IDs
        alpha_user_ids = [m.user_id for m in alpha_members]
        beta_user_ids = [m.user_id for m in beta_members]
        
        # Should have different members
        assert alpha_user_ids != beta_user_ids
    
    def test_user_different_roles_different_clubs(self, multi_club_user, club_alpha, club_beta):
        """Test user can have different roles in different clubs."""
        assert multi_club_user.is_member_of_club(club_alpha.id)
        assert multi_club_user.is_member_of_club(club_beta.id)
        
        assert not multi_club_user.is_admin_of_club(club_alpha.id)
        assert multi_club_user.is_admin_of_club(club_beta.id)
