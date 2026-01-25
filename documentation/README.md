# Nockpoint Archery Club Management System

## Documentation Overview

This documentation provides comprehensive information about the Nockpoint Archery Club Management System, a multi-tenant Flask-based web application for managing archery club operations.

## System Architecture

Nockpoint is a multi-tenant platform where multiple independent archery clubs can operate on a shared infrastructure. Each club has complete data isolation with its own members, events, inventory, and competitions.

The application follows a modular Flask blueprint architecture with the following key components:

- **Multi-Tenancy** - Club-based data isolation and user management
- **Authentication** - User registration, login, and club-scoped authorization
- **Inventory Management** - Equipment tracking and categorization per club
- **Member Management** - Club member administration and bulk import
- **Events System** - Shooting event calendar, attendance, and payment tracking
- **Competitions** - Tournament management with scoring

## Documentation Structure

### Getting Started
- **[Quickstart Guide](../QUICKSTART.md)** - Quick setup for new developers
- [Deployment](./deployment.md) - Production deployment instructions
- [Dependencies](./dependencies.md) - Third-party packages and requirements

### Core Architecture
- **[Multi-Tenancy](./multi-tenancy.md)** - ⭐ Multi-club architecture and developer guide
- [Models](./models.md) - Database models and relationships
- [Authentication](./authentication.md) - User authentication and club authorization
- [Forms](./forms.md) - WTForms for user input validation
- [Views & Routes](./views-and-routes.md) - Application endpoints and business logic
- [Templates](./templates.md) - Frontend user interface documentation

### Feature Modules
- [Inventory Management](./inventory.md) - Equipment and category management
- [Member Management](./members.md) - Club member administration
- [CSV Import](./csv-import.md) - Bulk member import feature
- [Events System](./events.md) - Shooting events and attendance tracking
- [Shooting Events](./shooting-events.md) - Event-specific features and workflows
- [Competitions](./competitions.md) - Tournament management

### Testing & Quality
- [Testing](./testing.md) - Automated testing guide
- [Manual QA Plan](./manual-qa-plan.md) - Manual testing procedures
- [Web Interface](./web-interface.md) - UI/UX documentation

## Quick Start

### For New Developers
See the **[Quickstart Guide](../QUICKSTART.md)** for rapid onboarding.

### Basic Setup
1. **Installation**: `pip install -r requirements.txt`
2. **Database**: `flask db upgrade`
3. **Create Admin**: `python create_admin.py`
4. **Launch**: `python app.py`
5. **Access**: http://localhost:5000

### Multi-Tenant Setup
1. Register a new club at `/auth/register-club`
2. First user becomes club admin automatically
3. Configure club settings at `/settings`
4. Add members via `/members/import-csv` or manually

## Key Features

### Multi-Tenancy
- Multiple independent clubs on one platform
- Complete data isolation between clubs
- Users can belong to multiple clubs
- Per-club admin roles and permissions

### User Management
- Flask-Login authentication
- Club-scoped role-based access control
- Club selection for multi-club users
- Bulk member CSV import with password generation

### Inventory
- Category-based equipment organization
- Flexible attributes per category (JSON storage)
- Quantity tracking and location management
- Club-specific inventory catalogs

### Events & Attendance
- Shooting event calendar
- Attendance tracking
- Payment/charge management per member
- Event-specific pricing

### Competitions
- Tournament creation and management
- Group and team organization
- Scoring system with arrow-level tracking
- Competition registration

## Development Guidelines

### Multi-Tenancy Rules
**Always** follow these patterns when developing:

1. **Filter by club**: `MyModel.query.filter_by(club_id=g.current_club.id)`
2. **Set club_id**: All records must have `club_id` set on creation
3. **Use decorators**: `@require_club_context` or `@require_club_admin`
4. **Verify ownership**: Filter by both `id` and `club_id` when viewing/editing
5. **Club-scoped helpers**: Use `is_club_admin()` in templates, not deprecated `is_admin()`

See [Multi-Tenancy Guide](./multi-tenancy.md) for complete developer reference.

## Project Structure

```
nockpoint/
├── app/
│   ├── __init__.py           # App factory
│   ├── models.py             # Database models
│   ├── forms.py              # WTForms definitions
│   ├── decorators.py         # Authorization decorators
│   ├── club_utils.py         # Club helper functions
│   ├── auth/                 # Authentication blueprint
│   ├── main/                 # Main routes blueprint
│   ├── members/              # Member management
│   ├── inventory/            # Inventory management
│   ├── events/               # Event management
│   ├── competitions/         # Competition management
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
├── migrations/               # Database migrations
├── tests/                    # Test suite
├── documentation/            # This documentation
├── config.py                 # Configuration
├── app.py                    # Development server
└── requirements.txt          # Python dependencies
```

## Contributing

When adding new features:
1. Follow the multi-tenancy patterns (see [Multi-Tenancy Guide](./multi-tenancy.md))
2. Add tests for new functionality
3. Update relevant documentation
4. Use proper decorators for authorization
5. Ensure data is scoped to clubs

## Support

For questions or issues:
- Review the [Multi-Tenancy Guide](./multi-tenancy.md) for common patterns
- Check existing documentation in this folder
- Review test files for examples
- See [QUICKSTART.md](../QUICKSTART.md) for setup help
- **Database Migrations** with Flask-Migrate

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with session management

---

For detailed information about each component, please refer to the individual documentation files in this directory.
