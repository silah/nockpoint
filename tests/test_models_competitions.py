"""
Test Competition models functionality
"""
import unittest
from app import create_app, db
from app.models import (User, ShootingEvent, Competition, CompetitionGroup, 
                       CompetitionTeam, CompetitionRegistration, ArrowScore)
from tests.conftest import BaseTestCase
from datetime import datetime, date, time

class TestCompetitionModels(BaseTestCase):
    """Test competition-related models"""
    
    def setUp(self):
        """Set up test fixtures"""
        super().setUp()
        
        # Create test users
        self.admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True
        )
        self.admin.set_password('password')
        
        self.member1 = User(
            username='archer1',
            email='archer1@example.com',
            first_name='Alice',
            last_name='Archer',
            is_admin=False
        )
        self.member1.set_password('password')
        
        self.member2 = User(
            username='archer2',
            email='archer2@example.com',
            first_name='Bob',
            last_name='Bowman',
            is_admin=False
        )
        self.member2.set_password('password')
        
        db.session.add_all([self.admin, self.member1, self.member2])
        db.session.commit()
        
        # Create test event
        self.event = ShootingEvent(
            name='Championship 2025',
            description='Annual championship competition',
            location='Competition Range',
            date=date(2025, 12, 15),
            start_time=time(9, 0),
            duration_hours=6,
            created_by=self.admin.id
        )
        db.session.add(self.event)
        db.session.commit()
    
    def test_competition_creation(self):
        """Test creating a competition"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            target_size_cm=122,
            max_team_size=4,
            status='setup'
        )
        
        db.session.add(competition)
        db.session.commit()
        
        # Verify competition was created
        self.assertIsNotNone(competition.id)
        self.assertEqual(competition.event_id, self.event.id)
        self.assertEqual(competition.number_of_rounds, 6)
        self.assertEqual(competition.arrows_per_round, 6)
        self.assertEqual(competition.target_size_cm, 122)
        self.assertEqual(competition.max_team_size, 4)
        self.assertEqual(competition.status, 'setup')
        self.assertIsNotNone(competition.created_at)
    
    def test_competition_properties(self):
        """Test competition computed properties"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=8,
            arrows_per_round=3,
            target_size_cm=80,
            max_team_size=3,
            status='setup'
        )
        
        # Test computed properties
        self.assertEqual(competition.total_arrows, 24)  # 8 * 3
        self.assertEqual(competition.max_possible_score, 240)  # 24 * 10
    
    def test_competition_group_creation(self):
        """Test creating competition groups"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            status='setup'
        )
        db.session.add(competition)
        db.session.commit()
        
        # Create groups
        senior_group = CompetitionGroup(
            competition_id=competition.id,
            name='Senior Men',
            description='Male archers 18 and over',
            min_age=18,
            max_age=None
        )
        
        junior_group = CompetitionGroup(
            competition_id=competition.id,
            name='Junior',
            description='Archers under 18',
            min_age=None,
            max_age=17
        )
        
        db.session.add_all([senior_group, junior_group])
        db.session.commit()
        
        # Verify groups
        self.assertEqual(len(competition.groups), 2)
        self.assertEqual(senior_group.competition_id, competition.id)
        self.assertEqual(junior_group.min_age, None)
        self.assertEqual(junior_group.max_age, 17)
    
    def test_competition_team_creation(self):
        """Test creating competition teams"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            status='setup'
        )
        db.session.add(competition)
        db.session.commit()
        
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Open Class',
            description='Open to all'
        )
        db.session.add(group)
        db.session.commit()
        
        team = CompetitionTeam(
            group_id=group.id,
            name='Team Alpha',
            target_assignment='Target 1'
        )
        db.session.add(team)
        db.session.commit()
        
        # Verify team
        self.assertEqual(team.group_id, group.id)
        self.assertEqual(team.name, 'Team Alpha')
        self.assertEqual(team.target_assignment, 'Target 1')
        self.assertEqual(len(group.teams), 1)
    
    def test_competition_registration(self):
        """Test competition registration"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            status='registration_open'
        )
        db.session.add(competition)
        db.session.commit()
        
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Open Class'
        )
        db.session.add(group)
        db.session.commit()
        
        registration = CompetitionRegistration(
            competition_id=competition.id,
            member_id=self.member1.id,
            group_id=group.id
        )
        db.session.add(registration)
        db.session.commit()
        
        # Verify registration
        self.assertEqual(registration.competition_id, competition.id)
        self.assertEqual(registration.member_id, self.member1.id)
        self.assertEqual(registration.group_id, group.id)
        self.assertIsNotNone(registration.registered_at)
        
        # Test relationships
        self.assertEqual(len(competition.registrations), 1)
        self.assertEqual(competition.registrations[0].member.username, 'archer1')
    
    def test_arrow_score_creation(self):
        """Test creating arrow scores"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            status='in_progress'
        )
        db.session.add(competition)
        db.session.commit()
        
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Open Class'
        )
        db.session.add(group)
        db.session.commit()
        
        registration = CompetitionRegistration(
            competition_id=competition.id,
            member_id=self.member1.id,
            group_id=group.id
        )
        db.session.add(registration)
        db.session.commit()
        
        # Create arrow scores
        scores = [10, 9, 8, 10, 7, 9]  # First round
        for arrow_num, score in enumerate(scores, 1):
            arrow_score = ArrowScore(
                registration_id=registration.id,
                round_number=1,
                arrow_number=arrow_num,
                score=score
            )
            db.session.add(arrow_score)
        
        db.session.commit()
        
        # Verify scores
        saved_scores = ArrowScore.query.filter_by(
            registration_id=registration.id,
            round_number=1
        ).order_by(ArrowScore.arrow_number).all()
        
        self.assertEqual(len(saved_scores), 6)
        self.assertEqual([s.score for s in saved_scores], [10, 9, 8, 10, 7, 9])
        self.assertEqual(sum(s.score for s in saved_scores), 53)  # Total for round 1
    
    def test_competition_workflow(self):
        """Test complete competition workflow"""
        # 1. Create competition
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=2,
            arrows_per_round=3,
            status='setup'
        )
        db.session.add(competition)
        db.session.commit()
        
        # 2. Create groups
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Test Group'
        )
        db.session.add(group)
        db.session.commit()
        
        # 3. Open registration
        competition.status = 'registration_open'
        db.session.commit()
        
        # 4. Register participants
        reg1 = CompetitionRegistration(
            competition_id=competition.id,
            member_id=self.member1.id,
            group_id=group.id
        )
        reg2 = CompetitionRegistration(
            competition_id=competition.id,
            member_id=self.member2.id,
            group_id=group.id
        )
        db.session.add_all([reg1, reg2])
        db.session.commit()
        
        # 5. Create team
        team = CompetitionTeam(
            group_id=group.id,
            name='Test Team',
            target_assignment='Target 1'
        )
        db.session.add(team)
        db.session.commit()
        
        # 6. Assign to team
        reg1.team_id = team.id
        reg2.team_id = team.id
        db.session.commit()
        
        # 7. Start competition
        competition.status = 'in_progress'
        db.session.commit()
        
        # 8. Record scores
        for reg in [reg1, reg2]:
            for round_num in range(1, 3):  # 2 rounds
                for arrow_num in range(1, 4):  # 3 arrows per round
                    score = ArrowScore(
                        registration_id=reg.id,
                        round_number=round_num,
                        arrow_number=arrow_num,
                        score=8  # Everyone shoots 8
                    )
                    db.session.add(score)
        
        db.session.commit()
        
        # 9. Verify final state
        self.assertEqual(competition.status, 'in_progress')
        self.assertEqual(len(competition.registrations), 2)
        self.assertEqual(len(group.teams), 1)
        self.assertEqual(len(team.members), 2)
        
        # Check total scores
        total_scores = db.session.query(
            db.func.sum(ArrowScore.score)
        ).filter_by(registration_id=reg1.id).scalar()
        self.assertEqual(total_scores, 48)  # 2 rounds * 3 arrows * 8 points

if __name__ == '__main__':
    unittest.main()
