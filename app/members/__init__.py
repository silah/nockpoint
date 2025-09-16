from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User
from app.forms import RegistrationForm, MemberEditForm
from datetime import datetime

members_bp = Blueprint('members', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@members_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    query = User.query
    
    if search:
        query = query.filter(
            User.username.contains(search) | 
            User.email.contains(search) |
            User.first_name.contains(search) |
            User.last_name.contains(search)
        )
    
    if role_filter:
        query = query.filter_by(role=role_filter)
    
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)
    
    members = query.order_by(User.last_name, User.first_name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get stats for dashboard cards
    total_members = User.query.count()
    active_members = User.query.filter_by(is_active=True).count()
    admins = User.query.filter_by(role='admin').count()
    
    return render_template('members/index.html', 
                         members=members,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter,
                         total_members=total_members,
                         active_members=active_members,
                         admins=admins)

@members_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_member():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('members/member_form.html', form=form, title='New Member')
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('members/member_form.html', form=form, title='New Member')
        
        # Create new member
        member = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            membership_type=form.membership_type.data,
            role='admin' if form.is_admin.data else 'member'
        )
        member.set_password(form.password.data)
        
        db.session.add(member)
        db.session.commit()
        
        flash(f'Member {member.username} created successfully!', 'success')
        return redirect(url_for('members.view_member', id=member.id))
    
    return render_template('members/member_form.html', form=form, title='New Member')

@members_bp.route('/member/<int:id>')
@login_required
def view_member(id):
    member = User.query.get_or_404(id)
    
    # Non-admins can only view their own profile
    if not current_user.is_admin() and current_user.id != member.id:
        flash('Access denied.', 'error')
        return redirect(url_for('members.view_member', id=current_user.id))
    
    return render_template('members/view_member.html', member=member)

@members_bp.route('/member/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_member(id):
    member = User.query.get_or_404(id)
    
    # Users can edit their own profile, admins can edit any profile
    if not current_user.is_admin() and current_user.id != member.id:
        flash('Access denied.', 'error')
        return redirect(url_for('members.view_member', id=current_user.id))
    
    form = MemberEditForm(obj=member)
    
    # Set checkbox values based on current member data
    if request.method == 'GET':
        form.is_admin.data = (member.role == 'admin')
        form.is_active.data = member.is_active
    
    # Only admins can change roles and status
    if not current_user.is_admin():
        del form.is_admin
        del form.is_active
    
    if form.validate_on_submit():
        # Check for username/email conflicts (excluding current user)
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user and existing_user.id != member.id:
            flash('Username already exists.', 'error')
            return render_template('members/edit_member.html', form=form, member=member)
        
        existing_email = User.query.filter_by(email=form.email.data).first()
        if existing_email and existing_email.id != member.id:
            flash('Email already registered.', 'error')
            return render_template('members/edit_member.html', form=form, member=member)
        
        # Update member information
        member.username = form.username.data
        member.email = form.email.data
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.membership_type = form.membership_type.data
        
        # Only admins can update role and status
        if current_user.is_admin():
            if hasattr(form, 'is_admin'):
                member.role = 'admin' if form.is_admin.data else 'member'
            if hasattr(form, 'is_active'):
                member.is_active = form.is_active.data
        
        # Update password if provided
        if form.password.data:
            member.set_password(form.password.data)
        
        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members.view_member', id=member.id))
    
    return render_template('members/edit_member.html', form=form, member=member)

@members_bp.route('/member/<int:id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_member_status(id):
    member = User.query.get_or_404(id)
    
    # Prevent deactivating the last admin
    if member.role == 'admin' and member.is_active:
        active_admins = User.query.filter_by(role='admin', is_active=True).count()
        if active_admins <= 1:
            flash('Cannot deactivate the last active admin.', 'error')
            return redirect(url_for('members.view_member', id=member.id))
    
    member.is_active = not member.is_active
    db.session.commit()
    
    status = 'activated' if member.is_active else 'deactivated'
    flash(f'Member {member.username} has been {status}.', 'success')
    return redirect(url_for('members.view_member', id=member.id))

@members_bp.route('/member/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_member(id):
    member = User.query.get_or_404(id)
    
    # Prevent deleting the current user
    if member.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('members.view_member', id=member.id))
    
    # Prevent deleting the last admin
    if member.role == 'admin':
        active_admins = User.query.filter_by(role='admin', is_active=True).count()
        if active_admins <= 1 and member.is_active:
            flash('Cannot delete the last active admin.', 'error')
            return redirect(url_for('members.view_member', id=member.id))
    
    username = member.username
    db.session.delete(member)
    db.session.commit()
    
    flash(f'Member {username} has been deleted.', 'success')
    return redirect(url_for('members.index'))

@members_bp.route('/profile')
@login_required
def profile():
    """Redirect to current user's profile"""
    return redirect(url_for('members.view_member', id=current_user.id))
