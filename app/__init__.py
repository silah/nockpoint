from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
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
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///nockpoint.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if config:
        app.config.update(config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Register blueprints first
    from app.auth import auth_bp
    from app.main import main_bp
    from app.inventory import inventory_bp
    from app.members import members_bp
    from app.events import events_bp
    from app.competitions import competitions_bp
    from app.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(members_bp, url_prefix='/members')
    app.register_blueprint(events_bp, url_prefix='/events')
    app.register_blueprint(competitions_bp, url_prefix='/competitions')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Initialize CSRF and exempt API blueprint
    csrf.init_app(app)
    csrf.exempt(api_bp)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Context processor to make club settings available in all templates
    @app.context_processor
    def inject_club_settings():
        from app.models import ClubSettings
        return dict(club_settings=ClubSettings.get_settings())
    
    # Register pro feature template functions
    from app.pro_features import register_pro_template_functions
    register_pro_template_functions(app)
    
    # Template filter to convert newlines to HTML breaks
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if not text:
            return text
        return text.replace('\n', '<br>')
    
    return app
