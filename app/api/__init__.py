from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes after blueprint creation
from app.api import auth, events, competitions