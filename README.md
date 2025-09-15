# Nockpoint - Archery Club Management System

A comprehensive Flask-based web application designed to help archery clubs manage their operations efficiently. The MVP focuses on inventory management with plans to expand to competition management, member management, and scheduling.

## Features

### Current (MVP - Inventory Management)
- **User Authentication & Authorization**
  - User registration and login
  - Role-based access control (Admin/Member)
  - Secure password hashing

- **Inventory Management**
  - Multiple inventory categories (Bows, Arrows, Targets, etc.)
  - Category-specific attributes (draw weight, spine, face size, etc.)
  - Quantity tracking and location management
  - Item condition monitoring
  - Search and filtering capabilities
  - Responsive UI with Bootstrap 5

- **Dashboard**
  - Inventory statistics
  - Recent items overview
  - Quick actions for efficient management

### Planned Features
- Competition management (schedules, results, categories)
- Member management and participation tracking
- Shooting schedule coordination
- Reporting and analytics

## Technology Stack

- **Backend**: Flask with Blueprints architecture
- **Database**: SQLAlchemy with SQLite (dev) / PostgreSQL (prod)
- **Authentication**: Flask-Login
- **Forms**: WTForms and Flask-WTF
- **Frontend**: Bootstrap 5, Jinja2 templates
- **Migrations**: Flask-Migrate

## Project Structure

```
nockpoint/
├── app/
│   ├── __init__.py              # Application factory
│   ├── models.py                # Database models
│   ├── forms.py                 # WTForms definitions
│   ├── auth/                    # Authentication blueprint
│   ├── main/                    # Main application blueprint
│   ├── inventory/               # Inventory management blueprint
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── dashboard.html
│   │   ├── auth/
│   │   └── inventory/
│   └── static/
│       └── css/
├── app.py                       # Application entry point
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
└── README.md
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd nockpoint
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   flask init-db
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

The application will be available at `http://localhost:5000`

## Default Login Credentials

- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator

## Configuration

### Environment Variables

- `FLASK_APP`: Application entry point (default: `app.py`)
- `FLASK_ENV`: Environment (development/production)
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string

### Database Configuration

**Development (SQLite)**:
```
DATABASE_URL=sqlite:///nockpoint.db
```

**Production (PostgreSQL)**:
```
DATABASE_URL=postgresql://username:password@localhost/nockpoint
```

## Database Schema

### Users
- User authentication and role management
- Supports Admin and Member roles
- Password hashing with werkzeug

### Inventory Categories
- Flexible category system
- Supports custom descriptions
- One-to-many relationship with items

### Inventory Items
- Complete item tracking
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
