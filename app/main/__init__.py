from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import InventoryItem, InventoryCategory, ShootingEvent
from datetime import datetime, timedelta

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
