from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import InventoryItem, InventoryCategory, ShootingEvent, ClubSettings
from datetime import datetime, timedelta
from app.forms import ClubSettingsForm

main_bp = Blueprint('main', __name__)

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


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False) and not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return wrapper


@main_bp.route('/settings')
@login_required
@admin_required
def settings():
    settings = ClubSettings.get_settings()
    return render_template('main/settings.html', settings=settings)


@main_bp.route('/settings/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_settings():
    settings = ClubSettings.get_settings()
    form = ClubSettingsForm(obj=settings)
    if form.validate_on_submit():
        form.populate_obj(settings)
        settings.updated_by = current_user.id
        settings.updated_at = datetime.utcnow()
        from app import db
        db.session.commit()
        flash('Club settings updated successfully!', 'success')
        return redirect(url_for('main.settings'))

    return render_template('main/settings_form.html', form=form, settings=settings)
