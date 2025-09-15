"""
Test Events models (ShootingEvent, EventAttendance, MemberCharge) functionality
"""
import unittest
from app import create_app, db
from app.models import User, ShootingEvent, EventAttendance, MemberCharge
from tests.conftest import BaseTestCase
from datetime import datetime, date, time
from decimal import Decimal

class TestEventsModels(BaseTestCase):
    """Test events-related models"""
    
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
        
        self.member = User(
            username='member',
            email='member@example.com',
            first_name='Test',
            last_name='Member',
            is_admin=False
        )
        self.member.set_password('password')
        
        db.session.add(self.admin)
        db.session.add(self.member)
        db.session.commit()
    
    def test_shooting_event_creation(self):
        """Test creating a shooting event"""
        event = ShootingEvent(
            name='Weekly Practice',
            description='Regular weekly practice session',
            location='Indoor Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            price=Decimal('15.00'),
            max_participants=20,
            created_by=self.admin.id
        )
        
        db.session.add(event)
        db.session.commit()
        
        # Verify event was created
        self.assertIsNotNone(event.id)
        self.assertEqual(event.name, 'Weekly Practice')
        self.assertEqual(event.location, 'Indoor Range')
        self.assertEqual(event.date, date(2025, 12, 1))
        self.assertEqual(event.start_time, time(9, 0))
        self.assertEqual(event.duration_hours, 2)
        self.assertEqual(event.price, Decimal('15.00'))
        self.assertEqual(event.max_participants, 20)
        self.assertIsNotNone(event.created_at)
    
    def test_shooting_event_properties(self):
        """Test shooting event computed properties"""
        event = ShootingEvent(
            name='Test Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 30),
            duration_hours=3,
            created_by=self.admin.id
        )
        
        # Test end_time property
        expected_end_time = time(12, 30)  # 9:30 + 3 hours
        self.assertEqual(event.end_time, expected_end_time)
        
        # Test is_past property (event is in future)
        self.assertFalse(event.is_past)
        
        # Test past event
        past_event = ShootingEvent(
            name='Past Event',
            location='Test Range',
            date=date(2020, 1, 1),  # Past date
            start_time=time(9, 0),
            duration_hours=2,
            created_by=self.admin.id
        )
        self.assertTrue(past_event.is_past)
    
    def test_event_attendance_creation(self):
        """Test creating event attendance record"""
        # Create event first
        event = ShootingEvent(
            name='Test Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            created_by=self.admin.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Create attendance record
        attendance = EventAttendance(
            event_id=event.id,
            member_id=self.member.id,
            recorded_by=self.admin.id,
            notes='Walk-in registration'
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        # Verify attendance was created
        self.assertIsNotNone(attendance.id)
        self.assertEqual(attendance.event_id, event.id)
        self.assertEqual(attendance.member_id, self.member.id)
        self.assertEqual(attendance.recorded_by, self.admin.id)
        self.assertEqual(attendance.notes, 'Walk-in registration')
        self.assertIsNotNone(attendance.created_at)
        self.assertIsNone(attendance.attended_at)  # Not attended yet
    
    def test_event_attendance_relationships(self):
        """Test event attendance relationships"""
        event = ShootingEvent(
            name='Test Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            created_by=self.admin.id
        )
        db.session.add(event)
        db.session.commit()
        
        attendance = EventAttendance(
            event_id=event.id,
            member_id=self.member.id,
            recorded_by=self.admin.id
        )
        db.session.add(attendance)
        db.session.commit()
        
        # Test relationships
        self.assertEqual(attendance.member.username, 'member')
        self.assertEqual(attendance.recorder.username, 'admin')
        self.assertEqual(len(event.attendances), 1)
        self.assertEqual(event.attendances[0].member.username, 'member')
    
    def test_event_attendance_attended_property(self):
        """Test attended property of EventAttendance"""
        event = ShootingEvent(
            name='Test Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            created_by=self.admin.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Create attendance without attended_at
        attendance = EventAttendance(
            event_id=event.id,
            member_id=self.member.id,
            recorded_by=self.admin.id
        )
        db.session.add(attendance)
        db.session.commit()
        
        # Should not be attended yet
        self.assertFalse(attendance.attended)
        
        # Mark as attended
        attendance.attended_at = datetime.utcnow()
        db.session.commit()
        
        # Should now be attended
        self.assertTrue(attendance.attended)
    
    def test_member_charge_creation(self):
        """Test creating member charge"""
        charge = MemberCharge(
            member_id=self.member.id,
            description='Event fee for Weekly Practice',
            amount=Decimal('15.00'),
            is_paid=False
        )
        
        db.session.add(charge)
        db.session.commit()
        
        # Verify charge was created
        self.assertIsNotNone(charge.id)
        self.assertEqual(charge.member_id, self.member.id)
        self.assertEqual(charge.amount, Decimal('15.00'))
        self.assertFalse(charge.is_paid)
        self.assertIsNotNone(charge.charge_date)
        self.assertIsNone(charge.paid_date)
    
    def test_member_charge_with_event(self):
        """Test member charge linked to an event"""
        event = ShootingEvent(
            name='Paid Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            price=Decimal('20.00'),
            created_by=self.admin.id
        )
        db.session.add(event)
        db.session.commit()
        
        charge = MemberCharge(
            member_id=self.member.id,
            event_id=event.id,
            description=f'Event fee for {event.name}',
            amount=event.price,
            is_paid=False
        )
        db.session.add(charge)
        db.session.commit()
        
        # Test relationships
        self.assertEqual(charge.event.name, 'Paid Event')
        self.assertEqual(charge.member.username, 'member')
        self.assertEqual(len(event.charges), 1)
        self.assertEqual(event.charges[0].amount, Decimal('20.00'))
    
    def test_member_charge_payment(self):
        """Test marking a charge as paid"""
        charge = MemberCharge(
            member_id=self.member.id,
            description='Test charge',
            amount=Decimal('10.00'),
            is_paid=False
        )
        db.session.add(charge)
        db.session.commit()
        
        # Mark as paid
        charge.is_paid = True
        charge.paid_date = datetime.utcnow()
        charge.paid_by_admin = self.admin.id
        charge.payment_notes = 'Cash payment'
        db.session.commit()
        
        # Verify payment details
        self.assertTrue(charge.is_paid)
        self.assertIsNotNone(charge.paid_date)
        self.assertEqual(charge.paid_by_admin, self.admin.id)
        self.assertEqual(charge.payment_notes, 'Cash payment')
    
    def test_event_attendance_count(self):
        """Test event attendance_count method"""
        event = ShootingEvent(
            name='Popular Event',
            location='Test Range',
            date=date(2025, 12, 1),
            start_time=time(9, 0),
            duration_hours=2,
            created_by=self.admin.id
        )
        db.session.add(event)
        db.session.commit()
        
        # Initially no attendances
        # Test attendance count
        self.assertEqual(event.attendance_count, 0)
        
        # Add some attendances
        for i in range(3):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                first_name=f'User{i}',
                last_name='Test'
            )
            user.set_password('password')
            db.session.add(user)
            db.session.flush()  # Get user.id
            
            attendance = EventAttendance(
                event_id=event.id,
                member_id=user.id,
                recorded_by=self.admin.id
            )
            db.session.add(attendance)
        
        db.session.commit()
        
        # Should now have 3 attendances
        self.assertEqual(event.attendance_count, 3)

if __name__ == '__main__':
    unittest.main()
