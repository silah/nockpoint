from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import InventoryItem, InventoryCategory, ShootingEvent, MemberCharge, EventAttendance
from datetime import datetime, timedelta
from app.forms import ClubSettingsForm
from app.models import ClubSettings
from app import db
from flask import flash, redirect, url_for, request

main_bp = Blueprint('main', __name__)

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need administrator privileges to access this page.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Redirect members to their member dashboard, admins see admin dashboard
    if current_user.is_admin():
        return admin_dashboard()
    else:
        return member_dashboard()

def admin_dashboard():
    """Admin dashboard with system overview"""
    # Get inventory statistics
    total_items = InventoryItem.query.count()
    total_categories = InventoryCategory.query.count()
    
    # Get member statistics
    from app.models import User
    total_members = User.query.count()
    active_members = User.query.filter_by(is_active=True).count()
    
    # Get recent items
    recent_items = InventoryItem.query.order_by(InventoryItem.created_at.desc()).limit(5).all()
    
    # Get upcoming events count (next 30 days)
    thirty_days_from_now = datetime.now().date() + timedelta(days=30)
    upcoming_events_count = ShootingEvent.query.filter(
        ShootingEvent.date >= datetime.now().date(),
        ShootingEvent.date <= thirty_days_from_now
    ).count()
    
    return render_template('dashboard.html', 
                         total_items=total_items,
                         total_categories=total_categories,
                         total_members=total_members,
                         active_members=active_members,
                         recent_items=recent_items,
                         upcoming_events_count=upcoming_events_count)

def member_dashboard():
    """Member dashboard with personal events and payments"""
    # Get outstanding payments
    outstanding_charges = MemberCharge.query.filter_by(
        member_id=current_user.id,
        is_paid=False
    ).order_by(MemberCharge.charge_date.desc()).all()
    
    total_outstanding = sum(float(charge.amount) for charge in outstanding_charges)
    
    # Get upcoming events (next 60 days) that user is registered for OR can register for
    today = datetime.now().date()
    sixty_days_from_now = today + timedelta(days=60)
    
    # Events user is registered for
    registered_event_ids = [ea.event_id for ea in EventAttendance.query.filter_by(member_id=current_user.id).all()]
    
    registered_upcoming_events = ShootingEvent.query.filter(
        ShootingEvent.id.in_(registered_event_ids),
        ShootingEvent.date >= today,
        ShootingEvent.date <= sixty_days_from_now
    ).order_by(ShootingEvent.date, ShootingEvent.start_time).all()
    
    # Available upcoming events (not registered for, with space available)
    available_upcoming_events = ShootingEvent.query.filter(
        ~ShootingEvent.id.in_(registered_event_ids),
        ShootingEvent.date >= today,
        ShootingEvent.date <= sixty_days_from_now
    ).order_by(ShootingEvent.date, ShootingEvent.start_time).limit(10).all()
    
    # Filter available events by capacity if they have max_participants set
    available_events_filtered = []
    for event in available_upcoming_events:
        if event.max_participants is None or event.attendance_count < event.max_participants:
            available_events_filtered.append(event)
    
    # Get recent past events user participated in (last 90 days)
    ninety_days_ago = today - timedelta(days=90)
    
    recent_past_attendances = EventAttendance.query.join(ShootingEvent).filter(
        EventAttendance.member_id == current_user.id,
        ShootingEvent.date >= ninety_days_ago,
        ShootingEvent.date < today
    ).order_by(ShootingEvent.date.desc()).limit(10).all()
    
    return render_template('member_dashboard.html',
                         outstanding_charges=outstanding_charges,
                         total_outstanding=total_outstanding,
                         registered_upcoming_events=registered_upcoming_events,
                         available_upcoming_events=available_events_filtered[:5],  # Limit to 5
                         recent_past_attendances=recent_past_attendances)

@main_bp.route('/settings')
@login_required
@admin_required
def settings():
    """Display club settings page"""
    settings = ClubSettings.get_settings()
    return render_template('main/settings.html', settings=settings)

@main_bp.route('/settings/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_settings():
    """Edit club settings"""
    settings = ClubSettings.get_settings()
    form = ClubSettingsForm(obj=settings)
    
    if form.validate_on_submit():
        # Update settings from form
        form.populate_obj(settings)
        settings.updated_by = current_user.id
        settings.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Club settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))
    
    return render_template('main/settings_form.html', form=form, settings=settings)


@main_bp.route('/health')
def health_check():
    """Health check endpoint for Docker"""
    return {'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()}, 200
