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
    
    # Get available clubs for dropdown
    all_clubs = Club.query.filter_by(is_active=True).order_by(Club.name).all()
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            # Get club ID from form
            club_id = request.form.get('club_id', type=int)
            
            if not club_id:
                flash('Please select a club.', 'error')
                return render_template('auth/login.html', form=form, clubs=all_clubs)
            
            # Verify user is member of selected club
            membership = ClubMembership.query.filter_by(
                user_id=user.id, 
                club_id=club_id,
                is_active=True
            ).first()
            
            if not membership:
                flash('You are not a member of the selected club.', 'error')
                return render_template('auth/login.html', form=form, clubs=all_clubs)
            
            # Login and set club in session (locked for this session)
            login_user(user)
            set_current_club(club_id)
            
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        
        flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html', form=form, clubs=all_clubs)

# Club switching removed - users must logout to change clubs

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Get all active clubs
    all_clubs = Club.query.filter_by(is_active=True).order_by(Club.name).all()
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Get club selection from form
        club_id = request.form.get('club_id', type=int)
        
        if not club_id:
            flash('Please select a club to join.', 'error')
            return render_template('auth/register.html', form=form, clubs=all_clubs)
        
        club = Club.query.get(club_id)
        if not club or not club.is_active:
            flash('Selected club is not available.', 'error')
            return render_template('auth/register.html', form=form, clubs=all_clubs)
        
        # Check if user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html', form=form, clubs=all_clubs)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html', form=form, clubs=all_clubs)

        # If an activation code is configured for this club, require it to match
        required_code = (club.activation_code or '').strip()
        provided_code = (form.activation_code.data or '').strip()
        if required_code:
            if not provided_code:
                flash('Activation code is required to join this club.', 'error')
                return render_template('auth/register.html', form=form, clubs=all_clubs)
            if provided_code != required_code:
                flash('Invalid activation code. Please check with your club administrator.', 'error')
                return render_template('auth/register.html', form=form, clubs=all_clubs)
        
        try:
            # Create new user
            user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.flush()  # Get user.id
            
            # Create club membership
            membership = ClubMembership(
                user_id=user.id,
                club_id=club_id,
                role='member',  # New registrations are members by default
                is_active=True
            )
            db.session.add(membership)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            return render_template('auth/register.html', form=form, clubs=all_clubs)
    
    return render_template('auth/register.html', form=form, clubs=all_clubs)

@auth_bp.route('/logout')
@login_required
def logout():
    clear_current_club()
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/select-club', methods=['GET', 'POST'])
@login_required
def select_club():
    """Allow user to select which club to access"""
    # Get clubs user is a member of
    user_memberships = ClubMembership.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    clubs = [m.club for m in user_memberships if m.club.is_active]
    
    if request.method == 'POST':
        club_id = request.form.get('club_id', type=int)
        
        if not club_id:
            flash('Please select a club.', 'error')
            return render_template('auth/select_club.html', clubs=clubs)
        
        # Verify user is member of selected club
        membership = ClubMembership.query.filter_by(
            user_id=current_user.id,
            club_id=club_id,
            is_active=True
        ).first()
        
        if not membership:
            flash('You are not a member of the selected club.', 'error')
            return render_template('auth/select_club.html', clubs=clubs)
        
        # Set club in session
        set_current_club(club_id)
        flash(f'Now viewing {membership.club.name}', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/select_club.html', clubs=clubs)


@auth_bp.route('/register-club', methods=['GET', 'POST'])
def register_club():
    """Register a new club in the multi-tenant system"""
    from app.forms import ClubRegistrationForm
    
    if current_user.is_authenticated:
        flash('Please logout to register a new club.', 'info')
        return redirect(url_for('main.index'))
    
    form = ClubRegistrationForm()
    
    if form.validate_on_submit():
        # Check if club name or slug already exists
        if Club.query.filter_by(name=form.club_name.data).first():
            flash('Club name already exists.', 'error')
            return render_template('auth/register_club.html', form=form)
        
        # Generate slug from club name if not provided
        slug = form.club_slug.data or form.club_name.data.lower().replace(' ', '-')
        
        if Club.query.filter_by(slug=slug).first():
            flash('Club URL slug already exists.', 'error')
            return render_template('auth/register_club.html', form=form)
        
        # Check if admin user already exists
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register_club.html', form=form)
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register_club.html', form=form)
        
        try:
            # Create the club
            club = Club(
                name=form.club_name.data,
                slug=slug,
                description=form.club_description.data,
                email=form.club_email.data,
                is_active=True
            )
            db.session.add(club)
            db.session.flush()  # Get club.id
            
            # Create admin user
            admin_user = User(
                username=form.username.data,
                email=form.email.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            admin_user.set_password(form.password.data)
            db.session.add(admin_user)
            db.session.flush()  # Get user.id
            
            # Create admin membership
            membership = ClubMembership(
                user_id=admin_user.id,
                club_id=club.id,
                role='admin',
                is_active=True
            )
            db.session.add(membership)
            
            db.session.commit()
            
            flash(f'Club "{club.name}" registered successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating club: {str(e)}', 'error')
            return render_template('auth/register_club.html', form=form)
    
    return render_template('auth/register_club.html', form=form)
