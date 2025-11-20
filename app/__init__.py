from flask import Flask, g, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config=None):
    # Use instance_relative_config so we can store the SQLite DB under instance/
    app = Flask(__name__, instance_relative_config=True)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    # Default to instance DB unless DATABASE_URL is provided
    default_db_uri = 'sqlite:///' + os.path.join(app.instance_path, 'nockpoint.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', default_db_uri)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if config:
        app.config.update(config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.auth import auth_bp
    from app.main import main_bp
    from app.inventory import inventory_bp
    from app.members import members_bp
    from app.events import events_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(members_bp, url_prefix='/members')
    app.register_blueprint(events_bp, url_prefix='/events')
    
    # Club context middleware
    @app.before_request
    def load_club_context():
        """Load current club into request context"""
        from app.models import Club, ClubMembership
        
        g.current_club = None
        g.current_membership = None
        
        if current_user.is_authenticated:
            club_id = session.get('current_club_id')
            
            if club_id:
                # Load club and verify user has access
                club = Club.query.get(club_id)
                if club and club.is_active:
                    membership = ClubMembership.query.filter_by(
                        user_id=current_user.id,
                        club_id=club_id,
                        is_active=True
                    ).first()
                    
                    if membership:
                        g.current_club = club
                        g.current_membership = membership
                    else:
                        # User doesn't have access to this club, clear session
                        session.pop('current_club_id', None)
    
    # Make csrf_token() available in all templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)
    
    # Make club context available in all templates
    @app.context_processor
    def inject_club_context():
        """Make club information available in all templates"""
        return dict(
            current_club=getattr(g, 'current_club', None),
            current_membership=getattr(g, 'current_membership', None)
        )

    return app
