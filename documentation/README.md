# Nockpoint Archery Club Management System

## Documentation Overview

This documentation provides comprehensive information about the Nockpoint Archery Club Management System, a Flask-based **web application** for managing archery club operations.

**Important Note**: This is a traditional web application that serves HTML pages and uses form-based interactions. It is **not** a REST API system. See [Web Application Architecture](#web-application-architecture) for details.

## Web Application Architecture

The application follows a modular Flask blueprint architecture with the following key components:

- **Authentication & User Management** - HTML-based user registration, login, and role-based access control
- **Inventory Management** - Web interface for equipment tracking, categorization, and attribute management  
- **Member Management** - Web forms for club member administration and profile management
- **Events System** - Calendar interface for shooting events, attendance tracking, and payment management
- **Competition Management** - Web-based competition system with button-based scoring, teams, and results

## Key Features

### Competition System
- **Multi-format Competitions**: Web interface supporting various archery competition formats
- **Team Management**: Automatic team generation and target assignment through web forms
- **Button-based Scoring**: Individual arrow scoring with numbered button interface (1-10 per arrow)
- **Results & Rankings**: HTML results pages with group and team standings
- **Progress Tracking**: Web-based competition completion monitoring and statistics

### Event Management
- **Event Scheduling**: HTML calendar interface for event management
- **Attendance Tracking**: Web forms for member registration and attendance recording
- **Payment Integration**: Web interface for event fees and member charge management
- **Automated Workflows**: Form-based event administration

### Inventory Control
- **Flexible Categories**: Web interface for customizable equipment categories with specific attributes
- **Dynamic Forms**: Category-specific form fields (e.g., bow attributes: handedness, length, draw weight)
- **Stock Management**: Web forms for quantity tracking and location management
- **Condition Monitoring**: Web interface for equipment condition and maintenance tracking
- **Search & Filter**: HTML-based inventory search and filtering capabilities

### User & Access Management
- **Role-based Security**: Admin and member role separation with web session authentication
- **Secure Authentication**: Flask-Login with password hashing and HTML login forms
- **Profile Management**: Web-based user profile management system
- **Activity Tracking**: Server-side logging and flash message notifications

## Documentation Structure

### Core Components
- [Models](./models.md) - Database models and relationships
- [Forms](./forms.md) - WTForms for user input validation
- [Views and Routes](./views-and-routes.md) - Flask blueprints and URL routing
- [Templates](./templates.md) - Jinja2 templates and UI components

### Feature Modules
- [Authentication](./authentication.md) - User management and security
- [Inventory Management](./inventory.md) - Equipment tracking system
- [Member Management](./members.md) - Club member administration
- [Events System](./events.md) - Shooting events and attendance
- [Competition Management](./competitions.md) - Competition system and scoring

### Development & Operations
- [Configuration](./configuration.md) - Application configuration and settings
- [~~API Documentation~~](./api.md) - **OUTDATED**: Documents REST API that doesn't exist
- [Testing](./testing.md) - Test strategies and procedures
- [Deployment](./deployment.md) - Production deployment guide
- [Dependencies](./dependencies.md) - Required packages and versions

### Technical Documentation  
- [Dependencies](./dependencies.md) - Third-party packages and requirements
- [Web Interface Overview](./web-interface.md) - HTML routes and form handling

## Getting Started

### For Developers
1. Start with [Configuration](./configuration.md) to set up your development environment
2. Review [Models](./models.md) to understand the data structure
3. Check [Views and Routes](./views-and-routes.md) for web endpoint details
4. Follow [Testing](./testing.md) guidelines for quality assurance

### For System Administrators
1. Read [Deployment](./deployment.md) for production setup
2. Review [Configuration](./configuration.md) for environment settings
3. Check [Dependencies](./dependencies.md) for system requirements

### For Users
1. See [Authentication](./authentication.md) for user management
2. Review individual feature documentation for specific functionality

## Quick Start

1. **Installation**: Install dependencies from `requirements.txt`
2. **Configuration**: Copy `.env.example` to `.env` and configure
3. **Database**: Initialize with `flask db upgrade`
4. **Admin User**: Create via registration and set role to 'admin'
5. **Launch**: Run with `python app.py`

## Key Features

- **Complete Competition System** with button-based scoring, teams, and HTML results
- **User Authentication** with Flask-Login and HTML-based role access control
- **Inventory Tracking** with dynamic category-specific forms and attributes
- **Member Management** with comprehensive web-based profile administration
- **Event Management** with HTML calendar, attendance forms, and payment tracking
- **Web Application Interface** with comprehensive HTML endpoint coverage
- **Responsive UI** with Bootstrap 5 and modern design
- **Database Migrations** with Flask-Migrate for version control

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Jinja2 templates, JavaScript (minimal)
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with secure session management
- **Forms**: HTML forms with CSRF protection and server-side validation
- **UI Framework**: Bootstrap 5 with responsive design
- **Testing**: unittest with comprehensive test coverage
- **Deployment**: Gunicorn, Nginx, systemd integration

## Recent Updates

- ✅ **Competition System**: Complete competition management with button-based scoring interface
- ✅ **Inventory Forms**: Dynamic category-specific forms with JSON field loading
- ✅ **Bow Management**: Specific bow attributes (handedness, length, draw weight)
- ✅ **Web Interface**: Complete HTML-based interface with Bootstrap 5
- ✅ **Documentation**: Updated to reflect actual web application architecture

## Architecture Type: Web Application (Not API)

**This system is a traditional server-rendered web application**, not a REST API:

- **HTML Responses**: All routes return rendered HTML pages
- **Form-Based**: Uses HTML forms with POST/redirect pattern
- **Session Authentication**: Browser sessions with Flask-Login
- **Server-Side Rendering**: Jinja2 templates with server-side logic
- **CSRF Protection**: Form-based CSRF tokens
- **Flash Messages**: Server-side notification system

**Limited JSON Endpoints**:
- `/inventory/api/category-fields/<id>` - Dynamic form field loading
- `/inventory/api/item-attributes/<id>` - Item attribute retrieval
- Various AJAX helpers for payment status updates

## Documentation Coverage

The documentation now covers all major system components with comprehensive detail for developers, administrators, and users.

---

For detailed information about each component, please refer to the individual documentation files in this directory.
