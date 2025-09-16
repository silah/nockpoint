# Nockpoint Archery Club Management System

A comprehensive Flask-based **web application** for managing archery club operations including inventory management, member administration, event scheduling, and competition management with advanced scoring systems.

## ⚠️ Important: Web Application (Not API)

This is a **traditional web application** that serves HTML pages and uses form-based interactions. It is **NOT** a REST API system. See [documentation/web-interface.md](documentation/web-interface.md) for detailed interface documentation.

## Key Features

- **Club Settings Management**: Customize club name, default event location, and social links
- **Competition Management**: Button-based scoring system with team management and comprehensive results
- **Dynamic Inventory System**: Category-specific forms with bow attributes (handedness, length, draw weight)  
- **Member Administration**: Complete member profile and role management
- **Event Scheduling**: Calendar-based event management with attendance tracking
- **Payment Integration**: Event fees and member charge management
- **Role-based Security**: Admin and member access controls with session authentication

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite (development) or PostgreSQL (production)

### Installation

1. **Clone and Setup**:
```bash
git clone <repository-url>
cd nockpoint
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. **Database Setup**:
```bash
flask db upgrade
```

3. **Create Admin User**:
Register through the web interface, then update user role in database:
```bash
# Access database and update user role to 'admin'
```

4. **Run Application**:
```bash
python app.py
# or
flask run
```

5. **Access Application**:
Open http://localhost:5000 in your browser

## Technology Stack

- **Backend**: Flask 2.3.3, SQLAlchemy, WTForms
- **Frontend**: Bootstrap 5, Jinja2 templates, JavaScript (minimal)
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: Flask-Login with session management
- **Forms**: HTML forms with CSRF protection and server-side validation
- **UI**: Responsive Bootstrap 5 interface

## System Architecture

### Web Application Structure
```
app/
├── __init__.py          # Flask app factory
├── models.py           # SQLAlchemy database models
├── forms.py            # WTForms definitions (including dynamic forms)
├── auth/               # Authentication blueprint (HTML forms)
├── main/               # Main application routes
├── inventory/          # Inventory management (with JSON API helpers)
├── members/            # Member management (HTML interface)
├── events/             # Event management (HTML interface)
├── competitions/       # Competition system (HTML interface)
└── templates/          # Jinja2 HTML templates
    ├── base.html       # Base template with navigation
    ├── auth/           # Login/registration forms
    ├── inventory/      # Inventory management pages
    ├── members/        # Member management pages
    ├── events/         # Event management pages
    └── competitions/   # Competition pages including scoring
```

### Key Components

1. **HTML Web Interface**: All primary functionality through web pages
2. **Form-Based Interactions**: Traditional HTML forms with POST/redirect
3. **Session Authentication**: Flask-Login with browser sessions
4. **Dynamic Forms**: JavaScript-enhanced category-specific forms
5. **Bootstrap UI**: Responsive interface with modern design

## Feature Highlights

### Competition System
- **Button-based Scoring**: Numbered buttons (1-10) for each arrow instead of dropdowns
- **JavaScript Enhancement**: Visual feedback and client-side validation
- **Team Management**: Automatic team generation and target assignment
- **Comprehensive Results**: Group and team standings with detailed statistics

### Dynamic Inventory Management
- **Category-specific Forms**: Bow items show handedness, length, draw weight fields
- **JSON API Helpers**: Two endpoints for dynamic field loading
- **Flexible Attributes**: JSON storage for category-specific data
- **Search and Filtering**: HTML-based inventory search

### Event Management
- **Calendar Interface**: Bootstrap-based event calendar
- **Attendance Tracking**: Web forms for member registration
- **Payment Management**: Event fees and charge tracking
- **AJAX Enhancements**: Limited JSON responses for payment updates

## Documentation

### Core Documentation
- [**Web Interface Overview**](documentation/web-interface.md) - Actual HTML routes and forms
- [System Architecture](documentation/README.md) - Complete system overview
- [Database Models](documentation/models.md) - SQLAlchemy model definitions
- [Forms & Validation](documentation/forms.md) - WTForms and dynamic forms

### Feature Documentation  
- [Competition Management](documentation/competitions.md) - Button-based scoring system
- [Inventory System](documentation/inventory.md) - Dynamic category-specific forms
- [Member Management](documentation/members.md) - User administration
- [Event Management](documentation/events.md) - Calendar and attendance
- [Authentication](documentation/authentication.md) - Session-based security

### Development Documentation
- [Views and Routes](documentation/views-and-routes.md) - Flask blueprint routes
- [Templates](documentation/templates.md) - Jinja2 template system
- [Configuration](documentation/configuration.md) - Environment setup
- [Dependencies](documentation/dependencies.md) - Package requirements

### ⚠️ Outdated Documentation
- [~~API Documentation~~](documentation/api.md) - **OUTDATED**: Documents non-existent REST API

## Development

### Running Tests
```bash
python -m pytest
```

### Database Migrations
```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

### Adding New Categories
To add new inventory categories with specific attributes:

1. **Add Category**: Use web interface to create category
2. **Update Form Logic**: Modify `get_category_fields()` in `app/inventory/__init__.py`
3. **Add Form Class**: Create specific form class in `app/forms.py`
4. **Update Templates**: Ensure templates handle new attributes

## Recent Updates

- ✅ **Club Settings Management**: Admin interface for club name, default location, and social links
- ✅ **Auto-populated Event Location**: New events automatically use club's default location
- ✅ **Dynamic Club Branding**: Club name displayed in navbar and page titles
- ✅ **Button-based Competition Scoring**: Replaced dropdowns with numbered buttons
- ✅ **Dynamic Inventory Forms**: Category-specific forms with bow attributes
- ✅ **Documentation Update**: Accurate documentation reflecting web app architecture
- ✅ **Web Interface Documentation**: Complete HTML route documentation
- ✅ **API Status Clarification**: Clear indication of limited JSON API functionality

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make changes and test thoroughly
4. Update documentation as needed
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Note**: This is a web application designed for browser-based interaction. For programmatic integration, consider adding REST API endpoints alongside the existing HTML interface.

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
