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
            status='setup',
            created_by=self.admin.id
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
            status='setup',
            created_by=self.admin.id
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
            status='setup',
            created_by=self.admin.id
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
            status='setup',
            created_by=self.admin.id
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
            team_number=1,
            target_number=1
        )
        db.session.add(team)
        db.session.commit()
        
        # Verify team
        self.assertEqual(team.group_id, group.id)
        self.assertEqual(team.team_number, 1)
        self.assertEqual(team.target_number, 1)
        self.assertEqual(len(group.teams), 1)
    
    def test_competition_registration(self):
        """Test competition registration"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            status='registration_open',
            created_by=self.admin.id
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
        self.assertIsNotNone(registration.registration_date)
        
        # Test relationships
        self.assertEqual(len(competition.registrations), 1)
        self.assertEqual(competition.registrations[0].member.username, 'archer1')
    
    def test_arrow_score_creation(self):
        """Test creating arrow scores"""
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=6,
            arrows_per_round=6,
            status='in_progress',
            created_by=self.admin.id
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
                points=score,
                recorded_by=self.admin.id
            )
            db.session.add(arrow_score)
        
        db.session.commit()
        
        # Verify scores
        saved_scores = ArrowScore.query.filter_by(
            registration_id=registration.id,
            round_number=1
        ).order_by(ArrowScore.arrow_number).all()
        
        self.assertEqual(len(saved_scores), 6)
        self.assertEqual([s.points for s in saved_scores], [10, 9, 8, 10, 7, 9])
        self.assertEqual(sum(s.points for s in saved_scores), 53)  # Total for round 1
    
    def test_competition_workflow(self):
        """Test complete competition workflow"""
        # 1. Create competition
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=2,
            arrows_per_round=3,
            status='setup',
            created_by=self.admin.id
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
            team_number=1,
            target_number=1
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
            arrow_count = 1
            for round_num in range(1, 3):  # 2 rounds
                for arrow_in_round in range(1, 4):  # 3 arrows per round
                    score = ArrowScore(
                        registration_id=reg.id,
                        round_number=round_num,
                        arrow_number=arrow_count,  # Sequential arrow number across all rounds
                        points=8,  # Everyone shoots 8
                        recorded_by=self.admin.id
                    )
                    db.session.add(score)
                    arrow_count += 1
        
        db.session.commit()
        
        # 9. Verify final state
        self.assertEqual(competition.status, 'in_progress')
        self.assertEqual(len(competition.registrations), 2)
        self.assertEqual(len(group.teams), 1)
        self.assertEqual(len(team.registrations), 2)
        
        # Check total scores
        total_scores = db.session.query(
            db.func.sum(ArrowScore.points)
        ).filter_by(registration_id=reg1.id).scalar()
        self.assertEqual(total_scores, 48)  # 2 rounds * 3 arrows * 8 points
    
    def test_competition_results_basic(self):
        """Test basic competition results functionality"""
        # Create competition
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=3,
            arrows_per_round=6,
            target_size_cm=122,
            max_team_size=1,  # Individual competition
            status='in_progress',
            created_by=self.admin.id
        )
        db.session.add(competition)
        db.session.commit()
        
        # Create group
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Adults',
            description='Adult archers',
            min_age=18,
            max_age=None
        )
        db.session.add(group)
        db.session.commit()
        
        # Create registrations
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
        
        # Add scores for member1 (better performance)
        arrow_num = 1
        for round_num in range(1, 4):  # 3 rounds
            for arrow_in_round in range(1, 7):  # 6 arrows per round
                score = ArrowScore(
                    registration_id=reg1.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=9,  # High scorer
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        # Add scores for member2 (lower performance)  
        arrow_num = 1
        for round_num in range(1, 3):  # Only 2 complete rounds
            for arrow_in_round in range(1, 7):  # 6 arrows per round
                score = ArrowScore(
                    registration_id=reg2.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=7,  # Lower scorer
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        db.session.commit()
        
        # Test get_results_by_group method
        results = competition.get_results_by_group()
        
        # Verify structure
        self.assertIsInstance(results, dict)
        self.assertIn('Adults', results)
        adult_results = results['Adults']
        
        # Should have 2 participants
        self.assertEqual(len(adult_results), 2)
        
        # Should be sorted by score (highest first)
        self.assertEqual(adult_results[0].member_id, self.member1.id)  # Higher scorer first
        self.assertEqual(adult_results[1].member_id, self.member2.id)  # Lower scorer second
        
        # Check scores
        self.assertEqual(adult_results[0].total_score, 162)  # 3 rounds * 6 arrows * 9 points
        self.assertEqual(adult_results[1].total_score, 84)   # 2 rounds * 6 arrows * 7 points
        
        # Check completion status
        self.assertEqual(adult_results[0].completed_rounds, 3)
        self.assertEqual(adult_results[1].completed_rounds, 2)
        
        self.assertTrue(adult_results[0].is_complete)  # All rounds done
        self.assertFalse(adult_results[1].is_complete)  # Missing 1 round
    
    def test_competition_results_multiple_groups(self):
        """Test competition results with multiple groups"""
        # Create competition
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=2,
            arrows_per_round=3,
            target_size_cm=80,
            max_team_size=1,
            status='in_progress',
            created_by=self.admin.id
        )
        db.session.add(competition)
        db.session.commit()
        
        # Create groups
        adults_group = CompetitionGroup(
            competition_id=competition.id,
            name='Adults',
            description='Adult archers',
            min_age=18
        )
        juniors_group = CompetitionGroup(
            competition_id=competition.id,
            name='Juniors',
            description='Junior archers',
            max_age=17
        )
        db.session.add_all([adults_group, juniors_group])
        db.session.commit()
        
        # Create a third member for juniors
        junior_member = User(
            username='junior',
            email='junior@example.com',
            first_name='Junior',
            last_name='Archer',
            is_admin=False
        )
        junior_member.set_password('password')
        db.session.add(junior_member)
        db.session.commit()
        
        # Create registrations
        adult_reg = CompetitionRegistration(
            competition_id=competition.id,
            member_id=self.member1.id,
            group_id=adults_group.id
        )
        junior_reg = CompetitionRegistration(
            competition_id=competition.id,
            member_id=junior_member.id,
            group_id=juniors_group.id
        )
        db.session.add_all([adult_reg, junior_reg])
        db.session.commit()
        
        # Add scores
        # Adult: 2 complete rounds
        arrow_num = 1
        for round_num in range(1, 3):
            for arrow_in_round in range(1, 4):
                score = ArrowScore(
                    registration_id=adult_reg.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=8,
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        # Junior: 1 complete round
        arrow_num = 1
        for round_num in range(1, 2):
            for arrow_in_round in range(1, 4):
                score = ArrowScore(
                    registration_id=junior_reg.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=9,
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        db.session.commit()
        
        # Test results by group
        results = competition.get_results_by_group()
        
        # Should have both groups
        self.assertIn('Adults', results)
        self.assertIn('Juniors', results)
        
        # Each group should have one participant
        self.assertEqual(len(results['Adults']), 1)
        self.assertEqual(len(results['Juniors']), 1)
        
        # Check scores
        adult_result = results['Adults'][0]
        junior_result = results['Juniors'][0]
        
        self.assertEqual(adult_result.total_score, 48)  # 2*3*8
        self.assertEqual(junior_result.total_score, 27)  # 1*3*9
        
        self.assertEqual(adult_result.completed_rounds, 2)
        self.assertEqual(junior_result.completed_rounds, 1)
    
    def test_competition_results_empty(self):
        """Test competition results with no participants"""
        # Create competition with no registrations
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=3,
            arrows_per_round=6,
            status='setup',
            created_by=self.admin.id
        )
        db.session.add(competition)
        db.session.commit()
        
        # Test empty results
        results = competition.get_results_by_group()
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 0)
    
    def test_competition_results_no_scores(self):
        """Test competition results with registrations but no scores"""
        # Create competition
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=3,
            arrows_per_round=6,
            status='setup',
            created_by=self.admin.id
        )
        db.session.add(competition)
        db.session.commit()
        
        # Create group and registration
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Adults',
            description='Adult archers'
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
        
        # Test results with no scores
        results = competition.get_results_by_group()
        
        self.assertIn('Adults', results)
        adult_results = results['Adults']
        self.assertEqual(len(adult_results), 1)
        
        # Should have zero scores and rounds
        result = adult_results[0]
        self.assertEqual(result.total_score, 0)
        self.assertEqual(result.completed_rounds, 0)
        self.assertFalse(result.is_complete)
    
    def test_competition_registration_properties(self):
        """Test CompetitionRegistration calculated properties"""
        # Create competition
        competition = Competition(
            event_id=self.event.id,
            number_of_rounds=4,
            arrows_per_round=6,
            status='in_progress',
            created_by=self.admin.id
        )
        db.session.add(competition)
        db.session.commit()
        
        # Create group and registration
        group = CompetitionGroup(
            competition_id=competition.id,
            name='Test Group'
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
        
        # Add partial scores (3 complete rounds out of 4)
        arrow_num = 1
        for round_num in range(1, 4):  # Rounds 1-3 only
            for arrow_in_round in range(1, 7):  # 6 arrows
                score = ArrowScore(
                    registration_id=registration.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=7,
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        db.session.commit()
        
        # Test calculated properties
        self.assertEqual(registration.total_score, 126)  # 3*6*7
        self.assertEqual(registration.completed_rounds, 3)
        self.assertFalse(registration.is_complete)  # Missing round 4
        
        # Add final round
        for arrow_in_round in range(1, 7):
            score = ArrowScore(
                registration_id=registration.id,
                round_number=4,
                arrow_number=arrow_num,
                points=8,
                recorded_by=self.admin.id
            )
            db.session.add(score)
            arrow_num += 1
        
        db.session.commit()
        
        # Now should be complete
        self.assertEqual(registration.total_score, 174)  # 126 + 6*8
        self.assertEqual(registration.completed_rounds, 4)
        self.assertTrue(registration.is_complete)

if __name__ == '__main__':
    unittest.main()
