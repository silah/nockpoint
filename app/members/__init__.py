from flask import Blueprint, render_template, redirect, url_for, flash, request, g, make_response
from flask_login import login_required, current_user
from app import db
from app.models import User, ClubMembership
from app.forms import RegistrationForm, MemberEditForm, CSVImportForm
from app.decorators import require_club_context, require_club_admin, require_club_member
from datetime import datetime
import csv
import io
import secrets
import string

members_bp = Blueprint('members', __name__)

@members_bp.route('/')
@login_required
@require_club_context
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    status_filter = request.args.get('status', '')
    
    # Get memberships for current club
    query = ClubMembership.query.filter_by(club_id=g.current_club.id).join(User)
    
    if search:
        query = query.filter(
            User.username.contains(search) | 
            User.email.contains(search) |
            User.first_name.contains(search) |
            User.last_name.contains(search)
        )
    
    if role_filter:
        query = query.filter(ClubMembership.role == role_filter)
    
    if status_filter == 'active':
        query = query.filter(ClubMembership.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(ClubMembership.is_active == False)
    
    memberships = query.order_by(User.last_name, User.first_name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Get stats for dashboard cards - scoped to current club
    total_members = ClubMembership.query.filter_by(club_id=g.current_club.id).count()
    active_members = ClubMembership.query.filter_by(club_id=g.current_club.id, is_active=True).count()
    admins = ClubMembership.query.filter_by(club_id=g.current_club.id, role='admin').count()
    
    return render_template('members/index.html', 
                         members=memberships,
                         search=search,
                         role_filter=role_filter,
                         status_filter=status_filter,
                         total_members=total_members,
                         active_members=active_members,
                         admins=admins)

@members_bp.route('/new', methods=['GET', 'POST'])
@login_required
@require_club_admin
def new_member():
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            # User exists - check if already a member of current club
            existing_membership = ClubMembership.query.filter_by(
                user_id=existing_user.id,
                club_id=g.current_club.id
            ).first()
            
            if existing_membership:
                flash('User is already a member of this club.', 'error')
                return render_template('members/member_form.html', form=form, title='New Member')
            else:
                # Add existing user to current club
                membership = ClubMembership(
                    user_id=existing_user.id,
                    club_id=g.current_club.id,
                    role='admin' if form.is_admin.data else 'member',
                    is_active=True
                )
                db.session.add(membership)
                db.session.commit()
                
                flash(f'User {existing_user.username} added to club!', 'success')
                return redirect(url_for('members.view_member', id=existing_user.id))
        
        # Check if email is already registered
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered.', 'error')
            return render_template('members/member_form.html', form=form, title='New Member')
        
        # Create new user and add to current club
        member = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data
        )
        member.set_password(form.password.data)
        
        db.session.add(member)
        db.session.flush()  # Get member.id
        
        # Create club membership
        membership = ClubMembership(
            user_id=member.id,
            club_id=g.current_club.id,
            role='admin' if form.is_admin.data else 'member',
            is_active=True
        )
        db.session.add(membership)
        db.session.commit()
        
        flash(f'Member {member.username} created successfully!', 'success')
        return redirect(url_for('members.view_member', id=member.id))
    
    return render_template('members/member_form.html', form=form, title='New Member')

@members_bp.route('/member/<int:id>')
@login_required
@require_club_context
def view_member(id):
    member = User.query.get_or_404(id)
    
    # Non-admins can only view their own profile
    is_club_admin = current_user.is_admin_of_club(g.current_club.id) if g.current_club else False
    if not is_club_admin and current_user.id != member.id:
        flash('Access denied.', 'error')
        return redirect(url_for('members.view_member', id=current_user.id))
    
    return render_template('members/view_member.html', member=member)

@members_bp.route('/member/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_club_context
def edit_member(id):
    member = User.query.get_or_404(id)
    
    # Users can edit their own profile, admins can edit any profile
    is_club_admin = current_user.is_admin_of_club(g.current_club.id) if g.current_club else False
    if not is_club_admin and current_user.id != member.id:
        flash('Access denied.', 'error')
        return redirect(url_for('members.view_member', id=current_user.id))
    
    form = MemberEditForm(obj=member)
    
    # Get member's membership in current club
    membership = member.get_membership_in_club(g.current_club.id) if g.current_club else None
    
    # Set checkbox values based on current member data
    if request.method == 'GET':
        form.is_admin.data = (membership.role == 'admin') if membership else False
        form.is_active.data = membership.is_active if membership else False
    
    # Only admins can change roles and status
    if not is_club_admin:
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
        
        # Only admins can update role and status (in the club membership)
        if is_club_admin and membership:
            if hasattr(form, 'is_admin'):
                membership.role = 'admin' if form.is_admin.data else 'member'
            if hasattr(form, 'is_active'):
                membership.is_active = form.is_active.data
        
        # Update password if provided
        if form.password.data:
            member.set_password(form.password.data)
        
        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members.view_member', id=member.id))
    
    return render_template('members/edit_member.html', form=form, member=member)

@members_bp.route('/member/<int:id>/toggle-status', methods=['POST'])
@login_required
@require_club_admin
def toggle_member_status(id):
    member = User.query.get_or_404(id)
    membership = member.get_membership_in_club(g.current_club.id)
    
    if not membership:
        flash('Member not found in current club.', 'error')
        return redirect(url_for('members.index'))
    
    # Prevent deactivating the last admin
    if membership.role == 'admin' and membership.is_active:
        active_admins = ClubMembership.query.filter_by(
            club_id=g.current_club.id,
            role='admin',
            is_active=True
        ).count()
        if active_admins <= 1:
            flash('Cannot deactivate the last active admin.', 'error')
            return redirect(url_for('members.view_member', id=member.id))
    
    membership.is_active = not membership.is_active
    db.session.commit()
    
    status = 'activated' if membership.is_active else 'deactivated'
    flash(f'Member {member.username} has been {status}.', 'success')
    return redirect(url_for('members.view_member', id=member.id))

@members_bp.route('/member/<int:id>/delete', methods=['POST'])
@login_required
@require_club_admin
def delete_member(id):
    member = User.query.get_or_404(id)
    membership = member.get_membership_in_club(g.current_club.id)
    
    if not membership:
        flash('Member not found in current club.', 'error')
        return redirect(url_for('members.index'))
    
    # Prevent deleting the current user
    if member.id == current_user.id:
        flash('You cannot delete your own account.', 'error')
        return redirect(url_for('members.view_member', id=member.id))
    
    # Prevent deleting the last admin
    if membership.role == 'admin':
        active_admins = ClubMembership.query.filter_by(
            club_id=g.current_club.id,
            role='admin',
            is_active=True
        ).count()
        if active_admins <= 1 and membership.is_active:
            flash('Cannot delete the last active admin.', 'error')
            return redirect(url_for('members.view_member', id=member.id))
    
    username = member.username
    # Delete the club membership, not the user
    db.session.delete(membership)
    db.session.commit()
    
    flash(f'Member {username} has been removed from the club.', 'success')
    return redirect(url_for('members.index'))

@members_bp.route('/profile')


@members_bp.route('/import-csv', methods=['GET', 'POST'])
@login_required
@require_club_admin
def import_csv():
    """Import members from CSV file"""
    form = CSVImportForm()
    
    if form.validate_on_submit():
        csv_file = form.csv_file.data
        membership_type = form.membership_type.data
        make_admin = form.make_admin.data
        
        # Read CSV file
        try:
            # Read file content
            stream = io.StringIO(csv_file.stream.read().decode('UTF-8'), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Validate headers
            required_headers = ['email', 'first_name', 'last_name']
            if not all(header in csv_reader.fieldnames for header in required_headers):
                flash(f'CSV must contain headers: {", ".join(required_headers)}', 'error')
                return render_template('members/import_csv.html', form=form)
            
            imported_users = []
            errors = []
            row_num = 1
            
            for row in csv_reader:
                row_num += 1
                
                email = row.get('email', '').strip()
                first_name = row.get('first_name', '').strip()
                last_name = row.get('last_name', '').strip()
                
                # Skip empty rows
                if not email and not first_name and not last_name:
                    continue
                
                # Validate required fields
                if not email or not first_name or not last_name:
                    errors.append(f"Row {row_num}: Missing required fields")
                    continue
                
                # Check if user already exists
                existing_user = User.query.filter_by(email=email).first()
                
                if existing_user:
                    # Check if already a member of this club
                    existing_membership = ClubMembership.query.filter_by(
                        user_id=existing_user.id,
                        club_id=g.current_club.id
                    ).first()
                    
                    if existing_membership:
                        errors.append(f"Row {row_num}: {email} is already a member of this club")
                        continue
                    else:
                        # Add existing user to club
                        membership = ClubMembership(
                            user_id=existing_user.id,
                            club_id=g.current_club.id,
                            role='admin' if make_admin else 'member',
                            membership_type=membership_type,
                            is_active=True
                        )
                        db.session.add(membership)
                        imported_users.append({
                            'email': email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'password': 'EXISTING_USER',
                            'is_new': False
                        })
                else:
                    # Generate random password
                    password = generate_random_password()
                    
                    # Create new user (username = email)
                    user = User(
                        username=email,
                        email=email,
                        first_name=first_name,
                        last_name=last_name
                    )
                    user.set_password(password)
                    
                    db.session.add(user)
                    db.session.flush()  # Get user.id
                    
                    # Create club membership
                    membership = ClubMembership(
                        user_id=user.id,
                        club_id=g.current_club.id,
                        role='admin' if make_admin else 'member',
                        membership_type=membership_type,
                        is_active=True
                    )
                    db.session.add(membership)
                    
                    imported_users.append({
                        'email': email,
                        'first_name': first_name,
                        'last_name': last_name,
                        'password': password,
                        'is_new': True
                    })
            
            # Commit all changes
            db.session.commit()
            
            if imported_users:
                flash(f'Successfully imported {len(imported_users)} member(s)!', 'success')
                return render_template('members/import_results.html', 
                                     imported_users=imported_users,
                                     errors=errors)
            else:
                flash('No members were imported.', 'warning')
                if errors:
                    for error in errors:
                        flash(error, 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing CSV file: {str(e)}', 'error')
            return render_template('members/import_csv.html', form=form)
    
    return render_template('members/import_csv.html', form=form)


@members_bp.route('/download-template')
@login_required
@require_club_admin
def download_template():
    """Download CSV template for member import"""
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['email', 'first_name', 'last_name'])
    
    # Write example row
    writer.writerow(['john.doe@example.com', 'John', 'Doe'])
    writer.writerow(['jane.smith@example.com', 'Jane', 'Smith'])
    
    # Create response
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=member_import_template_{g.current_club.slug}.csv'
    
    return response


def generate_random_password(length=12):
    """Generate a random password with letters, digits, and special characters"""
    # Use a mix of uppercase, lowercase, digits, and some special characters
    characters = string.ascii_letters + string.digits + '@#$%&*'
    
    # Ensure at least one of each type
    password = [
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.digits),
        secrets.choice('@#$%&*')
    ]
    
    # Fill the rest randomly
    password.extend(secrets.choice(characters) for _ in range(length - 4))
    
    # Shuffle to avoid predictable patterns
    password_list = list(password)
    secrets.SystemRandom().shuffle(password_list)
    
    return ''.join(password_list)

@members_bp.route('/profile')
@login_required
def profile():
    """Redirect to current user's profile"""
    return redirect(url_for('members.view_member', id=current_user.id))
