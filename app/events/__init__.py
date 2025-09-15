from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import ShootingEvent, EventAttendance, MemberCharge, User
from app.forms import ShootingEventForm, AttendanceForm, PaymentUpdateForm
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
    form = ShootingEventForm()
    
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
                price=form.price.data,
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

@events_bp.route('/event/<int:id>')
@login_required
def view_event(id):
    """View shooting event details"""
    event = ShootingEvent.query.get_or_404(id)
    
    # Get attendance list
    attendances = EventAttendance.query.filter_by(event_id=id).join(User).order_by(User.first_name, User.last_name).all()
    
    return render_template('events/view_event.html', event=event, attendances=attendances)

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
    
    if form.validate_on_submit():
        try:
            start_time_obj = datetime.strptime(form.start_time.data, '%H:%M').time()
            
            event.name = form.name.data
            event.description = form.description.data
            event.location = form.location.data
            event.date = form.date.data
            event.start_time = start_time_obj
            event.duration_hours = form.duration_hours.data
            event.price = form.price.data
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
            
            # Create charge for the member if event has a price
            if event.price > 0:
                member = User.query.get(form.member_id.data)
                charge = MemberCharge(
                    member_id=member.id,
                    event_id=event.id,
                    description=f'Shooting event: {event.name} on {event.date.strftime("%Y-%m-%d")}',
                    amount=event.price
                )
                db.session.add(charge)
            
            db.session.commit()
            
            member = User.query.get(form.member_id.data)
            flash(f'Attendance recorded for {member.first_name} {member.last_name}', 'success')
            
            # Reset form
            form.member_id.data = ''
            form.notes.data = ''
    
    # Get current attendances
    attendances = EventAttendance.query.filter_by(event_id=id).join(User).order_by(User.first_name, User.last_name).all()
    
    return render_template('events/manage_attendance.html', event=event, form=form, attendances=attendances)

@events_bp.route('/payments')
@login_required
@admin_required
def outstanding_payments():
    """Show outstanding payments admin page"""
    # Get all unpaid charges
    unpaid_charges = MemberCharge.query.filter_by(is_paid=False).join(User).order_by(
        MemberCharge.charge_date.desc()
    ).all()
    
    # Calculate total outstanding
    total_outstanding = sum(charge.amount for charge in unpaid_charges)
    
    return render_template('events/outstanding_payments.html', 
                         unpaid_charges=unpaid_charges,
                         total_outstanding=total_outstanding)

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
    
    # Calculate outstanding amount
    total_outstanding = sum(charge.amount for charge in outstanding_charges)
    
    return render_template('events/my_charges.html', 
                         charges=charges,
                         my_charges=charges,  # Template uses both 'charges' and 'my_charges'
                         outstanding_charges=outstanding_charges,
                         paid_charges=paid_charges,
                         total_outstanding=total_outstanding)

@events_bp.route('/event/<int:event_id>/add-attendee', methods=['POST'])
@login_required
@admin_required
def add_attendee(event_id):
    """Add an attendee to an event"""
    event = ShootingEvent.query.get_or_404(event_id)
    
    member_id = request.form.get('member_id', type=int)
    mark_attended = request.form.get('mark_attended') == '1'
    
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
        
        # Create charge if event is paid and member attended
        if mark_attended and event.price > 0:
            member = User.query.get(member_id)
            charge = MemberCharge(
                member_id=member.id,
                event_id=event.id,
                description=f"Charge for {event.name}",
                amount=event.price,
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
        
        # Create charge if attending and event is paid
        event = ShootingEvent.query.get(id)
        if attended and event.price > 0:
            existing_charge = MemberCharge.query.filter_by(
                member_id=attendee_id, event_id=id
            ).first()
            
            if not existing_charge:
                charge = MemberCharge(
                    member_id=attendee_id,
                    event_id=id,
                    description=f"Charge for {event.name}",
                    amount=event.price,
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
