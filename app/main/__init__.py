from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import InventoryItem, InventoryCategory, ShootingEvent
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
