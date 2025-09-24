from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import (ShootingEvent, Competition, CompetitionGroup, CompetitionTeam, 
                       CompetitionRegistration, ArrowScore, User)
from app.forms import (CompetitionForm, CompetitionGroupForm, CompetitionRegistrationForm, 
                      ArrowScoreForm, BulkArrowScoreForm, TeamAssignmentForm)
from datetime import datetime, date, timedelta
from sqlalchemy import desc, func
import math
import random

competitions_bp = Blueprint('competitions', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@competitions_bp.route('/')
@login_required
def index():
    """List all competitions"""
    # Get upcoming competitions (within next 60 days)
    today = date.today()
    future_date = today + timedelta(days=60)
    
    upcoming_competitions = db.session.query(Competition).join(ShootingEvent).filter(
        ShootingEvent.date >= today,
        ShootingEvent.date <= future_date
    ).order_by(ShootingEvent.date, ShootingEvent.start_time).all()
    
    # Get past competitions
    past_competitions = db.session.query(Competition).join(ShootingEvent).filter(
        ShootingEvent.date < today
    ).order_by(desc(ShootingEvent.date)).limit(10).all()
    
    # Get upcoming events without competitions (for admin dropdown)
    upcoming_events = []
    if current_user.is_admin():
        existing_competition_events = [c.event_id for c in upcoming_competitions]
        upcoming_events = ShootingEvent.query.filter(
            ShootingEvent.date >= today,
            ShootingEvent.date <= future_date,
            ~ShootingEvent.id.in_(existing_competition_events)
        ).order_by(ShootingEvent.date, ShootingEvent.start_time).all()
    
    return render_template('competitions/index.html',
                         upcoming_competitions=upcoming_competitions,
                         past_competitions=past_competitions,
                         upcoming_events=upcoming_events)

@competitions_bp.route('/event/<int:event_id>/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_competition(event_id):
    """Create a competition for an existing event"""
    event = ShootingEvent.query.get_or_404(event_id)
    
    # Check if competition already exists for this event
    existing_competition = Competition.query.filter_by(event_id=event_id).first()
    if existing_competition:
        flash('A competition already exists for this event.', 'error')
        return redirect(url_for('competitions.view_competition', id=existing_competition.id))
    
    form = CompetitionForm()
    
    if form.validate_on_submit():
        competition = Competition(
            event_id=event_id,
            number_of_rounds=form.number_of_rounds.data,
            target_size_cm=form.target_size_cm.data,
            arrows_per_round=form.arrows_per_round.data,
            max_team_size=form.max_team_size.data,
            created_by=current_user.id,
            status='setup'
        )
        
        db.session.add(competition)
        db.session.commit()
        
        flash(f'Competition created for "{event.name}"!', 'success')
        return redirect(url_for('competitions.setup_groups', id=competition.id))
    
    return render_template('competitions/create.html', form=form, event=event)

@competitions_bp.route('/<int:id>')
@login_required
def view_competition(id):
    """View competition details"""
    competition = Competition.query.get_or_404(id)
    
    # Get statistics
    total_participants = len(competition.registrations)
    groups_with_stats = []
    
    for group in competition.groups:
        group_participants = [r for r in competition.registrations if r.group_id == group.id]
        group_teams = group.teams
        
        groups_with_stats.append({
            'group': group,
            'participant_count': len(group_participants),
            'team_count': len(group_teams),
            'participants': group_participants
        })
    
    # Get available users for admin registration (users not already registered)
    available_users = []
    if current_user.is_admin() and competition.status == 'registration_open':
        registered_user_ids = [registration.member_id for registration in competition.registrations]
        available_users = User.query.filter(
            User.is_active == True,
            ~User.id.in_(registered_user_ids)
        ).order_by(User.first_name, User.last_name).all()
    
    # Get inventory status for target faces
    inventory_status = competition.check_target_face_inventory()
    
    return render_template('competitions/view.html',
                         competition=competition,
                         total_participants=total_participants,
                         groups_with_stats=groups_with_stats,
                         available_users=available_users,
                         inventory_status=inventory_status)

@competitions_bp.route('/<int:id>/setup-groups', methods=['GET', 'POST'])
@login_required
@admin_required
def setup_groups(id):
    """Setup competition groups"""
    competition = Competition.query.get_or_404(id)
    form = CompetitionGroupForm()
    
    if form.validate_on_submit():
        group = CompetitionGroup(
            competition_id=id,
            name=form.name.data,
            description=form.description.data,
            min_age=form.min_age.data,
            max_age=form.max_age.data
        )
        
        db.session.add(group)
        db.session.commit()
        
        flash(f'Group "{group.name}" added successfully!', 'success')
        return redirect(url_for('competitions.setup_groups', id=id))
    
    return render_template('competitions/setup_groups.html',
                         competition=competition,
                         form=form)

@competitions_bp.route('/<int:id>/open-registration', methods=['POST'])
@login_required
@admin_required
def open_registration(id):
    """Open registration for the competition"""
    competition = Competition.query.get_or_404(id)
    
    if not competition.groups:
        flash('Please create at least one group before opening registration.', 'error')
        return redirect(url_for('competitions.setup_groups', id=id))
    
    competition.status = 'registration_open'
    db.session.commit()
    
    flash('Registration is now open for participants!', 'success')
    return redirect(url_for('competitions.view_competition', id=id))

@competitions_bp.route('/<int:id>/register', methods=['GET', 'POST'])
@login_required
def register(id):
    """Register current user for competition"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status != 'registration_open':
        flash('Registration is not currently open for this competition.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    # Check if already registered
    existing_registration = CompetitionRegistration.query.filter_by(
        competition_id=id, member_id=current_user.id
    ).first()
    
    if existing_registration:
        flash('You are already registered for this competition.', 'info')
        return redirect(url_for('competitions.view_competition', id=id))
    
    form = CompetitionRegistrationForm(competition_id=id)
    
    if form.validate_on_submit():
        registration = CompetitionRegistration(
            competition_id=id,
            member_id=current_user.id,
            group_id=form.group_id.data,
            notes=form.notes.data
        )
        
        db.session.add(registration)
        db.session.commit()
        
        flash('Successfully registered for the competition!', 'success')
        return redirect(url_for('competitions.view_competition', id=id))
    
    return render_template('competitions/register.html',
                         competition=competition,
                         form=form)

@competitions_bp.route('/<int:id>/admin-register', methods=['POST'])
@login_required
@admin_required
def admin_register_member(id):
    """Admin register a member for competition"""
    competition = Competition.query.get_or_404(id)
    
    member_id = request.form.get('member_id', type=int)
    group_id = request.form.get('group_id', type=int)
    
    if not member_id:
        flash('Please select a member', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    if not group_id:
        flash('Please select a group', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    # Check if already registered
    existing_registration = CompetitionRegistration.query.filter_by(
        competition_id=id, member_id=member_id
    ).first()
    
    if existing_registration:
        flash('Member is already registered for this competition', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    try:
        # Create registration record
        registration = CompetitionRegistration(
            competition_id=id,
            member_id=member_id,
            group_id=group_id,
            notes=f'Registered by admin: {current_user.first_name} {current_user.last_name}'
        )
        
        db.session.add(registration)
        db.session.commit()
        
        member = User.query.get(member_id)
        group = CompetitionGroup.query.get(group_id)
        flash(f'{member.first_name} {member.last_name} has been registered for {group.name} group', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error registering member: {str(e)}', 'error')
    
    return redirect(url_for('competitions.view_competition', id=id))

@competitions_bp.route('/<int:id>/generate-teams', methods=['POST'])
@login_required
@admin_required
def generate_teams(id):
    """Generate teams automatically for competition"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status != 'registration_open':
        flash('Teams can only be generated when registration is open.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    # Delete existing teams
    for group in competition.groups:
        CompetitionTeam.query.filter_by(group_id=group.id).delete()
    
    teams_created = 0
    
    for group in competition.groups:
        # Get registrations for this group
        registrations = CompetitionRegistration.query.filter_by(
            competition_id=id, group_id=group.id
        ).all()
        
        if not registrations:
            continue
            
        # Shuffle for random team assignment
        import random
        random.shuffle(registrations)
        
        # Smart team balancing logic
        team_size = competition.max_team_size
        total_members = len(registrations)
        
        # Calculate optimal team distribution
        if total_members <= team_size:
            # Everyone on one team
            num_teams = 1
        else:
            # Calculate number of full teams and remainder
            full_teams = total_members // team_size
            remainder = total_members % team_size
            
            if remainder == 0:
                # Perfect division
                num_teams = full_teams
            elif remainder == 1:
                # One person left over - redistribute
                # Make one less full team and distribute extras
                if full_teams > 1:
                    num_teams = full_teams
                    # The last team will have (team_size + 1) members
                else:
                    num_teams = 1  # All members in one team
            else:
                # Remainder > 1, create one extra team with remainder members
                num_teams = full_teams + 1
        
        # Create teams with balanced member distribution
        for team_num in range(num_teams):
            team = CompetitionTeam(
                group_id=group.id,
                team_number=team_num + 1,
                target_number=teams_created + team_num + 1
            )
            db.session.add(team)
            db.session.flush()  # Get team ID
            
        # Now assign members to teams with balanced distribution
        members_per_team = [0] * num_teams
        target_per_team = total_members // num_teams
        extra_members = total_members % num_teams
        
        # Calculate how many members each team should get
        for i in range(num_teams):
            members_per_team[i] = target_per_team
            if i < extra_members:  # Distribute extra members to first few teams
                members_per_team[i] += 1
        
        # Get the created teams
        created_teams = CompetitionTeam.query.filter_by(group_id=group.id).order_by(CompetitionTeam.team_number.desc()).limit(num_teams).all()
        created_teams.reverse()  # Get in correct order
        
        # Assign members to teams
        member_index = 0
        for team_idx, team in enumerate(created_teams):
            members_for_this_team = members_per_team[team_idx]
            for _ in range(members_for_this_team):
                if member_index < len(registrations):
                    registrations[member_index].team_id = team.id
                    member_index += 1
        
        teams_created += num_teams
    
    db.session.commit()
    
    # Check target face inventory after teams are created
    inventory_status = competition.check_target_face_inventory()
    
    # Always show the success message first
    flash(f'Successfully generated {teams_created} teams.', 'success')
    
    # Then show inventory warning if needed
    if not inventory_status['has_enough']:
        flash(inventory_status['message'], 'warning')
    
    return redirect(url_for('competitions.view_competition', id=id))

@competitions_bp.route('/<int:id>/start', methods=['POST'])
@login_required
@admin_required
def start_competition(id):
    """Start the competition"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status != 'registration_open':
        flash('Competition can only be started from registration open status.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    # Check if teams exist
    teams_exist = any(group.teams for group in competition.groups)
    if not teams_exist:
        flash('Please generate teams before starting the competition.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    competition.status = 'in_progress'
    db.session.commit()
    
    flash('Competition has been started! Scoring is now available.', 'success')
    return redirect(url_for('competitions.view_competition', id=id))

@competitions_bp.route('/<int:id>/scoring')
@login_required
@admin_required  
def scoring(id):
    """Competition scoring interface for admins"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status not in ['in_progress', 'completed']:
        flash('Competition must be in progress to access scoring.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    # Get all registrations with their current scores
    registrations_with_scores = []
    for registration in competition.registrations:
        round_scores = registration.get_round_scores()
        registrations_with_scores.append({
            'registration': registration,
            'total_score': registration.total_score,
            'round_scores': round_scores,
            'completed_rounds': registration.completed_rounds,
            'is_complete': registration.is_complete
        })
    
    # Get completion statistics
    completion_stats = competition.get_completion_stats()
    
    return render_template('competitions/scoring.html',
                         competition=competition,
                         registrations_with_scores=registrations_with_scores,
                         completion_stats=completion_stats)

@competitions_bp.route('/<int:id>/score/<int:registration_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def score_registration(id, registration_id):
    """Score a specific registration"""
    competition = Competition.query.get_or_404(id)
    registration = CompetitionRegistration.query.get_or_404(registration_id)
    
    if registration.competition_id != id:
        flash('Invalid registration for this competition.', 'error')
        return redirect(url_for('competitions.scoring', id=id))
    
    # Determine current round
    completed_arrows = len(registration.arrow_scores)
    current_round = (completed_arrows // competition.arrows_per_round) + 1
    
    if current_round > competition.number_of_rounds:
        flash('All rounds completed for this participant.', 'info')
        return redirect(url_for('competitions.scoring', id=id))

    if request.method == 'POST':
        # Basic CSRF token check
        if not request.form.get('csrf_token'):
            flash('Missing CSRF token.', 'error')
            return redirect(url_for('competitions.score_registration', id=id, registration_id=registration_id))
        
        # Validate round number
        submitted_round = request.form.get('round_number')
        if not submitted_round or int(submitted_round) != current_round:
            flash('Invalid round number.', 'error')
            return redirect(url_for('competitions.score_registration', id=id, registration_id=registration_id))
        
        # Record scores for this round
        base_arrow_number = (current_round - 1) * competition.arrows_per_round
        
        # Validate all arrow scores are present and valid
        all_valid = True
        arrow_data = []
        
        for i in range(competition.arrows_per_round):
            arrow_score_str = request.form.get(f'arrow_{i+1}')
            is_x_checked = request.form.get(f'is_x_{i+1}') == 'on'
            
            if not arrow_score_str:
                flash(f'Score for Arrow {i+1} is missing.', 'error')
                all_valid = False
                continue
                
            try:
                arrow_score = int(arrow_score_str)
                if arrow_score < 0 or arrow_score > 10:
                    flash(f'Score for Arrow {i+1} must be between 0 and 10.', 'error')
                    all_valid = False
                    continue
                    
                arrow_data.append({
                    'points': arrow_score,
                    'is_x': is_x_checked,
                    'arrow_number': base_arrow_number + i + 1
                })
            except ValueError:
                flash(f'Invalid score for Arrow {i+1}.', 'error')
                all_valid = False
                continue
        
        if all_valid:
            # Save all arrow scores
            for arrow_info in arrow_data:
                arrow_score = ArrowScore(
                    registration_id=registration.id,
                    arrow_number=arrow_info['arrow_number'],
                    points=arrow_info['points'],
                    is_x=arrow_info['is_x'],
                    round_number=current_round,
                    recorded_by=current_user.id
                )
                db.session.add(arrow_score)
            
            db.session.commit()
            flash(f'Round {current_round} scored successfully for {registration.member.first_name} {registration.member.last_name}!', 'success')
            return redirect(url_for('competitions.scoring', id=id))
        else:
            # If validation failed, stay on the same page to show errors
            return render_template('competitions/score_registration.html',
                                 competition=competition,
                                 registration=registration,
                                 current_round=current_round)
    
    return render_template('competitions/score_registration.html',
                         competition=competition,
                         registration=registration,
                         current_round=current_round)

@competitions_bp.route('/<int:id>/results')
@login_required
def results(id):
    """View competition results"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status == 'setup':
        flash('Competition has not started yet.', 'info')
        return redirect(url_for('competitions.view_competition', id=id))
    
    results_by_group = competition.get_results_by_group()
    
    return render_template('competitions/results.html',
                         competition=competition,
                         results_by_group=results_by_group)

@competitions_bp.route('/<int:id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_competition(id):
    """Complete the competition and fill missing arrows with 0-point scores"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status not in ['in_progress', 'registration_open']:
        flash('Only competitions in progress or with open registration can be completed.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    # Fill missing arrows with 0-point scores for all registrations
    total_arrows_needed = competition.total_arrows
    filled_count = 0
    
    for registration in competition.registrations:
        current_arrows = len(registration.arrow_scores)
        
        if current_arrows < total_arrows_needed:
            # Fill remaining arrows with 0-point scores
            for arrow_num in range(current_arrows + 1, total_arrows_needed + 1):
                round_num = ((arrow_num - 1) // competition.arrows_per_round) + 1
                
                arrow_score = ArrowScore(
                    registration_id=registration.id,
                    arrow_number=arrow_num,
                    points=0,
                    is_x=False,
                    round_number=round_num,
                    recorded_by=current_user.id,
                    notes="Auto-filled on competition completion"
                )
                db.session.add(arrow_score)
                filled_count += 1
    
    # Mark competition as completed
    competition.status = 'completed'
    db.session.commit()
    
    if filled_count > 0:
        flash(f'Competition completed! {filled_count} missing arrows were automatically filled with 0-point scores. Results are now final.', 'success')
    else:
        flash('Competition has been completed! Results are now final.', 'success')
    
    return redirect(url_for('competitions.view_competition', id=id))

@competitions_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_competition(id):
    """Delete a competition"""
    competition = Competition.query.get_or_404(id)
    event_name = competition.event.name
    
    db.session.delete(competition)
    db.session.commit()
    
    flash(f'Competition for "{event_name}" has been deleted.', 'success')
    return redirect(url_for('competitions.index'))

@competitions_bp.route('/group/<int:group_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_group(group_id):
    """Delete a competition group"""
    group = CompetitionGroup.query.get_or_404(group_id)
    competition = group.competition
    
    # Check if group has registrations
    if group.registrations:
        flash(f'Cannot delete group "{group.name}" because it has registered participants.', 'error')
        return redirect(url_for('competitions.setup_groups', id=competition.id))
    
    group_name = group.name
    db.session.delete(group)
    db.session.commit()
    
    flash(f'Group "{group_name}" deleted successfully.', 'success')
    return redirect(url_for('competitions.setup_groups', id=competition.id))
