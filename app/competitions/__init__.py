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
    
    return render_template('competitions/view.html',
                         competition=competition,
                         total_participants=total_participants,
                         groups_with_stats=groups_with_stats)

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
        
        # Create teams
        team_size = competition.max_team_size
        num_teams = (len(registrations) + team_size - 1) // team_size  # Ceiling division
        
        for team_num in range(num_teams):
            team = CompetitionTeam(
                group_id=group.id,
                name=f"{group.name} Team {team_num + 1}",
                target_assignment=f"Target {teams_created + team_num + 1}"
            )
            db.session.add(team)
            db.session.flush()  # Get team ID
            
            # Assign members to team
            start_idx = team_num * team_size
            end_idx = min(start_idx + team_size, len(registrations))
            
            for i in range(start_idx, end_idx):
                registrations[i].team_id = team.id
        
        teams_created += num_teams
    
    db.session.commit()
    flash(f'Successfully generated {teams_created} teams.', 'success')
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
    
    return render_template('competitions/scoring.html',
                         competition=competition,
                         registrations_with_scores=registrations_with_scores)

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
    
    form = BulkArrowScoreForm(arrows_per_round=competition.arrows_per_round)
    form.round_number.data = current_round
    
    if form.validate_on_submit():
        # Record scores for this round
        base_arrow_number = (current_round - 1) * competition.arrows_per_round
        
        for i in range(competition.arrows_per_round):
            arrow_field = getattr(form, f'arrow_{i+1}')
            is_x_field = getattr(form, f'is_x_{i+1}')
            
            arrow_score = ArrowScore(
                registration_id=registration.id,
                arrow_number=base_arrow_number + i + 1,
                points=arrow_field.data,
                is_x=is_x_field.data,
                round_number=current_round,
                recorded_by=current_user.id
            )
            db.session.add(arrow_score)
        
        db.session.commit()
        
        flash(f'Round {current_round} scored successfully for {registration.member.first_name} {registration.member.last_name}!', 'success')
        return redirect(url_for('competitions.scoring', id=id))
    
    return render_template('competitions/score_registration.html',
                         competition=competition,
                         registration=registration,
                         form=form,
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
    """Complete the competition"""
    competition = Competition.query.get_or_404(id)
    
    if competition.status != 'in_progress':
        flash('Only competitions in progress can be completed.', 'error')
        return redirect(url_for('competitions.view_competition', id=id))
    
    competition.status = 'completed'
    db.session.commit()
    
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
