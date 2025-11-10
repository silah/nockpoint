from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
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
    
    # Make csrf_token() available in all templates
    @app.context_processor
    def inject_csrf_token():
        return dict(csrf_token=generate_csrf)

    return app
