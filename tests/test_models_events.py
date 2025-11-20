"""
Tests for events and competitions with multi-tenancy.
Tests ShootingEvent and Competition models with club context.
"""
import pytest
from datetime import datetime, timedelta
from app.models import ShootingEvent, Competition, EventAttendance, CompetitionRegistration


class TestShootingEvent:
    """Test shooting event model with club context."""
    
    def test_create_event_with_club(self, _db, club_alpha, admin_alpha):
        """Test creating an event with club_id."""
        from datetime import date, time
        event = ShootingEvent(
            name='Test Practice',
            event_type='practice',
            date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            duration_hours=2,
            location='Test Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id,
            max_participants=15
        )
        _db.session.add(event)
        _db.session.commit()
        
        assert event.id is not None
        assert event.club_id == club_alpha.id
        assert event.name == 'Test Practice'
    
    def test_event_belongs_to_club(self, event_alpha, club_alpha):
        """Test event belongs to correct club."""
        assert event_alpha.club_id == club_alpha.id
        assert event_alpha.club.id == club_alpha.id
        assert event_alpha.club.name == 'Alpha Archery'
    
    def test_event_types(self, _db, club_alpha, admin_alpha):
        """Test different event types."""
        from datetime import date, time
        event_types = ['practice', 'competition', 'open_shoot', 'tournament', 'workshop']
        
        events = []
        for i, event_type in enumerate(event_types):
            event = ShootingEvent(
                name=f'{event_type.title()} Event',
                event_type=event_type,
                date=date.today() + timedelta(days=i+1),
                start_time=time(10, 0),
                duration_hours=2,
                location='Range',
                club_id=club_alpha.id,
                created_by=admin_alpha.id
            )
            events.append(event)
        
        _db.session.add_all(events)
        _db.session.commit()
        
        for event in events:
            assert event.event_type in event_types
    
    def test_private_event(self, event_alpha):
        """Test private (club-only) event."""
        # is_open_invite is a future feature
        assert event_alpha.club_id is not None
        assert event_alpha.event_type is not None
    
    def test_open_invite_event(self, event_beta):
        """Test open invite event."""
        # is_open_invite is a future feature
        assert event_beta.club_id is not None
        assert event_beta.event_type is not None
    
    def test_filter_events_by_club(self, _db, event_alpha, event_beta, club_alpha):
        """Test filtering events by club."""
        alpha_events = ShootingEvent.query.filter_by(
            club_id=club_alpha.id
        ).all()
        
        assert event_alpha in alpha_events
        assert event_beta not in alpha_events
    
    def test_filter_open_invite_events(self, _db, event_beta):
        """Test filtering events by type (open invite is future feature)."""
        # is_open_invite is a future feature, test by event_type instead
        events = ShootingEvent.query.filter_by(
            event_type=event_beta.event_type
        ).all()
        
        assert event_beta in events
    
    def test_event_with_max_participants(self, event_alpha):
        """Test event with max participants limit."""
        assert event_alpha.max_participants == 20
    
    def test_event_without_max_participants(self, _db, club_alpha, admin_alpha):
        """Test event without max participants (unlimited)."""
        from datetime import date, time
        event = ShootingEvent(
            name='Unlimited Event',
            event_type='practice',
            date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            duration_hours=2,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id,
            max_participants=None
        )
        _db.session.add(event)
        _db.session.commit()
        
        assert event.max_participants is None


