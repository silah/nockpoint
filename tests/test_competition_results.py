"""
Test Competition Results functionality and routes
"""
import unittest
from app import create_app, db
from app.models import (User, ShootingEvent, Competition, CompetitionGroup, 
                       CompetitionTeam, CompetitionRegistration, ArrowScore, EventAttendance)
from tests.conftest import BaseTestCase
from datetime import datetime, date, time
import json

class TestCompetitionResults(BaseTestCase):
    """Test competition results routes and functionality"""
    
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
        
        self.member3 = User(
            username='archer3',
            email='archer3@example.com',
            first_name='Charlie',
            last_name='Champion',
            is_admin=False
        )
        self.member3.set_password('password')
        
        db.session.add_all([self.admin, self.member1, self.member2, self.member3])
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
        
        # Create competition with complete setup
        self.competition = Competition(
            event_id=self.event.id,
            number_of_rounds=3,
            arrows_per_round=6,
            target_size_cm=122,
            max_team_size=1,
            status='in_progress',
            created_by=self.admin.id
        )
        db.session.add(self.competition)
        db.session.commit()
        
        # Create groups
        self.adults_group = CompetitionGroup(
            competition_id=self.competition.id,
            name='Adults',
            description='Adult archers 18+',
            min_age=18
        )
        self.juniors_group = CompetitionGroup(
            competition_id=self.competition.id,
            name='Juniors',
            description='Junior archers under 18',
            max_age=17
        )
        db.session.add_all([self.adults_group, self.juniors_group])
        db.session.commit()
        
        # Create registrations
        self.reg1 = CompetitionRegistration(
            competition_id=self.competition.id,
            member_id=self.member1.id,
            group_id=self.adults_group.id
        )
        self.reg2 = CompetitionRegistration(
            competition_id=self.competition.id,
            member_id=self.member2.id,
            group_id=self.adults_group.id
        )
        self.reg3 = CompetitionRegistration(
            competition_id=self.competition.id,
            member_id=self.member3.id,
            group_id=self.juniors_group.id
        )
        db.session.add_all([self.reg1, self.reg2, self.reg3])
        db.session.commit()
    
    def login_admin(self):
        """Helper to log in admin user"""
        return self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'password'
        }, follow_redirects=True)
    
    def login_member(self, username='archer1'):
        """Helper to log in member user"""
        return self.client.post('/auth/login', data={
            'username': username,
            'password': 'password'
        }, follow_redirects=True)
    
    def add_test_scores(self):
        """Helper to add test scores for competitions"""
        # Alice (member1) - High scorer, all rounds complete
        arrow_num = 1
        for round_num in range(1, 4):  # 3 rounds
            for arrow_in_round in range(1, 7):  # 6 arrows per round
                score = ArrowScore(
                    registration_id=self.reg1.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=9,  # High performance
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        # Bob (member2) - Medium scorer, 2 rounds complete
        arrow_num = 1
        for round_num in range(1, 3):  # Only 2 rounds
            for arrow_in_round in range(1, 7):  # 6 arrows per round
                score = ArrowScore(
                    registration_id=self.reg2.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=7,  # Medium performance
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        # Charlie (member3) - Junior, 1 round complete
        arrow_num = 1
        for round_num in range(1, 2):  # Only 1 round
            for arrow_in_round in range(1, 7):  # 6 arrows per round
                score = ArrowScore(
                    registration_id=self.reg3.id,
                    round_number=round_num,
                    arrow_number=arrow_num,
                    points=8,  # Good performance
                    recorded_by=self.admin.id
                )
                db.session.add(score)
                arrow_num += 1
        
        db.session.commit()
    
    def test_competition_results_data_structure(self):
        """Test that results data structure is correct"""
        self.add_test_scores()
        
        # Test the data structure without involving routes
        results = self.competition.get_results_by_group()
        
        # Should have both groups
        self.assertIn('Adults', results)
        self.assertIn('Juniors', results)
        
        # Adults group should have 2 participants
        adult_results = results['Adults']
        self.assertEqual(len(adult_results), 2)
        
        # Should be ranked by score (highest first)
        self.assertEqual(adult_results[0].member_id, self.member1.id)  # Alice first
        self.assertEqual(adult_results[1].member_id, self.member2.id)  # Bob second
        
        # Check scores are correct
        self.assertEqual(adult_results[0].total_score, 162)  # Alice: 3*6*9
        self.assertEqual(adult_results[1].total_score, 84)   # Bob: 2*6*7
        
        # Juniors group should have 1 participant
        junior_results = results['Juniors']
        self.assertEqual(len(junior_results), 1)
        self.assertEqual(junior_results[0].total_score, 48)  # Charlie: 1*6*8
    
    def test_competition_results_ranking_accuracy(self):
        """Test that results ranking is mathematically correct"""
        self.add_test_scores()
        
        results = self.competition.get_results_by_group()
        adult_results = results['Adults']
        
        # Verify ranking logic
        self.assertEqual(len(adult_results), 2)
        
        # Alice should be first (higher total score)
        alice = adult_results[0]
        bob = adult_results[1]
        
        self.assertEqual(alice.member_id, self.member1.id)
        self.assertEqual(bob.member_id, self.member2.id)
        
        # Alice: 3 rounds * 6 arrows * 9 points = 162
        # Bob: 2 rounds * 6 arrows * 7 points = 84
        self.assertEqual(alice.total_score, 162)
        self.assertEqual(bob.total_score, 84)
        self.assertGreater(alice.total_score, bob.total_score)
    
    def test_competition_results_team_data(self):
        """Test results data structure with teams"""
        # Convert to team competition
        self.competition.max_team_size = 2
        db.session.commit()
        
        # Create team
        team = CompetitionTeam(
            group_id=self.adults_group.id,
            team_number=1,
            target_number=1
        )
        db.session.add(team)
        db.session.commit()
        
        # Assign members to team
        self.reg1.team_id = team.id
        self.reg2.team_id = team.id
        db.session.commit()
        
        self.add_test_scores()
        
        results = self.competition.get_results_by_group()
        adult_results = results['Adults']
        
        # Both members should be on the same team
        self.assertEqual(adult_results[0].team_id, team.id)
        self.assertEqual(adult_results[1].team_id, team.id)
        self.assertEqual(adult_results[0].team.team_number, 1)
        self.assertEqual(adult_results[1].team.team_number, 1)
    
    def test_competition_results_empty_state(self):
        """Test results with no participants"""
        # Create empty competition
        empty_event = ShootingEvent(
            name='Empty Competition',
            location='Test Location',  # Add required field
            date=date(2025, 12, 20),
            start_time=time(10, 0),
            duration_hours=4,
            created_by=self.admin.id
        )
        db.session.add(empty_event)
        db.session.commit()
        
        empty_competition = Competition(
            event_id=empty_event.id,
            number_of_rounds=3,
            arrows_per_round=6,
            status='setup',
            created_by=self.admin.id
        )
        db.session.add(empty_competition)
        db.session.commit()
        
        results = empty_competition.get_results_by_group()
        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 0)
    
    def test_competition_results_scoring_calculations(self):
        """Test that scoring calculations are mathematically correct"""
        self.add_test_scores()
        
        results = self.competition.get_results_by_group()
        adult_results = results['Adults']
        
        alice = adult_results[0]
        bob = adult_results[1]
        
        # Alice: 3 rounds * 6 arrows * 9 points = 162
        # Bob: 2 rounds * 6 arrows * 7 points = 84
        # Max possible: 3 rounds * 6 arrows * 10 points = 180
        
        alice_percentage = (alice.total_score / self.competition.max_possible_score * 100)
        bob_percentage = (bob.total_score / self.competition.max_possible_score * 100)
        
        self.assertAlmostEqual(alice_percentage, 90.0, places=1)
        self.assertAlmostEqual(bob_percentage, 46.7, places=1)
        
        # Test completion ratios
        self.assertEqual(alice.completed_rounds / self.competition.number_of_rounds, 1.0)  # 100% complete
        self.assertAlmostEqual(bob.completed_rounds / self.competition.number_of_rounds, 0.667, places=2)  # 67% complete
    
    def test_competition_results_completion_states(self):
        """Test participants in different completion states"""
        self.add_test_scores()  # This gives us mixed completion states
        
        results = self.competition.get_results_by_group()
        
        adult_results = results['Adults']
        junior_results = results['Juniors']
        
        # Alice: 3/3 rounds complete (member1)
        alice = adult_results[0]
        self.assertEqual(alice.completed_rounds, 3)
        self.assertTrue(alice.is_complete)
        
        # Bob: 2/3 rounds complete (member2)
        bob = adult_results[1]
        self.assertEqual(bob.completed_rounds, 2)
        self.assertFalse(bob.is_complete)
        
        # Charlie: 1/3 rounds complete (member3)
        charlie = junior_results[0]
        self.assertEqual(charlie.completed_rounds, 1)
        self.assertFalse(charlie.is_complete)
    
    def test_results_data_consistency_and_structure(self):
        """Test that the results data structure is consistent and well-formed"""
        self.add_test_scores()
        
        results = self.competition.get_results_by_group()
        
        # Should be dictionary with group names as keys
        self.assertIsInstance(results, dict)
        
        # Each value should be list of registrations sorted by score
        for group_name, registrations in results.items():
            self.assertIsInstance(registrations, list)
            self.assertIsInstance(group_name, str)
            
            # Should be sorted by total_score descending
            if len(registrations) > 1:
                for i in range(len(registrations) - 1):
                    self.assertGreaterEqual(
                        registrations[i].total_score,
                        registrations[i + 1].total_score,
                        f"Results not properly sorted by score in group {group_name}"
                    )
            
            # Each registration should have expected attributes
            for reg in registrations:
                self.assertIsNotNone(reg.member)
                self.assertIsNotNone(reg.group)
                self.assertIsInstance(reg.total_score, int)
                self.assertIsInstance(reg.completed_rounds, int)
                self.assertIsInstance(reg.is_complete, bool)

if __name__ == '__main__':
    unittest.main()
