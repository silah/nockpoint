from flask import request, jsonify
from datetime import datetime
from app.api import api_bp
from app.api.utils import token_required, get_current_api_user
from app.models import ShootingEvent, EventAttendance, BeginnersStudent, db


@api_bp.route('/events', methods=['GET'])
@token_required
def api_list_events():
    """API endpoint to list all events."""
    try:
        user = get_current_api_user()
        
        # Get query parameters for filtering
        event_type = request.args.get('type')  # regular, competition, beginners_course
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        
        # Start with base query
        query = ShootingEvent.query
        
        # Apply filters
        if event_type:
            query = query.filter(ShootingEvent.event_type == event_type)
            
        if from_date:
            try:
                from_date_parsed = datetime.fromisoformat(from_date.replace('Z', '+00:00')).date()
                query = query.filter(ShootingEvent.date >= from_date_parsed)
            except ValueError:
                return jsonify({'error': 'Invalid from_date format. Use ISO format'}), 400
                
        if to_date:
            try:
                to_date_parsed = datetime.fromisoformat(to_date.replace('Z', '+00:00')).date()
                query = query.filter(ShootingEvent.date <= to_date_parsed)
            except ValueError:
                return jsonify({'error': 'Invalid to_date format. Use ISO format'}), 400
                
        if upcoming_only:
            query = query.filter(ShootingEvent.date >= datetime.now().date())
            
        # Order by event date
        events = query.order_by(ShootingEvent.date).all()
        
        # Format events for API response
        events_data = []
        for event in events:
            # Check if user is already registered
            attendance = EventAttendance.query.filter_by(
                event_id=event.id,
                member_id=user.id
            ).first()
            
            # Calculate available spots
            total_registered = event.attendance_count
            beginners_count = BeginnersStudent.query.filter_by(event_id=event.id).count()
            available_spots = None
            if event.max_participants:
                available_spots = event.max_participants - total_registered - beginners_count
            
            event_data = {
                'id': event.id,
                'title': event.name,  # API uses 'title' for consistency
                'description': event.description,
                'event_date': datetime.combine(event.date, event.start_time).isoformat(),
                'event_type': event.event_type,
                'location': event.location,
                'max_participants': event.max_participants,
                'available_spots': available_spots,
                'is_free': event.is_free_event,
                'charge_amount': None,  # ShootingEvent doesn't have charge_amount in this model
                'user_registered': attendance is not None,
                'user_attended': attendance.attended if attendance else False,
                'registration_open': datetime.combine(event.date, event.start_time) > datetime.now(),
                'can_register': (
                    datetime.combine(event.date, event.start_time) > datetime.now() and 
                    (available_spots is None or available_spots > 0) and
                    attendance is None
                )
            }
            events_data.append(event_data)
        
        return jsonify({
            'events': events_data,
            'total': len(events_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/events/<int:event_id>', methods=['GET'])
@token_required
def api_get_event(event_id):
    """API endpoint to get details of a specific event."""
    try:
        user = get_current_api_user()
        
        event = ShootingEvent.query.get_or_404(event_id)
        
        # Check if user is already registered
        attendance = EventAttendance.query.filter_by(
            event_id=event.id,
            member_id=user.id
        ).first()
        
        # Calculate available spots
        total_registered = event.attendance_count
        beginners_count = BeginnersStudent.query.filter_by(event_id=event.id).count()
        available_spots = None
        if event.max_participants:
            available_spots = event.max_participants - total_registered - beginners_count
        
        # Get participants list
        participants = []
        for participant in event.attendances:
            participants.append({
                'id': participant.member.id,
                'name': f"{participant.member.first_name} {participant.member.last_name}",
                'attended': participant.attended
            })
        
        # Get beginners students if applicable
        students = []
        if event.event_type == 'beginners_course':
            beginners = BeginnersStudent.query.filter_by(event_id=event.id).all()
            for student in beginners:
                students.append({
                    'id': student.id,
                    'name': student.name,
                    'age': student.age,
                    'gender': student.gender,
                    'orientation': student.orientation
                })
        
        event_data = {
            'id': event.id,
            'title': event.name,  # API uses 'title' for consistency
            'description': event.description,
            'event_date': datetime.combine(event.date, event.start_time).isoformat(),
            'event_type': event.event_type,
            'location': event.location,
            'max_participants': event.max_participants,
            'available_spots': available_spots,
            'is_free': event.is_free_event,
            'charge_amount': None,  # ShootingEvent doesn't have charge_amount in this model
            'user_registered': attendance is not None,
            'user_attended': attendance.attended if attendance else False,
            'registration_open': datetime.combine(event.date, event.start_time) > datetime.now(),
            'can_register': (
                datetime.combine(event.date, event.start_time) > datetime.now() and 
                (available_spots is None or available_spots > 0) and
                attendance is None
            ),
            'participants': participants,
            'students': students
        }
        
        return jsonify(event_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/events/<int:event_id>/register', methods=['POST'])
@token_required
def api_register_for_event(event_id):
    """API endpoint for user to register for an event."""
    try:
        user = get_current_api_user()
        
        event = ShootingEvent.query.get_or_404(event_id)
        
        # Check if event is still open for registration
        if datetime.combine(event.date, event.start_time) <= datetime.now():
            return jsonify({'error': 'Event registration is closed'}), 400
        
        # Check if user is already registered
        existing_attendance = EventAttendance.query.filter_by(
            event_id=event_id,
            member_id=user.id
        ).first()
        
        if existing_attendance:
            return jsonify({'error': 'Already registered for this event'}), 400
        
        # Check capacity limits
        if event.max_participants:
            total_registered = event.attendance_count
            beginners_count = BeginnersStudent.query.filter_by(event_id=event.id).count()
            
            if total_registered + beginners_count >= event.max_participants:
                return jsonify({'error': 'Event is at maximum capacity'}), 400
        
        # Create attendance record
        attendance = EventAttendance(
            event_id=event_id,
            member_id=user.id,
            recorded_by=user.id  # Self-registration
        )
        
        db.session.add(attendance)
        
        # Create charge if event is not free (for now, skipping charges since model doesn't support it directly)
        # TODO: Implement charging system if needed
        
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully registered for event',
            'event_id': event_id,
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/events/<int:event_id>/unregister', methods=['DELETE'])
@token_required
def api_unregister_from_event(event_id):
    """API endpoint for user to unregister from an event."""
    try:
        user = get_current_api_user()
        
        event = ShootingEvent.query.get_or_404(event_id)
        
        # Check if event is still open for changes
        if datetime.combine(event.date, event.start_time) <= datetime.now():
            return jsonify({'error': 'Cannot unregister from past events'}), 400
        
        # Find attendance record
        attendance = EventAttendance.query.filter_by(
            event_id=event_id,
            member_id=user.id
        ).first()
        
        if not attendance:
            return jsonify({'error': 'Not registered for this event'}), 400
        
        # Remove attendance record
        db.session.delete(attendance)
        
        # Remove associated charges if not paid
        from app.models import MemberCharge
        unpaid_charges = MemberCharge.query.filter_by(
            member_id=user.id,
            event_id=event_id,
            paid_date=None
        ).all()
        
        for charge in unpaid_charges:
            db.session.delete(charge)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Successfully unregistered from event',
            'event_id': event_id,
            'user_id': user.id
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500