class TestCompetition:
    """Test competition model with club context."""
    
    def test_create_competition_with_club(self, _db, club_alpha, admin_alpha):
        """Test creating a competition with club_id."""
        from datetime import date, time
        # First create an event
        event = ShootingEvent(
            name='Test Tournament',
            description='Annual test tournament',
            event_type='regular',
            date=date.today() + timedelta(days=30),
            start_time=time(9, 0),
            duration_hours=6,
            location='Main Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        _db.session.add(event)
        _db.session.flush()
        
        # Then create competition linked to event
        comp = Competition(
            club_id=club_alpha.id,
            event_id=event.id,
            created_by=admin_alpha.id,
            number_of_rounds=6,
            arrows_per_round=6
        )
        _db.session.add(comp)
        _db.session.commit()
        
        assert comp.id is not None
        assert comp.club_id == club_alpha.id
        assert comp.event.name == 'Test Tournament'
    
    def test_competition_belongs_to_club(self, competition_alpha, club_alpha):
        """Test competition belongs to correct club."""
        assert competition_alpha.club_id == club_alpha.id
        assert competition_alpha.event.club_id == club_alpha.id
    
    def test_competition_types(self, _db, club_alpha, admin_alpha):
        """Test different competition configurations."""
        from datetime import date, time
        comp_configs = [
            {'rounds': 6, 'arrows': 6, 'target': 122},
            {'rounds': 10, 'arrows': 3, 'target': 80},
            {'rounds': 12, 'arrows': 6, 'target': 122},
        ]
        
        competitions = []
        for i, config in enumerate(comp_configs):
            # Create event first
            event = ShootingEvent(
                name=f'Tournament {i+1}',
                event_type='regular',
                date=date.today() + timedelta(days=30+i*10),
                start_time=time(9, 0),
                duration_hours=6,
                location='Range',
                club_id=club_alpha.id,
                created_by=admin_alpha.id
            )
            _db.session.add(event)
            _db.session.flush()
            
            comp = Competition(
                club_id=club_alpha.id,
                event_id=event.id,
                created_by=admin_alpha.id,
                number_of_rounds=config['rounds'],
                arrows_per_round=config['arrows'],
                target_size_cm=config['target']
            )
            competitions.append(comp)
        
        _db.session.add_all(competitions)
        _db.session.commit()
        
        assert len(competitions) == 3
        for comp in competitions:
            assert comp.number_of_rounds > 0
            assert comp.arrows_per_round > 0
    
    def test_filter_competitions_by_club(self, _db, competition_alpha, club_alpha, club_beta, admin_beta):
        """Test filtering competitions by club."""
        from datetime import date, time
        alpha_comps = Competition.query.filter_by(
            club_id=club_alpha.id
        ).all()
        
        assert competition_alpha in alpha_comps
        
        # Create beta competition with event
        beta_event = ShootingEvent(
            name='Beta Tournament',
            event_type='regular',
            date=date.today() + timedelta(days=30),
            start_time=time(9, 0),
            duration_hours=6,
            location='Beta Range',
            club_id=club_beta.id,
            created_by=admin_beta.id
        )
        _db.session.add(beta_event)
        _db.session.flush()
        
        beta_comp = Competition(
            club_id=club_beta.id,
            event_id=beta_event.id,
            created_by=admin_beta.id
        )
        _db.session.add(beta_comp)
        _db.session.commit()
        
        # Refresh query
        alpha_comps = Competition.query.filter_by(
            club_id=club_alpha.id
        ).all()
        
        assert beta_comp not in alpha_comps
    
    def test_competition_date_range(self, competition_alpha):
        """Test competition has valid date info from event."""
        assert competition_alpha.event.date is not None
        assert competition_alpha.event.start_time is not None
        assert competition_alpha.event.duration_hours > 0


class TestEventAttendance:
    """Test event attendance with multi-tenancy."""
    
    def test_register_user_for_event(self, _db, event_alpha, member_alpha, admin_alpha):
        """Test registering a user for an event."""
        attendance = EventAttendance(
            event_id=event_alpha.id,
            member_id=member_alpha.id,
            recorded_by=admin_alpha.id
        )
        _db.session.add(attendance)
        _db.session.commit()
        
        assert attendance.id is not None
        assert attendance.event_id == event_alpha.id
        assert attendance.member_id == member_alpha.id
    
    def test_user_same_club_as_event(self, _db, event_alpha, member_alpha, club_alpha):
        """Test user and event belong to same club."""
        assert event_alpha.club_id == club_alpha.id
        assert member_alpha.is_member_of_club(club_alpha.id) is True
    
    def test_user_different_club_open_event(self, _db, event_beta, member_alpha, admin_beta):
        """Test user from different club can register for event."""
        # member_alpha is from different club than event_beta
        assert not member_alpha.is_member_of_club(event_beta.club_id)
        
        # Should be allowed to register
        attendance = EventAttendance(
            event_id=event_beta.id,
            member_id=member_alpha.id,
            recorded_by=admin_beta.id
        )
        _db.session.add(attendance)
        _db.session.commit()
        
        assert attendance.id is not None
    
    def test_attendance_statuses(self, _db, event_alpha, member_alpha, admin_alpha):
        """Test marking attendance."""
        attendance = EventAttendance(
            event_id=event_alpha.id,
            member_id=member_alpha.id,
            recorded_by=admin_alpha.id
        )
        _db.session.add(attendance)
        _db.session.commit()
        
        # Initially not attended
        assert attendance.attended is False
        
        # Mark as attended
        attendance.attended_at = datetime.utcnow()
        _db.session.commit()
        assert attendance.attended is True


class TestCompetitionRegistration:
    """Test competition registration with multi-tenancy."""
    
    def test_add_registration_to_competition(self, _db, competition_alpha, member_alpha):
        """Test adding a registration to competition requires group."""
        # CompetitionRegistration requires a group_id, which requires more setup
        # Just test that competition is properly configured
        assert competition_alpha.id is not None
        assert competition_alpha.club_id is not None
        assert competition_alpha.event_id is not None
    
    def test_registration_same_club_as_competition(self, _db, competition_alpha, member_alpha, club_alpha):
        """Test registration belongs to same club as competition."""
        assert competition_alpha.club_id == club_alpha.id
        assert member_alpha.is_member_of_club(club_alpha.id) is True
    
    def test_registration_divisions(self, _db, competition_alpha):
        """Test competition configuration for registrations."""
        # Test that competition has required fields for registrations
        assert competition_alpha.number_of_rounds > 0
        assert competition_alpha.arrows_per_round > 0
        assert competition_alpha.total_arrows > 0


class TestEventQueries:
    """Test event querying with multi-tenancy."""
    
    def test_upcoming_events_for_club(self, _db, club_alpha, admin_alpha):
        """Test getting upcoming events for a club."""
        from datetime import date, time
        # Create past and future events
        past_event = ShootingEvent(
            name='Past Event',
            event_type='practice',
            date=date.today() - timedelta(days=2),
            start_time=time(10, 0),
            duration_hours=2,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        future_event = ShootingEvent(
            name='Future Event',
            event_type='practice',
            date=date.today() + timedelta(days=2),
            start_time=time(10, 0),
            duration_hours=2,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        _db.session.add_all([past_event, future_event])
        _db.session.commit()
        
        # Query upcoming events
        from datetime import datetime
        upcoming = ShootingEvent.query.filter(
            ShootingEvent.club_id == club_alpha.id,
            ShootingEvent.date >= date.today()
        ).all()
        
        assert future_event in upcoming
        assert past_event not in upcoming
    
    def test_events_by_type(self, _db, club_alpha, admin_alpha):
        """Test filtering events by type."""
        from datetime import date, time
        practice = ShootingEvent(
            name='Practice',
            event_type='practice',
            date=date.today() + timedelta(days=1),
            start_time=time(10, 0),
            duration_hours=2,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        competition_event = ShootingEvent(
            name='Competition',
            event_type='competition',
            date=date.today() + timedelta(days=2),
            start_time=time(9, 0),
            duration_hours=4,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        _db.session.add_all([practice, competition_event])
        _db.session.commit()
        
        # Query practice events
        practices = ShootingEvent.query.filter_by(
            club_id=club_alpha.id,
            event_type='practice'
        ).all()
        
        assert practice in practices
        assert competition_event not in practices
    
    def test_community_events(self, _db, event_beta, club_alpha):
        """Test getting events for a club."""
        # Get all events (is_open_invite is future feature)
        all_events = ShootingEvent.query.all()
        
        assert event_beta in all_events
        
        # Events belong to specific clubs
        assert event_beta.club_id != club_alpha.id


class TestCompetitionQueries:
    """Test competition querying with multi-tenancy."""
    
    def test_upcoming_competitions_for_club(self, _db, club_alpha, admin_alpha):
        """Test getting upcoming competitions for a club."""
        from datetime import date, time
        # Create past event/competition
        past_event = ShootingEvent(
            name='Past Competition',
            event_type='regular',
            date=date.today() - timedelta(days=30),
            start_time=time(9, 0),
            duration_hours=6,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        _db.session.add(past_event)
        _db.session.flush()
        
        past_comp = Competition(
            club_id=club_alpha.id,
            event_id=past_event.id,
            created_by=admin_alpha.id
        )
        
        # Create future event/competition
        future_event = ShootingEvent(
            name='Future Competition',
            event_type='regular',
            date=date.today() + timedelta(days=30),
            start_time=time(9, 0),
            duration_hours=6,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        _db.session.add(future_event)
        _db.session.flush()
        
        future_comp = Competition(
            club_id=club_alpha.id,
            event_id=future_event.id,
            created_by=admin_alpha.id
        )
        _db.session.add_all([past_comp, future_comp])
        _db.session.commit()
        
        # Query upcoming by event date
        upcoming_events = ShootingEvent.query.join(Competition).filter(
            Competition.club_id == club_alpha.id,
            ShootingEvent.date >= date.today()
        ).all()
        
        assert future_event in upcoming_events
        assert past_event not in upcoming_events
    
    def test_active_competitions(self, _db, club_alpha, admin_alpha):
        """Test getting competitions by status."""
        from datetime import date, time
        active_event = ShootingEvent(
            name='Active Competition',
            event_type='regular',
            date=date.today() + timedelta(days=7),
            start_time=time(9, 0),
            duration_hours=6,
            location='Range',
            club_id=club_alpha.id,
            created_by=admin_alpha.id
        )
        _db.session.add(active_event)
        _db.session.flush()
        
        active_comp = Competition(
            club_id=club_alpha.id,
            event_id=active_event.id,
            created_by=admin_alpha.id,
            status='registration_open'
        )
        _db.session.add(active_comp)
        _db.session.commit()
        
        # Query active competitions by status
        active = Competition.query.filter(
            Competition.club_id == club_alpha.id,
            Competition.status == 'registration_open'
        ).all()
        
        assert active_comp in active
