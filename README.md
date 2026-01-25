# Nockpoint - Archery Club Management System

A comprehensive multi-tenant Flask-based web application for managing archery club operations. Multiple independent clubs can operate on a shared platform with complete data isolation.

## 🎯 Features

### Multi-Tenancy
- **Multiple Independent Clubs** - Each club has isolated data and settings
- **Club Registration** - Public registration flow for new clubs
- **User Management** - Users can belong to multiple clubs with different roles
- **Club Selection** - Automatic context switching for multi-club users

### Member Management
- **Bulk CSV Import** - Import members with automatic password generation
- **Profile Management** - Member information and club-specific roles
- **Role-Based Access** - Admin and member permissions per club
- **Multi-Club Membership** - Users can join and switch between clubs

### Inventory Management
- **Category System** - Flexible categories (Bows, Arrows, Targets, etc.)
- **Custom Attributes** - Category-specific fields (draw weight, spine, etc.)
- **Quantity Tracking** - Stock levels and location management
- **Search & Filter** - Find equipment quickly

### Events & Attendance
- **Event Calendar** - Schedule and manage shooting events
- **Attendance Tracking** - Monitor member participation
- **Payment Management** - Track member charges and payments
- **Event Types** - Regular events, competitions, training sessions

### Competitions
- **Tournament Management** - Create and manage competitions
- **Scoring System** - Arrow-level score tracking
- **Teams & Groups** - Organize participants
- **Results Tracking** - Competition outcomes and standings

## 🚀 Quick Start

### For Developers
See **[QUICKSTART.md](./QUICKSTART.md)** for rapid setup.

### Installation

```bash
# Clone and enter directory
git clone <repository-url>
cd nockpoint

# Install dependencies
pip install -r requirements.txt

# Initialize database
flask db upgrade

# Create first admin user (optional)
python create_admin.py

# Run development server
python app.py
```

Access at: http://localhost:5000

### First Time Setup

1. **Register a Club**: Navigate to `/auth/register-club`
2. **Login**: Use credentials from club registration
3. **Configure**: Set club settings at `/settings`
4. **Add Members**: Import via CSV or add individually

## 📚 Documentation

Full documentation is available in the [documentation/](./documentation/) folder:

- **[Multi-Tenancy Guide](./documentation/multi-tenancy.md)** - Architecture and developer patterns
- **[CSV Import](./documentation/csv-import.md)** - Bulk member import feature
- **[Models](./documentation/models.md)** - Database structure
- **[Authentication](./documentation/authentication.md)** - User auth and authorization
- **[Testing](./documentation/testing.md)** - Test suite guide

See [documentation/README.md](./documentation/README.md) for complete index.

## 🛠 Technology Stack

- **Backend**: Flask 2+ with Blueprints architecture
- **Database**: SQLAlchemy ORM (SQLite dev / PostgreSQL prod)
- **Authentication**: Flask-Login with club-scoped roles
- **Forms**: WTForms with CSRF protection
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Migrations**: Flask-Migrate (Alembic)

## 📁 Project Structure

```
nockpoint/
├── app/
│   ├── __init__.py           # App factory with multi-tenancy setup
│   ├── models.py             # SQLAlchemy models (Club, User, Inventory, etc.)
│   ├── forms.py              # WTForms for all features
│   ├── decorators.py         # Authorization decorators
│   ├── club_utils.py         # Club helper functions
│   ├── auth/                 # Authentication blueprint
│   ├── main/                 # Dashboard and settings
│   ├── members/              # Member management
│   ├── inventory/            # Equipment tracking
│   ├── events/               # Event calendar
│   ├── competitions/         # Tournament management
│   ├── templates/            # Jinja2 templates
│   └── static/               # CSS, JS, images
├── migrations/               # Database migrations (Alembic)
├── tests/                    # Test suite
├── documentation/            # Comprehensive docs
├── QUICKSTART.md            # Developer quick start
├── config.py                # Configuration
├── app.py                   # Development server
└── requirements.txt         # Python dependencies
```

## 🔧 Configuration

### Environment Variables

```bash
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/nockpoint.db
```

### Database Options

**Development (SQLite)**:
```
DATABASE_URL=sqlite:///instance/nockpoint.db
```

**Production (PostgreSQL)**:
```
DATABASE_URL=postgresql://user:password@localhost/nockpoint
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=app

# Run specific test file
python -m pytest tests/test_models.py
```

See [documentation/testing.md](./documentation/testing.md) for details.

## 🏗 Development Guidelines

### Multi-Tenancy Rules

When developing new features, **always**:

1. **Filter by club**: `MyModel.query.filter_by(club_id=g.current_club.id).all()`
2. **Set club_id**: All club-specific records need `club_id` on creation
3. **Use decorators**: `@require_club_context` or `@require_club_admin`
4. **Verify ownership**: Filter by both `id` and `club_id` when viewing/editing
5. **Club helpers**: Use `is_club_admin()` in templates

See [Multi-Tenancy Guide](./documentation/multi-tenancy.md) for complete patterns.

### Code Style

- Follow PEP 8 for Python code
- Use descriptive names for variables and functions
- Add docstrings to functions and classes
- Keep functions small and focused
- Write tests for new features

## 🚢 Deployment

See [documentation/deployment.md](./documentation/deployment.md) for production deployment instructions.

### Quick Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Set `FLASK_ENV=production`
- [ ] Configure WSGI server (gunicorn)
- [ ] Set up reverse proxy (nginx)
- [ ] Enable HTTPS
- [ ] Configure backups
- [ ] Set up monitoring

## 🤝 Contributing

1. Review [Multi-Tenancy Guide](./documentation/multi-tenancy.md)
2. Follow code style guidelines
3. Write tests for new features
4. Update documentation
5. Use proper authorization decorators
6. Ensure data is club-scoped

## 📝 License

[Add your license here]

## 📧 Support

For questions or issues:
- Review [documentation/](./documentation/)
- Check [QUICKSTART.md](./QUICKSTART.md)
- See test files for examples
- Category-specific attributes stored in JSON
- Quantity, location, and condition tracking
- Purchase information and notes

## Usage

### For Administrators
1. **Manage Categories**: Create and organize inventory categories
2. **Add Items**: Add new inventory items with detailed attributes
3. **Edit/Delete**: Modify or remove inventory items
4. **Monitor**: Track inventory levels and conditions

### For Members
1. **View Inventory**: Browse available items and categories
2. **Search**: Find specific items using search and filters
3. **View Details**: Access detailed information about items

## Development

### Adding New Features
1. Create new blueprints in the `app/` directory
2. Define models in `models.py`
3. Create forms in `forms.py`
4. Add templates in appropriate subdirectories
5. Register blueprints in `app/__init__.py`

### Database Migrations
```bash
flask db init      # Initialize migrations (first time only)
flask db migrate   # Generate migration
flask db upgrade   # Apply migration
```

### Creating Admin Users
```bash
flask create-admin username email password
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please create an issue in the repository or contact the development team.

---

**Nockpoint** - Making archery club management simple and efficient.
