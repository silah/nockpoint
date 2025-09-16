# Web Interface Overview

## Architecture Type: HTML Web Application

The Nockpoint system is a **traditional web application** that serves HTML pages and uses form-based interactions. It is **not** a REST API system.

## Authentication Routes (/auth)

### User Registration & Login
- **GET /auth/register** - Registration form page
- **POST /auth/register** - Process registration form 
- **GET /auth/login** - Login form page
- **POST /auth/login** - Process login form (returns HTML redirect)
- **GET /auth/logout** - Logout with redirect

**Response Type**: HTML pages with form redirects

## Main Application Routes (/)

- **GET /** - Home page
- **GET /dashboard** - User dashboard (login required)

## Member Management Routes (/members)

### Member Administration
- **GET /members** - List members page (HTML table)
- **GET /members/new** - New member form
- **POST /members/new** - Create member (HTML form submission)
- **GET /members/member/<int:id>** - View member profile page
- **GET /members/member/<int:id>/edit** - Edit member form
- **POST /members/member/<int:id>/edit** - Update member (form submission)
- **POST /members/member/<int:id>/toggle-status** - Activate/deactivate member
- **POST /members/member/<int:id>/delete** - Delete member
- **GET /members/profile** - Current user profile redirect

**Response Type**: HTML pages with Bootstrap tables and forms

## Event Management Routes (/events)

### Event Calendar & Management
- **GET /events** - Events calendar page (HTML)
- **GET /events/new** - New event form  
- **POST /events/new** - Create event (HTML form)
- **GET /events/event/<int:id>** - View event details page
- **GET /events/event/<int:id>/edit** - Edit event form
- **POST /events/event/<int:id>/edit** - Update event (HTML form)
- **POST /events/event/<int:id>/delete** - Delete event
- **GET /events/event/<int:id>/attendance** - Attendance management page
- **POST /events/event/<int:id>/attendance** - Record attendance (form)
- **GET /events/payments** - Outstanding payments page
- **GET /events/my-charges** - User's charges page

### Limited AJAX Endpoints (JSON Responses)
- **POST /events/mark-paid** - Mark payment as paid (JSON: {success: true})
- **POST /events/update-payment-status** - Update payment status (JSON)
- **POST /events/update-charge-amount** - Update charge amount (JSON)
- **POST /events/delete-charge** - Delete charge (JSON)
- **POST /events/attendance/<int:id>/remove** - Remove attendee (JSON)

## Competition Management Routes (/competitions)

### Competition System
- **GET /competitions** - Competitions list page (HTML)
- **GET /competitions/event/<int:event_id>/create** - Create competition form
- **POST /competitions/event/<int:event_id>/create** - Create competition (form)
- **GET /competitions/<int:id>** - View competition details page
- **GET /competitions/<int:id>/setup-groups** - Setup groups page
- **POST /competitions/<int:id>/setup-groups** - Create competition group
- **POST /competitions/<int:id>/open-registration** - Open registration
- **GET /competitions/<int:id>/register** - Registration form
- **POST /competitions/<int:id>/register** - Register for competition (form)
- **POST /competitions/<int:id>/admin-register** - Admin register member
- **POST /competitions/<int:id>/generate-teams** - Generate teams
- **POST /competitions/<int:id>/start** - Start competition
- **GET /competitions/<int:id>/scoring** - Scoring overview page
- **GET /competitions/<int:id>/score/<int:registration_id>** - Individual scoring form
- **POST /competitions/<int:id>/score/<int:registration_id>** - Submit scores (form)
- **GET /competitions/<int:id>/results** - Results page (HTML)
- **POST /competitions/<int:id>/complete** - Complete competition
- **POST /competitions/<int:id>/delete** - Delete competition
- **POST /competitions/group/<int:group_id>/delete** - Delete group

### Competition Scoring Interface
The competition scoring uses a **button-based interface** with JavaScript:
- Each arrow scored using numbered buttons 1-10
- JavaScript handles button selection and form validation
- Scores submitted via HTML form to Flask route
- Results displayed in HTML tables

## Inventory Management Routes (/inventory)

### Inventory Web Interface
- **GET /inventory** - Inventory items list page (HTML table)
- **GET /inventory/categories** - Categories page (HTML)
- **GET /inventory/categories/new** - New category form
- **POST /inventory/categories/new** - Create category (form)
- **GET /inventory/categories/<int:id>/edit** - Edit category form
- **POST /inventory/categories/<int:id>/edit** - Update category (form)
- **GET /inventory/new** - New item form  
- **POST /inventory/new** - Create item (form submission)
- **GET /inventory/item/<int:id>** - View item details page
- **GET /inventory/item/<int:id>/edit** - Edit item form
- **POST /inventory/item/<int:id>/edit** - Update item (form)
- **POST /inventory/item/<int:id>/delete** - Delete item

### Dynamic Form System (JSON API)
- **GET /inventory/api/category-fields/<int:category_id>** - Get form fields for category (JSON)
- **GET /inventory/api/item-attributes/<int:item_id>** - Get item attributes (JSON)

The inventory system features **dynamic category-specific forms**:
- JavaScript loads form fields based on selected category
- Category-specific attributes (e.g., bow: handedness, length, draw_weight)
- JSON responses provide field definitions for frontend rendering

## Form Handling & Validation

### HTML Form Processing
- **CSRF Protection**: All forms include CSRF tokens
- **Server-Side Validation**: WTForms validation with error messages
- **Flash Messages**: Success/error notifications via Flask flash
- **Redirect Pattern**: POST/redirect/GET pattern for form submissions

### Dynamic Form Fields
- **Category-Specific**: Inventory forms adapt based on item category
- **JavaScript Enhancement**: Dynamic field loading without page refresh
- **JSON Field Storage**: Category attributes stored as JSON in database

## User Interface Components

### Navigation
- **Bootstrap Navbar**: Responsive navigation with dropdowns
- **Role-Based Menus**: Different navigation for admin vs. member users
- **Icons**: Bootstrap Icons for visual enhancement

### Tables & Lists
- **Bootstrap Tables**: Responsive tables with sorting and filtering
- **Pagination**: Server-side pagination for large datasets
- **Search**: HTML form-based search functionality

### Forms
- **Bootstrap Form Styling**: Consistent form styling across application
- **Dynamic Fields**: JavaScript-enhanced forms for inventory management
- **Validation**: Client and server-side validation with error display

## Security & Authentication

### Session-Based Authentication
- **Flask-Login**: Server-side session management
- **Role-Based Access**: Admin and member role separation
- **Login Required**: Protected routes with @login_required decorator
- **CSRF Protection**: All forms protected against CSRF attacks

### Authorization
- **Admin Required**: Admin-only routes with @admin_required decorator
- **User Context**: Template access to current_user information
- **Secure Routes**: All sensitive operations require authentication

## No REST API Implementation

**Important**: The system does **not** implement a REST API:
- No JSON authentication endpoints
- No standardized JSON responses for CRUD operations
- No API versioning or rate limiting
- No API client libraries or SDKs
- No WebSocket or real-time API features

The application is designed as a traditional web application for browser-based interaction, not for programmatic API access.
