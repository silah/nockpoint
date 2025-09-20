from flask import request, jsonify
from werkzeug.security import check_password_hash
from app.api import api_bp
from app.api.utils import generate_token
from app.models import User


@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user authentication."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': 'Username and password are required'}), 400
            
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': 'Invalid credentials'}), 401
            
        # Generate JWT token
        token = generate_token(user)
        
        return jsonify({
            'token': token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin()
            },
            'expires_in': 30 * 24 * 60 * 60  # 30 days in seconds
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500


@api_bp.route('/auth/verify', methods=['GET'])
def api_verify_token():
    """API endpoint to verify if a token is still valid."""
    from app.api.utils import token_required, get_current_api_user
    
    @token_required
    def verify():
        user = get_current_api_user()
        return jsonify({
            'valid': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin()
            }
        }), 200
    
    return verify()