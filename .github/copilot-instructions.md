# Copilot Instructions for Nockpoint Archery Club Management

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a Flask-based web application for managing archery club operations, focusing initially on inventory management as the MVP.

## Technology Stack
- **Backend**: Flask with Blueprints architecture
- **Database**: SQLAlchemy with SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login
- **Forms**: WTForms and Flask-WTF
- **Frontend**: Bootstrap 5 with Jinja2 templates
- **Migration**: Flask-Migrate

## Architecture Patterns
- Use Flask Blueprints for modular organization (auth, main, inventory)
- Follow MVC pattern with clear separation of concerns
- Use SQLAlchemy models with relationships
- Implement role-based access control (Admin/Member)
- Store category-specific attributes in JSON fields for flexibility

## Database Design
- Users have roles (admin/member) with different permissions
- Inventory items belong to categories
- Category-specific attributes stored in JSON field for flexibility
- Use proper foreign key relationships and constraints

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
- Validate all form inputs using WTForms validators
- Use proper password hashing with werkzeug
- Escape all user input in templates

## Frontend Guidelines
- Use Bootstrap 5 components consistently
- Implement responsive design for mobile devices
- Use Bootstrap Icons for consistency
- Include proper ARIA labels for accessibility
- Use JavaScript sparingly, prefer server-side rendering

## Inventory-Specific Features
- Support multiple inventory categories with unique attributes
- Implement search and filtering functionality
- Use pagination for large lists
- Support different units (piece, set, pair, etc.)
- Track item condition and location

## Future Extensions
The system is designed to expand to include:
- Competition management
- Member management  
- Shooting schedule management
- Reporting and analytics
