# Nockpoint Deployment Guide

This document explains how to deploy the Nockpoint Archery Club Management System from a clean repository.

## Files Included in Repository

### Core Application Files
- `app.py` - Main application entry point
- `app/` - Application package containing all modules
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `README.md` - Main documentation

### Configuration Files
- `.gitignore` - Git ignore patterns
- `.github/copilot-instructions.md` - Development guidelines

## Files NOT Included (Generated/Local)

### Database & Migrations
- `instance/` - Contains SQLite database and instance config
- `migrations/` - Flask-Migrate database migration files
- `*.db`, `*.sqlite3` - Database files

### Development Files
- `documentation/` - Development documentation
- `tests/` - Test files
- `userstories/` - User story documentation
- Development markdown files (`*_STATUS.md`, etc.)

### Environment & Dependencies
- `.env` - Local environment variables (use `.env.example` as template)
- `venv/`, `.venv` - Virtual environment directories
- `__pycache__/` - Python bytecode cache

## Fresh Deployment Steps

### 1. Environment Setup
```bash
git clone <repository-url>
cd nockpoint
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
cp .env.example .env
# Edit .env file with your settings:
# - SECRET_KEY: Generate a secure secret key
# - DATABASE_URL: Set database connection (SQLite for dev, PostgreSQL for prod)
```

### 3. Database Initialization
```bash
# Initialize migrations (first time only)
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

### 4. Run Application
```bash
python app.py
```

## Environment Variables

Required variables (see `.env.example`):

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key for sessions | `your-secret-key-here` |
| `DATABASE_URL` | Database connection string | `sqlite:///nockpoint.db` |
| `FLASK_ENV` | Flask environment | `development` |
| `FLASK_DEBUG` | Enable debug mode | `1` |

## First-Time Setup

1. Register an admin user through the web interface
2. Manually update the user's role to 'admin' in the database
3. Configure club settings through the admin interface
4. Set up inventory categories and initial data

## Production Considerations

- Use PostgreSQL instead of SQLite
- Set `FLASK_ENV=production`
- Use proper secret key management
- Set up proper logging
- Configure reverse proxy (nginx)
- Use WSGI server (gunicorn)

## Security Notes

- Never commit `.env` files with real secrets
- Use strong database passwords
- Configure HTTPS in production
- Regular database backups
- Keep dependencies updated