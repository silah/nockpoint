# Copilot Instructions for Nockpoint Archery Club Management

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a comprehensive Flask-based web application for managing archery club operations, including:
- **Member Management**: User registration, profiles, membership types, and activity tracking
- **Event Management**: Shooting events, beginners courses, attendance tracking, and automated charging
- **Competition System**: Full competition management with groups, teams, scoring, and results
- **Inventory Management**: Equipment tracking with category-specific attributes and automated inventory checking
- **Financial Management**: Member charges, payment tracking, and membership-based pricing
- **API Integration**: RESTful API with JWT authentication for mobile and external integrations
- **Pro Feature System**: Subscription-based feature gating for advanced functionality

## Technology Stack
- **Backend**: Flask with Blueprints architecture
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login with JWT for API
- **Forms**: WTForms and Flask-WTF with CSRF protection
- **Frontend**: Bootstrap 5 with Jinja2 templates
- **Migration**: Flask-Migrate
- **Testing**: Custom test suite with 76+ automated tests

## Architecture Patterns
- Use Flask Blueprints for modular organization (auth, main, inventory, members, events, competitions, api)
- Follow MVC pattern with clear separation of concerns
- Use SQLAlchemy models with relationships and computed properties
- Implement role-based access control (Admin/Member) with decorators
- Store category-specific attributes in JSON fields for flexibility
- Implement pro feature gating using decorators and template functions
- Use comprehensive error handling and flash messaging

## Database Design
- **Users**: Roles (admin/member), membership types (annual/quarterly/monthly/per-event), activation codes
- **Events**: Shooting events with type distinction, capacity limits, and free event flags
- **Competitions**: Multi-group competitions with teams, individual/team scoring, and inventory checking
- **Inventory**: Categories with specialized forms, JSON attributes, and automated target face checking
- **Charges**: Automatic billing based on membership type with payment tracking
- **Pro Features**: Subscription tracking with feature-specific enablement and expiration dates

## Code Style Guidelines
- Follow PEP 8 for Python code
- Use descriptive variable and function names
- Include docstrings for functions and classes
- Use type hints where appropriate
- Keep functions small and focused
- Use Flask best practices for routing and error handling

## Security Considerations
- Always use @login_required decorator for protected routes
- Implement admin_required decorator for admin-only actions
- Use @pro_feature_required('feature_name') for pro-gated functionality
- Validate all form inputs using WTForms validators with CSRF tokens
- Use proper password hashing with werkzeug.security
- Escape all user input in templates
- API endpoints use JWT authentication with proper token validation
- Implement proper error handling to avoid information disclosure

## Pro Feature System
The application implements a comprehensive pro feature gating system:

### Using Pro Features in Routes
```python
from app.pro_features import pro_feature_required

@blueprint.route('/advanced-feature')
@login_required
@admin_required
@pro_feature_required()  # All-or-nothing: any feature name or none
def advanced_feature():
    return render_template('advanced.html')
```

### Using Pro Features in Templates
```html
{% if has_pro_feature() %}
    <a href="{{ url_for('members.analytics') }}" class="btn btn-primary">
        Advanced Analytics <span class="badge bg-success">Pro</span>
    </a>
{% else %}
    <button class="btn btn-outline-secondary" disabled>
        Advanced Analytics <span class="badge bg-warning">Pro</span>
    </button>
{% endif %}
```

### Available Pro Features
- `advanced_inventory`: Enhanced inventory tracking and analytics
- `advanced_competitions`: Tournament brackets and advanced scoring
- `member_analytics`: Detailed member activity reports
- `advanced_events`: Recurring events and templates
- `financial_reporting`: Revenue and expense tracking
- `communication_tools`: Email campaigns and notifications
- `api_access`: Enhanced API access with higher limits
- `custom_branding`: Club branding customization
- `data_export`: Advanced data export capabilities
- `coaching_tools`: Training plans and progress tracking

### Pro Feature Management
```python
# Enable pro features programmatically (all-or-nothing)
from app.models import ClubSettings
from datetime import datetime, timedelta
settings = ClubSettings.get_settings()
settings.is_pro_enabled = True
settings.pro_expires_at = datetime.utcnow() + timedelta(days=365)  # Optional expiration
settings.pro_subscription_id = 'sub_123456789'  # Optional external ID
db.session.commit()

# Check pro features in code (simplified)
from app.pro_features import check_pro_feature
if check_pro_feature():  # No specific feature name needed
    # Execute any pro feature logic
```

## Frontend Guidelines
- Use Bootstrap 5 components consistently with proper responsive classes
- Implement responsive design for mobile devices (especially for scoring interfaces)
- Use Bootstrap Icons for consistency throughout all modules
- Include proper ARIA labels for accessibility
- Use JavaScript sparingly, prefer server-side rendering
- Use modals for delete confirmations with proper CSRF tokens
- Implement flash message display for user feedback
- Show pro feature badges and upgrade prompts where appropriate

## Module-Specific Features

### Inventory Management
- Support multiple categories with specialized forms (Bows, Arrows, Targets, Target Faces)
- Store category-specific attributes in JSON fields for flexibility
- Implement automated inventory checking for competitions
- Support different units (piece, set, pair, etc.) and condition tracking
- Separate Target Faces from Targets with standardized sizes (20, 40, 60, 80, 122cm)

### Event Management
- Support different event types (regular, beginners_course)
- Implement capacity limits and attendance tracking
- Auto-generate charges based on membership type (free for annual/quarterly/monthly, charged for per-event)
- Handle both member registration and beginners course student management
- Support quick admin registration and bulk operations

### Competition System
- Multi-group competitions with age restrictions and descriptions
- Team and individual scoring with arrow-by-arrow tracking
- Automated team generation with smart balancing
- Competition workflow: setup → registration → teams → scoring → results
- Real-time inventory checking for target face availability
- Comprehensive results calculation with rankings and statistics

### Member Management
- Support multiple membership types with different pricing models
- Implement user activation codes for controlled registration
- Track member activity, attendance, and payment history
- Support admin-managed member profiles with role management
- Integrated charging system based on membership benefits

### API Integration
- RESTful API with JWT authentication
- Endpoints for events, competitions, scoring, and member management
- Proper error handling and response formatting
- Rate limiting and security controls
- Mobile-friendly endpoints for on-site usage

## Testing Guidelines
- Run full test suite with `python run_all_tests.py` before commits
- Maintain 76+ passing tests across all modules
- Test pro feature gating functionality
- Validate CSRF token handling in forms
- Test API endpoints with proper authentication
- Ensure database migrations work correctly

## Development Workflow
- Use feature branches for new development
- Test thoroughly before merging to main branches
- Document new pro features in `app/pro_features.py`
- Update database migrations for schema changes
- Maintain backward compatibility for existing installations
