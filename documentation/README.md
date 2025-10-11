# Nockpoint Archery Club Management System

## Documentation Overview

This documentation provides comprehensive information about the Nockpoint Archery Club Management System, a Flask-based web application for managing archery club operations.

## System Architecture

The application follows a modular Flask blueprint architecture with the following key components:

- **Authentication & User Management** - User registration, login, and role-based access
- **Inventory Management** - Equipment tracking and categorization
- **Member Management** - Club member administration
- **Events System** - Shooting event calendar, attendance, and payment tracking

## Documentation Structure

### Core Components
- [Models](./models.md) - Database models and relationships
- [Forms](./forms.md) - WTForms for user input validation
- [Views & Routes](./views-and-routes.md) - Application endpoints and business logic
- [Templates](./templates.md) - Frontend user interface documentation

### System Modules
- [Authentication](./authentication.md) - User authentication and authorization
- [Inventory Management](./inventory.md) - Equipment and category management
- [Member Management](./members.md) - Club member administration
- [Events System](./events.md) - Shooting events and attendance tracking

### Technical Documentation
- [Dependencies](./dependencies.md) - Third-party packages and requirements
- [Database Schema](./database-schema.md) - Database structure and relationships
- [API Reference](./api-reference.md) - Internal API endpoints
- [Deployment](./deployment.md) - Setup and deployment instructions

## Quick Start

1. **Installation**: Install dependencies from `requirements.txt`
2. **Database**: Initialize with `flask db upgrade`
3. **Admin User**: Create via registration and set role to 'admin'
4. **Launch**: Run with `python app.py`

## Key Features

- **User Authentication** with Flask-Login
- **Role-based Access Control** (Admin/Member)
- **Inventory Tracking** with categories and quantities
- **Member Management** with profile administration
- **Event Calendar** with attendance and payment tracking
- **Responsive UI** with Bootstrap 5
- **Database Migrations** with Flask-Migrate

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with session management

---

For detailed information about each component, please refer to the individual documentation files in this directory.
