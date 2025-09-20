from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import ShootingEvent, EventAttendance, MemberCharge, User, Competition, BeginnersStudent
from app.forms import ShootingEventForm, AttendanceForm, PaymentUpdateForm, CompetitionForm, BeginnersStudentForm
from datetime import datetime, date, time
from sqlalchemy import desc, asc
from decimal import Decimal

events_bp = Blueprint('events', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@events_bp.route('/')
@login_required
def calendar():
    """Show shooting calendar"""
    # Get upcoming events
    upcoming_events = ShootingEvent.query.filter(
        ShootingEvent.date >= date.today()
    ).order_by(ShootingEvent.date, ShootingEvent.start_time).all()
    
    # Get past events (last 30 days)
    past_events = ShootingEvent.query.filter(
        ShootingEvent.date < date.today()
    ).order_by(desc(ShootingEvent.date), desc(ShootingEvent.start_time)).limit(10).all()
    
    return render_template('events/calendar.html', 
                         upcoming_events=upcoming_events,
                         past_events=past_events)

@events_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_event():
    """Create new shooting event"""
    form = ShootingEventForm(auto_populate_location=True)
    
    if form.validate_on_submit():
        try:
            # Parse time string
            start_time_obj = datetime.strptime(form.start_time.data, '%H:%M').time()
            
            event = ShootingEvent(
                name=form.name.data,
                description=form.description.data,
                location=form.location.data,
                date=form.date.data,
                start_time=start_time_obj,
                duration_hours=form.duration_hours.data,
                event_type=form.event_type.data,
                is_free_event=form.is_free_event.data,
                max_participants=form.max_participants.data,
                created_by=current_user.id
            )
            
            db.session.add(event)
            db.session.commit()
            
            flash(f'Shooting event "{event.name}" created successfully!', 'success')
            return redirect(url_for('events.view_event', id=event.id))
            
        except ValueError:
            flash('Invalid time format. Please use HH:MM format (e.g., 14:30)', 'error')
    
    return render_template('events/event_form.html', form=form, title='New Shooting Event')

@events_bp.route('/events/<int:id>')
@login_required
def view_event(id):
    """View event details and attendees"""
    event = ShootingEvent.query.get_or_404(id)
    attendances = EventAttendance.query.filter_by(event_id=id).all()
    
    # Get all participants (from attendances and registered members)
    all_participants = User.query.join(
        EventAttendance, User.id == EventAttendance.member_id
    ).filter(
        EventAttendance.event_id == id
    ).all()
    
    # Check if current user is registered
    user_registration = EventAttendance.query.filter_by(
        event_id=id, member_id=current_user.id
    ).first()
    
    # Get competitions for this event
    competitions = Competition.query.filter_by(event_id=id).all()
    
    # Create competition form (needed by template)
    competition_form = CompetitionForm()
    
    # Get beginners course data if this is a beginners course
    beginners_students = []
    beginners_student_form = None
    if event.event_type == 'beginners_course':
        beginners_students = BeginnersStudent.query.filter_by(event_id=id).all()
        beginners_student_form = BeginnersStudentForm()
    
    # Count totals for display
    total_members = len(all_participants)
    total_students = len(beginners_students) if event.event_type == 'beginners_course' else 0
    total_registered = total_members + total_students
    
    total_attended = sum(1 for attendance in attendances if attendance.attended_at)
    attended_count = total_attended  # Alias for template compatibility
    attendance_count = total_registered  # Alias for template compatibility
    
    return render_template('events/view_event.html', 
                         event=event, 
                         attendances=attendances,
                         all_participants=all_participants,
                         competitions=competitions,
                         competition_form=competition_form,
                         beginners_students=beginners_students,
                         beginners_student_form=beginners_student_form,
                         total_members=total_members,
                         total_students=total_students,
                         total_registered=total_registered,
                         total_attended=total_attended,
                         attended_count=attended_count,
                         attendance_count=attendance_count,
                         user_registration=user_registration)

@events_bp.route('/event/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_event(id):
    """Edit shooting event"""
    event = ShootingEvent.query.get_or_404(id)
    form = ShootingEventForm(obj=event)
    
    if request.method == 'GET':
        # Set the time field as string
        form.start_time.data = event.start_time.strftime('%H:%M')
        # Ensure event_type is properly set
        form.event_type.data = event.event_type
    
    if form.validate_on_submit():
        try:
            start_time_obj = datetime.strptime(form.start_time.data, '%H:%M').time()
            
            event.name = form.name.data
            event.description = form.description.data
            event.location = form.location.data
            event.date = form.date.data
            event.start_time = start_time_obj
            event.duration_hours = form.duration_hours.data
            event.event_type = form.event_type.data
            event.is_free_event = form.is_free_event.data
            event.max_participants = form.max_participants.data
            
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for('events.view_event', id=event.id))
            
        except ValueError:
            flash('Invalid time format. Please use HH:MM format (e.g., 14:30)', 'error')
    
    return render_template('events/event_form.html', form=form, title='Edit Event', event=event)

@events_bp.route('/event/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_event(id):
    """Delete shooting event"""
    event = ShootingEvent.query.get_or_404(id)
    
    # Check if event has attendances
    if event.attendances:
        flash('Cannot delete event with recorded attendances. Consider canceling the event instead.', 'error')
        return redirect(url_for('events.view_event', id=id))
    
    event_name = event.name
    db.session.delete(event)
    db.session.commit()
    
    flash(f'Event "{event_name}" deleted successfully.', 'success')
    return redirect(url_for('events.calendar'))

@events_bp.route('/event/<int:id>/attendance', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_attendance(id):
    """Manage event attendance"""
    event = ShootingEvent.query.get_or_404(id)
    form = AttendanceForm()
    
    if form.validate_on_submit():
        # Check if member is already marked as attended
        existing_attendance = EventAttendance.query.filter_by(
            event_id=id,
            member_id=form.member_id.data
        ).first()
        
        if existing_attendance:
            flash('Member is already marked as attended for this event.', 'error')
        else:
            # Create attendance record
            attendance = EventAttendance(
                event_id=id,
                member_id=form.member_id.data,
                recorded_by=current_user.id,
                notes=form.notes.data
            )
            db.session.add(attendance)
            
            # If this is a competition event, auto-register them for competition
            if event.competition and len(event.competition) > 0:
                from app.models import CompetitionRegistration
                competition = event.competition[0]
                
                # Check if already registered for competition
                existing_comp_registration = CompetitionRegistration.query.filter_by(
                    competition_id=competition.id, member_id=form.member_id.data
                ).first()
                
                if not existing_comp_registration:
                    # Get the first available group
                    if competition.groups:
                        default_group = competition.groups[0]
                        comp_registration = CompetitionRegistration(
                            competition_id=competition.id,
                            member_id=form.member_id.data,
                            group_id=default_group.id,
                            notes=f'Auto-registered via event attendance by admin: {current_user.first_name} {current_user.last_name}'
                        )
                        db.session.add(comp_registration)
            
            # Create charge for the member if event is not free
            if not event.is_free_event:
                member = User.query.get(form.member_id.data)
                member_price = member.get_membership_price()
                charge = MemberCharge(
                    member_id=member.id,
                    event_id=event.id,
                    description=f'Shooting event: {event.name} on {event.date.strftime("%Y-%m-%d")}',
                    amount=member_price
                )
                db.session.add(charge)
            
            db.session.commit()
            
            member = User.query.get(form.member_id.data)
            flash(f'Attendance recorded for {member.first_name} {member.last_name}', 'success')
            
            # Reset form
            form.member_id.data = ''
            form.notes.data = ''
    
    # Get current attendances
    attendances = EventAttendance.query.filter_by(event_id=id).join(User, EventAttendance.member_id == User.id).order_by(User.first_name, User.last_name).all()
    
    # Calculate statistics for template
    attended_count = sum(1 for attendance in attendances if attendance.attended_at is not None)
    
    # Get available users for the add attendee modal (users not already registered)
    registered_user_ids = [attendance.member_id for attendance in attendances]
    available_users = User.query.filter(
        User.is_active == True,
        ~User.id.in_(registered_user_ids)
    ).order_by(User.first_name, User.last_name).all()
    
    # Get competition groups if this is a competition event
    competition_groups = []
    if event.competition and len(event.competition) > 0:
        competition = event.competition[0]
        competition_groups = competition.groups
    
    # For template compatibility, also pass attendances as 'all_attendees'
    all_attendees = attendances
    
    return render_template('events/manage_attendance.html', 
                         event=event, 
                         form=form, 
                         attendances=attendances,
                         all_attendees=all_attendees,
                         attended_count=attended_count,
                         available_users=available_users,
                         competition_groups=competition_groups)

@events_bp.route('/payments')
@login_required
@admin_required
def outstanding_payments():
    """Show outstanding payments admin page"""
    # Get all charges (both paid and unpaid) for comprehensive view
    all_charges = MemberCharge.query.join(User, MemberCharge.member_id == User.id).order_by(
        MemberCharge.charge_date.desc()
    ).all()
    
    # Get only unpaid charges for statistics
    unpaid_charges = [charge for charge in all_charges if not charge.is_paid]
    
    # Calculate total outstanding and unique members with debt
    total_outstanding = sum(charge.amount for charge in unpaid_charges)
    unique_members = len(set(charge.member_id for charge in unpaid_charges))
    
    return render_template('events/outstanding_payments.html', 
                         all_charges=all_charges,  # For template display
                         unpaid_charges=unpaid_charges,
                         outstanding_charges=unpaid_charges,  # For template compatibility
                         total_outstanding=total_outstanding,
                         unique_members=unique_members)

@events_bp.route('/payment/<int:id>/mark-paid', methods=['POST'])
@login_required
@admin_required
def mark_payment_paid(id):
    """Mark a payment as paid"""
    charge = MemberCharge.query.get_or_404(id)
    
    if charge.is_paid:
        flash('Payment is already marked as paid.', 'warning')
        return redirect(url_for('events.outstanding_payments'))
    
    form = PaymentUpdateForm()
    if form.validate_on_submit():
        charge.is_paid = True
        charge.paid_date = datetime.utcnow()
        charge.paid_by_admin = current_user.id
        charge.payment_notes = form.payment_notes.data
        
        db.session.commit()
        
        flash(f'Payment marked as paid for {charge.member.first_name} {charge.member.last_name}', 'success')
    
    return redirect(url_for('events.outstanding_payments'))

@events_bp.route('/my-charges')
@login_required
def my_charges():
    """Show current user's charges"""
    charges = MemberCharge.query.filter_by(member_id=current_user.id).order_by(
        desc(MemberCharge.charge_date)
    ).all()
    
    # Separate charges into paid and unpaid
    outstanding_charges = [charge for charge in charges if not charge.is_paid]
    paid_charges = [charge for charge in charges if charge.is_paid]
    
    # Calculate outstanding and paid amounts
    total_outstanding = sum(charge.amount for charge in outstanding_charges)
    total_paid = sum(charge.amount for charge in paid_charges)
    
    return render_template('events/my_charges.html', 
                         charges=charges,
                         my_charges=charges,  # Template uses both 'charges' and 'my_charges'
                         outstanding_charges=outstanding_charges,
                         paid_charges=paid_charges,
                         total_outstanding=total_outstanding,
                         total_paid=total_paid)

@events_bp.route('/event/<int:event_id>/add-attendee', methods=['POST'])
@login_required
@admin_required
def add_attendee(event_id):
    """Add an attendee to an event"""
    event = ShootingEvent.query.get_or_404(event_id)
    
    member_id = request.form.get('member_id', type=int)
    mark_attended = request.form.get('mark_attended') == '1'
    group_id = request.form.get('group_id', type=int)  # For competition events
    
    if not member_id:
        flash('Please select a member', 'error')
        return redirect(url_for('events.manage_attendance', id=event_id))
    
    # Check if already registered
    existing = EventAttendance.query.filter_by(
        event_id=event_id, member_id=member_id
    ).first()
    
    if existing:
        flash('Member is already registered for this event', 'error')
        return redirect(url_for('events.manage_attendance', id=event_id))
    
    try:
        # Create attendance record
        attendance = EventAttendance(
            event_id=event_id,
            member_id=member_id,
            recorded_by=current_user.id
        )
        
        if mark_attended:
            attendance.attended_at = datetime.utcnow()
        
        db.session.add(attendance)
        
        # If this is a competition event and member is attending, auto-register them for competition
        if mark_attended and event.competition and len(event.competition) > 0:
            from app.models import CompetitionRegistration
            competition = event.competition[0]
            
            # Check if already registered for competition
            existing_comp_registration = CompetitionRegistration.query.filter_by(
                competition_id=competition.id, member_id=member_id
            ).first()
            
            if not existing_comp_registration:
                # Use provided group_id or default to first group
                target_group_id = group_id if group_id else (competition.groups[0].id if competition.groups else None)
                
                if target_group_id:
                    comp_registration = CompetitionRegistration(
                        competition_id=competition.id,
                        member_id=member_id,
                        group_id=target_group_id,
                        notes=f'Auto-registered via event attendance by admin: {current_user.first_name} {current_user.last_name}'
                    )
                    db.session.add(comp_registration)
        
        # Create charge if event is not free and member attended
        if mark_attended and not event.is_free_event:
            member = User.query.get(member_id)
            member_price = member.get_membership_price()
            charge = MemberCharge(
                member_id=member.id,
                event_id=event.id,
                description=f"Charge for {event.name}",
                amount=member_price,
                is_paid=False
            )
            db.session.add(charge)
        
        db.session.commit()
        
        member = User.query.get(member_id)
        flash(f'{member.first_name} {member.last_name} has been added to the event', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error adding attendee: {str(e)}', 'error')
    
    return redirect(url_for('events.manage_attendance', id=event_id))

@events_bp.route('/event/<int:id>/update-attendance', methods=['POST'])
@login_required
@admin_required
def update_attendance(id):
    """Update attendance status via AJAX"""
    
    data = request.get_json()
    attendee_id = data.get('attendee_id')
    attended = data.get('attended', False)
    
    try:
        attendance = EventAttendance.query.filter_by(
            event_id=id, member_id=attendee_id
        ).first()
        
        if not attendance:
            return jsonify({'success': False, 'error': 'Attendance record not found'})
        
        # Update attended status
        attendance.attended_at = datetime.utcnow() if attended else None
        attendance.recorded_by = current_user.id
        
        # Get event for further processing
        event = ShootingEvent.query.get(id)
        
        # If this is a competition event and member is now attending, auto-register them for competition
        if attended and event.competition and len(event.competition) > 0:
            from app.models import CompetitionRegistration
            competition = event.competition[0]
            
            # Check if already registered for competition
            existing_comp_registration = CompetitionRegistration.query.filter_by(
                competition_id=competition.id, member_id=attendee_id
            ).first()
            
            if not existing_comp_registration:
                # Get the first available group
                if competition.groups:
                    default_group = competition.groups[0]
                    comp_registration = CompetitionRegistration(
                        competition_id=competition.id,
                        member_id=attendee_id,
                        group_id=default_group.id,
                        notes=f'Auto-registered via event attendance by admin: {current_user.first_name} {current_user.last_name}'
                    )
                    db.session.add(comp_registration)
        
        # Create charge if attending and event is not free
        if attended and not event.is_free_event:
            existing_charge = MemberCharge.query.filter_by(
                member_id=attendee_id, event_id=id
            ).first()
            
            if not existing_charge:
                member = User.query.get(attendee_id)
                member_price = member.get_membership_price()
                charge = MemberCharge(
                    member_id=attendee_id,
                    event_id=id,
                    description=f"Charge for {event.name}",
                    amount=member_price,
                    is_paid=False
                )
                db.session.add(charge)
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@events_bp.route('/mark-paid', methods=['POST'])
@login_required
@admin_required
def mark_paid():
    """Mark a charge as paid via AJAX"""
    
    data = request.get_json()
    charge_id = data.get('charge_id')
    
    try:
        charge = MemberCharge.query.get_or_404(charge_id)
        charge.is_paid = True
        charge.paid_date = datetime.utcnow()
        charge.paid_by_admin = current_user.id
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@events_bp.route('/attendance/<int:id>/remove', methods=['POST'])
@login_required  
@admin_required
def remove_attendee(id):
    """Remove an attendee from an event via AJAX"""
    
    data = request.get_json()
    member_id = data.get('member_id')
    
    try:
        # Find and remove attendance record
        attendance = EventAttendance.query.filter_by(
            event_id=id, member_id=member_id
        ).first()
        
        if not attendance:
            return jsonify({'success': False, 'error': 'Attendance record not found'})
        
        # Remove associated charges
        charges = MemberCharge.query.filter_by(
            member_id=member_id, event_id=id
        ).all()
        
        for charge in charges:
            db.session.delete(charge)
        
        db.session.delete(attendance)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@events_bp.route('/update-payment-status', methods=['POST'])
@login_required
@admin_required
def update_payment_status():
    """Update payment status via AJAX"""
    
    data = request.get_json()
    charge_id = data.get('charge_id')
    paid = data.get('paid', False)
    
    try:
        charge = MemberCharge.query.get_or_404(charge_id)
        charge.is_paid = paid
        
        if paid:
            charge.paid_date = datetime.utcnow()
            charge.paid_by_admin = current_user.id
        else:
            charge.paid_date = None
            charge.paid_by_admin = None
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@events_bp.route('/update-charge-amount', methods=['POST'])
@login_required
@admin_required
def update_charge_amount():
    """Update charge amount via AJAX"""
    
    data = request.get_json()
    charge_id = data.get('charge_id')
    new_amount = data.get('amount')
    
    try:
        charge = MemberCharge.query.get_or_404(charge_id)
        charge.amount = Decimal(str(new_amount))
        
        db.session.commit()
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@events_bp.route('/delete-charge', methods=['POST'])
@login_required
@admin_required  
def delete_charge():
    """Delete a charge via AJAX"""
    
    data = request.get_json()
    charge_id = data.get('charge_id')
    
    try:
        charge = MemberCharge.query.get_or_404(charge_id)
        db.session.delete(charge)
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})

@events_bp.route('/event/<int:id>/update-competition', methods=['POST'])
@login_required
@admin_required
def update_event_competition(id):
    """Update competition settings from event view"""
    event = ShootingEvent.query.get_or_404(id)
    
    # Check if event has a competition
    if not event.competition or len(event.competition) == 0:
        flash('No competition found for this event.', 'error')
        return redirect(url_for('events.view_event', id=id))
    
    competition = event.competition[0]
    form = CompetitionForm()
    
    if form.validate_on_submit():
        # Update competition fields
        competition.number_of_rounds = form.number_of_rounds.data
        competition.arrows_per_round = form.arrows_per_round.data
        competition.target_size_cm = form.target_size_cm.data
        competition.max_team_size = form.max_team_size.data
        
        db.session.commit()
        flash('Competition settings updated successfully!', 'success')
        return redirect(url_for('events.view_event', id=id))
    
    # If validation fails, show errors
    for field, errors in form.errors.items():
        for error in errors:
            flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('events.view_event', id=id))

@events_bp.route('/event/<int:id>/register', methods=['POST'])
@login_required
def register_for_event(id):
    """Register current user for an event"""
    event = ShootingEvent.query.get_or_404(id)
    
    # Check if already registered
    existing_attendance = EventAttendance.query.filter_by(
        event_id=id, member_id=current_user.id
    ).first()
    
    if existing_attendance:
        flash('You are already registered for this event.', 'warning')
        return redirect(url_for('events.view_event', id=id))
    
    # Check capacity if set
    if event.max_participants:
        current_members = EventAttendance.query.filter_by(event_id=id).count()
        current_students = BeginnersStudent.query.filter_by(event_id=id).count() if event.event_type == 'beginners_course' else 0
        total_participants = current_members + current_students
        
        if total_participants >= event.max_participants:
            flash('This event is full. No more registrations accepted.', 'error')
            return redirect(url_for('events.view_event', id=id))
    
    # Create attendance record (registration)
    attendance = EventAttendance(
        event_id=id,
        member_id=current_user.id,
        recorded_by=current_user.id,  # Self-registration
        notes='Self-registered by member'
    )
    
    db.session.add(attendance)
    
    # Create charge if event is not free
    if not event.is_free_event:
        member_price = current_user.get_membership_price()
        charge = MemberCharge(
            member_id=current_user.id,
            event_id=id,
            description=f'Shooting event: {event.name} on {event.date.strftime("%Y-%m-%d")}',
            amount=member_price
        )
        db.session.add(charge)
    
    db.session.commit()
    
    if event.is_free_event:
        flash('Successfully registered for this event!', 'success')
    else:
        flash(f'Successfully registered! A charge of ${current_user.get_membership_price():.2f} has been added to your account.', 'success')
    
    return redirect(url_for('events.view_event', id=id))


@events_bp.route('/event/<int:id>/cancel-registration', methods=['POST'])
@login_required
def cancel_registration(id):
    """Cancel current user's registration for an event"""
    event = ShootingEvent.query.get_or_404(id)
    
    # Find existing attendance record
    attendance = EventAttendance.query.filter_by(
        event_id=id, member_id=current_user.id
    ).first()
    
    if not attendance:
        flash('You are not registered for this event.', 'warning')
        return redirect(url_for('events.view_event', id=id))
    
    # Check if already attended - cannot cancel if attended
    if attendance.attended_at:
        flash('Cannot cancel registration - you have already attended this event.', 'error')
        return redirect(url_for('events.view_event', id=id))
    
    # Remove associated charges if not paid
    charges = MemberCharge.query.filter_by(
        event_id=id, member_id=current_user.id, is_paid=False
    ).all()
    
    for charge in charges:
        db.session.delete(charge)
    
    # Remove attendance record
    db.session.delete(attendance)
    db.session.commit()
    
    flash('Registration cancelled successfully!', 'success')
    return redirect(url_for('events.view_event', id=id))


# Beginners Course Student Management Routes

@events_bp.route('/events/<int:event_id>/beginners/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_beginners_student(event_id):
    """Add a student to a beginners course"""
    event = ShootingEvent.query.get_or_404(event_id)
    
    if event.event_type != 'beginners_course':
        flash('This is not a beginners course event.', 'error')
        return redirect(url_for('events.view_event', id=event_id))
    
    form = BeginnersStudentForm()
    
    if form.validate_on_submit():
        # Check capacity if set
        if event.max_participants:
            current_members = EventAttendance.query.filter_by(event_id=event_id).count()
            current_students = BeginnersStudent.query.filter_by(event_id=event_id).count()
            total_participants = current_members + current_students
            
            if total_participants >= event.max_participants:
                flash('This event is full. No more participants can be added.', 'error')
                return redirect(url_for('events.view_event', id=event_id))
        
        student = BeginnersStudent(
            event_id=event_id,
            name=form.name.data,
            age=form.age.data,
            height_cm=form.height_cm.data,
            gender=form.gender.data,
            orientation=form.orientation.data,
            has_paid=form.has_paid.data,
            insurance_done=form.insurance_done.data,
            notes=form.notes.data
        )
        
        db.session.add(student)
        db.session.commit()
        
        flash(f'Student {student.name} added to course successfully!', 'success')
        return redirect(url_for('events.view_event', id=event_id))
    
    return render_template('events/add_beginners_student.html', 
                         form=form, event=event)


@events_bp.route('/events/<int:event_id>/beginners/<int:student_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_beginners_student(event_id, student_id):
    """Edit a beginners course student"""
    event = ShootingEvent.query.get_or_404(event_id)
    student = BeginnersStudent.query.get_or_404(student_id)
    
    if student.event_id != event_id:
        flash('Student not found in this event.', 'error')
        return redirect(url_for('events.view_event', id=event_id))
    
    form = BeginnersStudentForm(obj=student)
    
    if form.validate_on_submit():
        form.populate_obj(student)
        student.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Student {student.name} updated successfully!', 'success')
        return redirect(url_for('events.view_event', id=event_id))
    
    return render_template('events/edit_beginners_student.html', 
                         form=form, event=event, student=student)


@events_bp.route('/events/<int:event_id>/beginners/<int:student_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_beginners_student(event_id, student_id):
    """Delete a beginners course student"""
    student = BeginnersStudent.query.get_or_404(student_id)
    
    if student.event_id != event_id:
        flash('Student not found in this event.', 'error')
        return redirect(url_for('events.view_event', id=event_id))
    
    student_name = student.name
    db.session.delete(student)
    db.session.commit()
    
    flash(f'Student {student_name} removed from course.', 'success')
    return redirect(url_for('events.view_event', id=event_id))
