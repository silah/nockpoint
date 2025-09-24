from flask import request, jsonify
from datetime import datetime
from app.api import api_bp
from app.api.utils import token_required, get_current_api_user
from app.models import Competition, CompetitionRegistration, ArrowScore, ShootingEvent, db


@api_bp.route('/competitions', methods=['GET'])
@token_required
def api_list_competitions():
    """API endpoint to list all competitions."""
    try:
        user = get_current_api_user()
        
        # Get query parameters for filtering
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        
        # Start with base query joining with ShootingEvent
        query = Competition.query.join(ShootingEvent)
        
        if upcoming_only:
            query = query.filter(ShootingEvent.date >= datetime.now().date())
            
        # Order by start date
        competitions = query.order_by(ShootingEvent.date).all()
        
        # Format competitions for API response
        competitions_data = []
        for comp in competitions:
            # Check if user is registered
            registration = CompetitionRegistration.query.filter_by(
                competition_id=comp.id,
                member_id=user.id
            ).first()
            
            comp_data = {
                'id': comp.id,
                'name': comp.event.name,  # Get name from linked event
                'description': comp.event.description,  # Get description from linked event
                'start_date': comp.event.date.isoformat(),
                'end_date': comp.event.date.isoformat(),  # Single day event
                'location': comp.event.location,
                'competition_type': 'archery',  # Fixed type for now
                'status': comp.status,
                'max_participants': comp.event.max_participants,
                'registration_deadline': None,  # Not implemented in model
                'user_registered': registration is not None,
                'user_can_submit_scores': (
                    registration is not None and 
                    comp.status in ['registration_open', 'in_progress'] and
                    comp.event.date <= datetime.now().date()
                )
            }
            competitions_data.append(comp_data)
        
        return jsonify({
            'competitions': competitions_data,
            'total': len(competitions_data)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/competitions/<int:competition_id>', methods=['GET'])
@token_required
def api_get_competition(competition_id):
    """API endpoint to get details of a specific competition."""
    try:
        user = get_current_api_user()
        
        competition = Competition.query.get_or_404(competition_id)
        
        # Check if user is registered
        registration = CompetitionRegistration.query.filter_by(
            competition_id=competition.id,
            member_id=user.id
        ).first()
        
        # Get user's scores if registered
        user_scores = []
        if registration:
            scores = ArrowScore.query.filter_by(
                registration_id=registration.id
            ).order_by(ArrowScore.round_number, ArrowScore.arrow_number).all()
            
            for score in scores:
                user_scores.append({
                    'id': score.id,
                    'round_number': score.round_number,
                    'arrow_number': score.arrow_number,
                    'score': score.points,
                    'is_x': score.is_x
                })
        
        # Get groups if any
        groups = []
        for group in competition.groups:
            groups.append({
                'id': group.id,
                'name': group.name,
                'description': group.description
            })
        
        comp_data = {
            'id': competition.id,
            'name': competition.event.name,
            'description': competition.event.description,
            'start_date': competition.event.date.isoformat(),
            'end_date': competition.event.date.isoformat(),  # Single day event
            'location': competition.event.location,
            'competition_type': 'archery',  # Fixed type
            'status': competition.status,
            'max_participants': competition.event.max_participants,
            'rounds': competition.number_of_rounds,
            'arrows_per_round': competition.arrows_per_round,
            'scoring_type': 'points',  # Assuming points scoring
            'registration_deadline': None,  # Not implemented
            'user_registered': registration is not None,
            'user_can_submit_scores': (
                registration is not None and 
                competition.status in ['registration_open', 'in_progress'] and
                competition.event.date <= datetime.now().date()
            ),
            'user_scores': user_scores,
            'groups': groups
        }
        
        return jsonify(comp_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/competitions/<int:competition_id>/scores', methods=['POST'])
@token_required
def api_submit_score(competition_id):
    """API endpoint to submit scores for a competition."""
    try:
        user = get_current_api_user()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        competition = Competition.query.get_or_404(competition_id)
        
        # Check if competition allows score submission
        if competition.status not in ['registration_open', 'in_progress']:
            return jsonify({'error': 'Competition is not accepting scores'}), 400
            
        if competition.event.date > datetime.now().date():
            return jsonify({'error': 'Competition has not started yet'}), 400
        
        # Check if user is registered
        registration = CompetitionRegistration.query.filter_by(
            competition_id=competition_id,
            member_id=user.id
        ).first()
        
        if not registration:
            return jsonify({'error': 'Not registered for this competition'}), 400
        
        # Validate required fields
        required_fields = ['round_number', 'arrow_number', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        round_number = data['round_number']
        arrow_number = data['arrow_number']
        score = data['score']
        is_x = data.get('is_x', False)
        
        # Validate ranges
        if round_number < 1 or round_number > competition.number_of_rounds:
            return jsonify({'error': f'Round number must be between 1 and {competition.number_of_rounds}'}), 400
            
        if arrow_number < 1 or arrow_number > competition.arrows_per_round:
            return jsonify({'error': f'Arrow number must be between 1 and {competition.arrows_per_round}'}), 400
        
        # Validate score based on scoring type (assuming points for now)
        if score < 0 or score > 10:
            return jsonify({'error': 'Score must be between 0 and 10'}), 400
        
        # Check if score already exists for this arrow
        existing_score = ArrowScore.query.filter_by(
            registration_id=registration.id,
            round_number=round_number,
            arrow_number=arrow_number
        ).first()
        
        if existing_score:
            # Update existing score
            existing_score.points = score
            existing_score.is_x = is_x
        else:
            # Create new score
            arrow_score = ArrowScore(
                registration_id=registration.id,
                round_number=round_number,
                arrow_number=arrow_number,
                points=score,
                is_x=is_x,
                recorded_by=user.id
            )
            db.session.add(arrow_score)
        
        db.session.commit()
        
        # Calculate total score for response
        total_score = db.session.query(db.func.sum(ArrowScore.points)).filter_by(
            registration_id=registration.id
        ).scalar() or 0
        
        return jsonify({
            'message': 'Score submitted successfully',
            'round_number': round_number,
            'arrow_number': arrow_number,
            'score': score,
            'is_x': is_x,
            'total_score': total_score
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/competitions/<int:competition_id>/scores/batch', methods=['POST'])
@token_required
def api_submit_scores_batch(competition_id):
    """API endpoint to submit multiple scores at once."""
    try:
        user = get_current_api_user()
        data = request.get_json()
        
        if not data or 'scores' not in data:
            return jsonify({'error': 'No scores data provided'}), 400
        
        competition = Competition.query.get_or_404(competition_id)
        
        # Check if competition allows score submission
        if competition.status not in ['registration_open', 'in_progress']:
            return jsonify({'error': 'Competition is not accepting scores'}), 400
            
        if competition.event.date > datetime.now().date():
            return jsonify({'error': 'Competition has not started yet'}), 400
        
        # Check if user is registered
        registration = CompetitionRegistration.query.filter_by(
            competition_id=competition_id,
            member_id=user.id
        ).first()
        
        if not registration:
            return jsonify({'error': 'Not registered for this competition'}), 400
        
        scores_data = data['scores']
        if not isinstance(scores_data, list):
            return jsonify({'error': 'Scores must be an array'}), 400
        
        submitted_scores = []
        
        # Process each score
        for score_data in scores_data:
            # Validate required fields
            required_fields = ['round_number', 'arrow_number', 'score']
            for field in required_fields:
                if field not in score_data:
                    return jsonify({'error': f'Missing required field: {field} in score entry'}), 400
            
            round_number = score_data['round_number']
            arrow_number = score_data['arrow_number']
            score = score_data['score']
            is_x = score_data.get('is_x', False)
            
            # Validate ranges
            if round_number < 1 or round_number > competition.number_of_rounds:
                return jsonify({'error': f'Round number must be between 1 and {competition.number_of_rounds}'}), 400
                
            if arrow_number < 1 or arrow_number > competition.arrows_per_round:
                return jsonify({'error': f'Arrow number must be between 1 and {competition.arrows_per_round}'}), 400
            
            # Validate score based on scoring type (assuming points for now)
            if score < 0 or score > 10:
                return jsonify({'error': 'Score must be between 0 and 10'}), 400
            
            # Check if score already exists for this arrow
            existing_score = ArrowScore.query.filter_by(
                registration_id=registration.id,
                round_number=round_number,
                arrow_number=arrow_number
            ).first()
            
            if existing_score:
                # Update existing score
                existing_score.points = score
                existing_score.is_x = is_x
            else:
                # Create new score
                arrow_score = ArrowScore(
                    registration_id=registration.id,
                    round_number=round_number,
                    arrow_number=arrow_number,
                    points=score,
                    is_x=is_x,
                    recorded_by=user.id
                )
                db.session.add(arrow_score)
            
            submitted_scores.append({
                'round_number': round_number,
                'arrow_number': arrow_number,
                'score': score,
                'is_x': is_x
            })
        
        db.session.commit()
        
        # Calculate total score for response
        total_score = db.session.query(db.func.sum(ArrowScore.points)).filter_by(
            registration_id=registration.id
        ).scalar() or 0
        
        return jsonify({
            'message': f'Successfully submitted {len(submitted_scores)} scores',
            'submitted_scores': submitted_scores,
            'total_score': total_score
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500