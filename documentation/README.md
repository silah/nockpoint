# Nockpoint Archery Club Management System

## Documentation Overview

This documentation provides comprehensive information about the Nockpoint Archery Club Management System, a Flask-based web application for managing archery club operations.

## System Architecture

The application follows a modular Flask blueprint architecture with the following key components:

- **Authentication & User Management** - User registration, login, and role-based access control
- **Inventory Management** - Equipment tracking, categorization, and attribute management
- **Member Management** - Club member administration and profile management
- **Events System** - Shooting event calendar, attendance tracking, and payment management
- **Competition Management** - Comprehensive competition system with scoring, teams, and results

## Key Features

### Competition System
- **Multi-format Competitions**: Support for various archery competition formats
- **Team Management**: Automatic team generation and target assignment
- **Real-time Scoring**: Individual arrow scoring with live calculations
- **Results & Rankings**: Comprehensive results with group and team standings
- **Progress Tracking**: Competition completion monitoring and statistics

### Event Management
- **Event Scheduling**: Calendar-based event management
- **Attendance Tracking**: Member registration and attendance recording
- **Payment Integration**: Event fees and member charge management
- **Automated Workflows**: Streamlined event administration

### Inventory Control
- **Flexible Categories**: Customizable equipment categories with specific attributes
- **Stock Management**: Quantity tracking and location management
- **Condition Monitoring**: Equipment condition and maintenance tracking
- **Search & Filter**: Advanced inventory search and filtering capabilities

### User & Access Management
- **Role-based Security**: Admin and member role separation
- **Secure Authentication**: Password hashing and session management
- **Profile Management**: Comprehensive user profile system
- **Activity Tracking**: User action logging and audit trails

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
- [API Documentation](./api.md) - RESTful API endpoints and usage
- [Testing](./testing.md) - Test strategies and procedures
- [Deployment](./deployment.md) - Production deployment guide
- [Dependencies](./dependencies.md) - Required packages and versions

### Technical Documentation  
- [Dependencies](./dependencies.md) - Third-party packages and requirements

## Getting Started

### For Developers
1. Start with [Configuration](./configuration.md) to set up your development environment
2. Review [Models](./models.md) to understand the data structure
3. Check [API Documentation](./api.md) for endpoint details
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

- **Complete Competition System** with scoring, teams, and results
- **User Authentication** with Flask-Login and role-based access control
- **Inventory Tracking** with flexible categories and attributes
- **Member Management** with comprehensive profile administration
- **Event Management** with calendar, attendance, and payment tracking
- **RESTful API** with comprehensive endpoint coverage
- **Responsive UI** with Bootstrap 5 and modern design
- **Database Migrations** with Flask-Migrate for version control

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Jinja2 templates, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with secure session management
- **Testing**: unittest with comprehensive test coverage
- **Deployment**: Gunicorn, Nginx, systemd integration

## Recent Updates

- ✅ **Competition System**: Complete competition management with real-time scoring
- ✅ **API Documentation**: Comprehensive REST API reference with examples
- ✅ **Testing Framework**: Unit and integration test coverage with automated workflows
- ✅ **Deployment Guide**: Production deployment procedures with security hardening
- ✅ **Configuration Management**: Environment-based configuration system

## Documentation Coverage

The documentation now covers all major system components with comprehensive detail for developers, administrators, and users.

---

For detailed information about each component, please refer to the individual documentation files in this directory.
