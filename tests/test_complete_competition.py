import unittest
from datetime import date, time, datetime
from app import create_app, db
from app.models import User, ShootingEvent, Competition, CompetitionGroup, CompetitionRegistration, ArrowScore

class CompleteCompetitionTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        config = {
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False,
            'SECRET_KEY': 'test-secret-key',
            'WTF_CSRF_ENABLED': False
        }
        self.app = create_app(config)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test users
        self.admin_user = User(
            username='admin',
            email='admin@test.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        self.admin_user.set_password('password')
        
        self.member_user = User(
            username='member',
            email='member@test.com',
            first_name='Member',
            last_name='User',
            role='member'
        )
        self.member_user.set_password('password')
        
        db.session.add(self.admin_user)
        db.session.add(self.member_user)
        
        # Create test event
        self.event = ShootingEvent(
            name='Test Competition Event',
            description='Test event for competition',
            location='Test Range',
            date=date.today(),
            start_time=time(10, 0),
            duration_hours=3,
            price=25.00,
            created_by=1
        )
        db.session.add(self.event)
        
        # Create test competition
        self.competition = Competition(
            event_id=1,
            number_of_rounds=3,
            target_size_cm=122,
            arrows_per_round=6,
            max_team_size=4,
            status='in_progress',
            created_by=1
        )
        db.session.add(self.competition)
        
        # Create test group
        self.group = CompetitionGroup(
            competition_id=1,
            name='Adult',
            description='Adult group'
        )
        db.session.add(self.group)
        
        # Create test registrations
        self.registration1 = CompetitionRegistration(
            competition_id=1,
            member_id=1,
            group_id=1
        )
        self.registration2 = CompetitionRegistration(
            competition_id=1,
            member_id=2,
            group_id=1
        )
        db.session.add(self.registration1)
        db.session.add(self.registration2)
        
        db.session.commit()
        
        self.client = self.app.test_client()

    def tearDown(self):
        """Clean up test environment"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login_as_admin(self):
        """Helper method to log in as admin"""
        return self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'password'
        }, follow_redirects=True)

    def test_complete_competition_with_partial_scores(self):
        """Test completing competition when some participants have partial scores"""
        self.login_as_admin()
        
        # Add partial scores for registration1 (only 9 arrows out of 18 total)
        for i in range(1, 10):  # 9 arrows
            round_num = ((i - 1) // 6) + 1
            arrow_score = ArrowScore(
                registration_id=1,
                arrow_number=i,
                points=8,
                is_x=False,
                round_number=round_num,
                recorded_by=1
            )
            db.session.add(arrow_score)
        
        # Add no scores for registration2
        db.session.commit()
        
        # Check initial state
        self.assertEqual(len(self.registration1.arrow_scores), 9)
        self.assertEqual(len(self.registration2.arrow_scores), 0)
        self.assertFalse(self.registration1.is_complete)
        self.assertFalse(self.registration2.is_complete)
        
        # Complete the competition
        response = self.client.post(f'/competitions/{self.competition.id}/complete')
        
        # Check that we were redirected (successful completion)
        self.assertEqual(response.status_code, 302)
        
        # Refresh from database
        db.session.refresh(self.registration1)
        db.session.refresh(self.registration2)
        db.session.refresh(self.competition)
        
        # Check that missing arrows were filled with 0-point scores
        self.assertEqual(len(self.registration1.arrow_scores), 18)  # Should now have all 18 arrows
        self.assertEqual(len(self.registration2.arrow_scores), 18)  # Should now have all 18 arrows
        
        # Check that the new arrows are 0-point scores
        registration1_arrows = sorted(self.registration1.arrow_scores, key=lambda x: x.arrow_number)
        registration2_arrows = sorted(self.registration2.arrow_scores, key=lambda x: x.arrow_number)
        
        # First 9 arrows of registration1 should be original scores (8 points each)
        for i in range(9):
            self.assertEqual(registration1_arrows[i].points, 8)
        
        # Last 9 arrows of registration1 should be 0-point auto-fills
        for i in range(9, 18):
            self.assertEqual(registration1_arrows[i].points, 0)
            self.assertEqual(registration1_arrows[i].notes, "Auto-filled on competition completion")
        
        # All arrows of registration2 should be 0-point auto-fills
        for arrow in registration2_arrows:
            self.assertEqual(arrow.points, 0)
            self.assertEqual(arrow.notes, "Auto-filled on competition completion")
        
        # Check that both registrations are now complete
        self.assertTrue(self.registration1.is_complete)
        self.assertTrue(self.registration2.is_complete)
        
        # Check that competition status is completed
        self.assertEqual(self.competition.status, 'completed')

    def test_complete_competition_with_no_scores(self):
        """Test completing competition when no participants have any scores"""
        self.login_as_admin()
        
        # Complete the competition without any scores
        response = self.client.post(f'/competitions/{self.competition.id}/complete')
        
        # Check that we were redirected (successful completion)
        self.assertEqual(response.status_code, 302)
        
        # Refresh from database
        db.session.refresh(self.registration1)
        db.session.refresh(self.registration2)
        db.session.refresh(self.competition)
        
        # Check that all arrows were filled with 0-point scores
        self.assertEqual(len(self.registration1.arrow_scores), 18)
        self.assertEqual(len(self.registration2.arrow_scores), 18)
        
        # Check that all arrows are 0-point scores
        for arrow in self.registration1.arrow_scores:
            self.assertEqual(arrow.points, 0)
            self.assertEqual(arrow.notes, "Auto-filled on competition completion")
        
        for arrow in self.registration2.arrow_scores:
            self.assertEqual(arrow.points, 0)
            self.assertEqual(arrow.notes, "Auto-filled on competition completion")
        
        # Check that competition is completed
        self.assertEqual(self.competition.status, 'completed')

    def test_complete_competition_with_full_scores(self):
        """Test completing competition when all participants have full scores"""
        self.login_as_admin()
        
        # Add full scores for both registrations
        for reg_id in [1, 2]:
            for i in range(1, 19):  # All 18 arrows
                round_num = ((i - 1) // 6) + 1
                arrow_score = ArrowScore(
                    registration_id=reg_id,
                    arrow_number=i,
                    points=9,
                    is_x=False,
                    round_number=round_num,
                    recorded_by=1
                )
                db.session.add(arrow_score)
        
        db.session.commit()
        
        # Check initial state - both should be complete
        self.assertTrue(self.registration1.is_complete)
        self.assertTrue(self.registration2.is_complete)
        
        # Complete the competition
        response = self.client.post(f'/competitions/{self.competition.id}/complete')
        
        # Check that we were redirected (successful completion)
        self.assertEqual(response.status_code, 302)
        
        # Refresh from database
        db.session.refresh(self.competition)
        
        # Check that no additional arrows were created
        self.assertEqual(len(self.registration1.arrow_scores), 18)
        self.assertEqual(len(self.registration2.arrow_scores), 18)
        
        # Check that competition is completed
        self.assertEqual(self.competition.status, 'completed')

    def test_completion_stats_calculation(self):
        """Test that completion stats are calculated correctly"""
        # Add partial scores for registration1
        for i in range(1, 10):  # 9 arrows out of 18
            round_num = ((i - 1) // 6) + 1
            arrow_score = ArrowScore(
                registration_id=1,
                arrow_number=i,
                points=7,
                is_x=False,
                round_number=round_num,
                recorded_by=1
            )
            db.session.add(arrow_score)
        
        db.session.commit()
        
        # Get completion stats
        stats = self.competition.get_completion_stats()
        
        self.assertEqual(stats['total_participants'], 2)
        self.assertEqual(stats['completed_participants'], 0)  # Neither is complete
        self.assertEqual(stats['completion_percentage'], 0)
        self.assertEqual(stats['missing_arrows_total'], 27)  # 9 missing from reg1, 18 missing from reg2

if __name__ == '__main__':
    unittest.main()
