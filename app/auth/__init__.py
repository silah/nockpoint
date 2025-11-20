from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, ClubSettings, Club, ClubMembership
from app.forms import LoginForm, RegistrationForm
from app.club_utils import set_current_club, clear_current_club

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Check clubs user belongs to
            clubs = user.get_clubs()
            
            if not clubs:
                flash('You are not a member of any clubs. Please contact an administrator.', 'warning')
                logout_user()
                return redirect(url_for('auth.login'))
            elif len(clubs) == 1:
                # Auto-select the only club
                set_current_club(clubs[0].id)
                flash('Login successful!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                # Multiple clubs, redirect to selection
                flash('Login successful! Please select a club.', 'success')
                return redirect(url_for('auth.select_club'))
        
        flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/select-club', methods=['GET', 'POST'])
@login_required
def select_club():
    """Allow user to select which club to access"""
    clubs = current_user.get_clubs()
    
    if not clubs:
        flash('You are not a member of any clubs.', 'warning')
        logout_user()
        return redirect(url_for('auth.login'))
    
    if len(clubs) == 1:
        # Only one club, auto-select it
        set_current_club(clubs[0].id)
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        club_id = request.form.get('club_id', type=int)
        if club_id:
            # Verify user has access
            if current_user.is_member_of_club(club_id):
                set_current_club(club_id)
                flash('Club selected successfully!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        flash('Invalid club selection.', 'error')
    
    return render_template('auth/select_club.html', clubs=clubs)

@auth_bp.route('/switch-club/<int:club_id>')
@login_required
def switch_club(club_id):
    """Quick club switching"""
    if current_user.is_member_of_club(club_id):
        set_current_club(club_id)
        flash('Switched club successfully!', 'success')
    else:
        flash('Access denied to this club.', 'error')
    
    return redirect(request.referrer or url_for('main.dashboard'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    settings = ClubSettings.get_settings()
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html', form=form, settings=settings)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html', form=form, settings=settings)

        # If an activation code is configured, require it to match
        required_code = (settings.activation_code or '').strip()
        provided_code = (form.activation_code.data or '').strip()
        if required_code:
            if not provided_code:
                flash('Activation code is required to register.', 'error')
                return render_template('auth/register.html', form=form, settings=settings)
            if provided_code != required_code:
                flash('Invalid activation code. Please check with your club administrator.', 'error')
                return render_template('auth/register.html', form=form, settings=settings)
        
        # Create new user
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form, settings=settings)

@auth_bp.route('/logout')
@login_required
def logout():
    clear_current_club()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))
