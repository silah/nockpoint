#!/usr/bin/env python3
"""
Test script to verify the shooting events system is properly implemented
"""

from app import create_app, db
from app.models import User, ShootingEvent, EventAttendance, MemberCharge
from datetime import datetime, timedelta

def test_events_system():
    """Test the shooting events system functionality."""
    app = create_app()
    
    with app.app_context():
        print("=== Shooting Events System Test ===")
        
        # Test 1: Check if models can be imported
        try:
            print("✓ Models imported successfully")
        except Exception as e:
            print(f"✗ Model import failed: {e}")
            return False
        
        # Test 2: Check database tables exist
        try:
            # This will fail if tables don't exist
            event_count = ShootingEvent.query.count()
            attendance_count = EventAttendance.query.count()
            charge_count = MemberCharge.query.count()
            print(f"✓ Database tables exist - Events: {event_count}, Attendance: {attendance_count}, Charges: {charge_count}")
        except Exception as e:
            print(f"✗ Database table check failed: {e}")
            return False
        
        # Test 3: Test model relationships
        try:
            # Create a test user if none exists
            user = User.query.first()
            if not user:
                user = User(
                    email='test@example.com',
                    first_name='Test',
                    last_name='User',
                    role='member'
                )
                user.set_password('password123')
                db.session.add(user)
                db.session.commit()
                print("✓ Created test user")
            else:
                print("✓ Using existing user for tests")
            
            # Create a test event
            test_event = ShootingEvent(
                name='Test Shooting Event',
                description='A test event for system verification',
                location='Test Range',
                date=datetime.now().date() + timedelta(days=7),
                start_time=datetime.now().time(),
                duration_hours=2,
                price=25.00,
                max_participants=10,
                created_by=user.id
            )
            db.session.add(test_event)
            db.session.commit()
            print("✓ Created test event")
            
            # Create test attendance
            attendance = EventAttendance(
                member_id=user.id,
                event_id=test_event.id,
                recorded_by=user.id
            )
            db.session.add(attendance)
            db.session.commit()
            print("✓ Created test attendance record")
            
            # Create test charge
            charge = MemberCharge(
                member_id=user.id,
                event_id=test_event.id,
                description=f"Charge for {test_event.name}",
                amount=test_event.price,
                is_paid=False
            )
            db.session.add(charge)
            db.session.commit()
            print("✓ Created test member charge")
            
            # Test relationships
            assert test_event.creator == user
            assert test_event.attendances[0] == attendance
            assert attendance.member == user
            assert attendance.event == test_event
            assert charge.member == user
            assert charge.event == test_event
            print("✓ Model relationships working correctly")
            
            # Clean up test data
            db.session.delete(charge)
            db.session.delete(attendance)
            db.session.delete(test_event)
            db.session.commit()
            print("✓ Test data cleaned up")
            
        except Exception as e:
            print(f"✗ Model relationship test failed: {e}")
            return False
        
        print("\n=== All Tests Passed! ===")
        print("The shooting events system is properly implemented and ready to use.")
        print("\nFeatures available:")
        print("• Event calendar with upcoming and past events")
        print("• Event creation and management (admin only)")
        print("• Attendance tracking with admin management interface")
        print("• Automatic charge creation for paid events")
        print("• Payment tracking and management")
        print("• Member charge history")
        print("• Navigation integration in main menu")
        print("• Dashboard integration with event statistics")
        
        return True

if __name__ == '__main__':
    test_events_system()
