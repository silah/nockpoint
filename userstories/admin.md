# Admin User Stories (Current System)

## As an Admin

### Dashboard Access and Overview
- **As an admin**, I want to access the main dashboard to see system statistics and quick actions
- **As an admin**, I want to see inventory metrics (total items, categories) displayed prominently
- **As an admin**, I want to see member statistics (total members, active members) for club oversight
- **As an admin**, I want to see upcoming events count and recent inventory activity
- **As an admin**, I want quick action buttons for creating new items, members, and events

### Member Management
- **As an admin**, I want to create new member accounts with username, email, name, and role assignment
- **As an admin**, I want to view all members with search and filter capabilities (by role and status)
- **As an admin**, I want to edit any member's profile information including personal details
- **As an admin**, I want to promote members to admin role or demote admins to member role
- **As an admin**, I want to activate or deactivate member accounts using toggle functionality
- **As an admin**, I want to permanently delete member accounts when necessary
- **As an admin**, I want protection from deleting my own account or the last admin

### Inventory Management
- **As an admin**, I want to create new inventory items with category-specific attributes
- **As an admin**, I want to edit existing inventory items including all item details
- **As an admin**, I want to delete inventory items when they are no longer needed
- **As an admin**, I want to create new inventory categories with names and descriptions
- **As an admin**, I want to edit category information and category-specific attributes
- **As an admin**, I want to manage category attributes (specific fields for bows, arrows, targets)

### Event Management
- **As an admin**, I want to create shooting events with date, time, location, and pricing
- **As an admin**, I want to edit event details including all event information
- **As an admin**, I want to delete events and all associated data when necessary
- **As an admin**, I want to manage event attendance including adding walk-in participants
- **As an admin**, I want to mark attendance and automatically create charges for paid events
- **As an admin**, I want to remove attendees from events when needed

### Competition Management
- **As an admin**, I want to create competitions linked to existing events
- **As an admin**, I want to set up competition groups and parameters (rounds, arrows, team size)
- **As an admin**, I want to open registration and register members for competitions
- **As an admin**, I want to generate balanced teams with automatic target assignment
- **As an admin**, I want to start competitions and access the scoring interface
- **As an admin**, I want to record arrow-by-arrow scores for all participants
- **As an admin**, I want to complete competitions with automatic score completion

### Payment Management
- **As an admin**, I want to view all outstanding member charges across the system
- **As an admin**, I want to search and filter charges by member, event, or payment status
- **As an admin**, I want to mark charges as paid when payment is received
- **As an admin**, I want to update charge amounts and add payment notes
- **As an admin**, I want to delete charges when necessary

### Navigation and Access Control
- **As an admin**, I want admin-only navigation items visible in the interface
- **As an admin**, I want admin action buttons available on relevant pages
- **As an admin**, I want clear visual indicators (badges) showing my admin status
- **As an admin**, I want access to all system functionality without restrictions

## Current System Implementation

### Admin Dashboard Functionality
The main dashboard (`/dashboard`) provides admin users with:
1. **Statistics Cards**: Total items, categories, members, active members, upcoming events
2. **Recent Activity**: Latest 5 inventory items added to the system  
3. **Quick Actions**: Admin-only buttons for creating items, members, events, managing payments
4. **System Status**: User role display, member since date, version information

### Admin Role Implementation
- **Role Assignment**: Binary admin/member role system with `is_admin()` method
- **Access Control**: `@admin_required` decorator protects administrative functions
- **Permission Checking**: Template-level role checking for conditional content display
- **Session Management**: Standard Flask-Login session handling with role persistence

### Administrative Functions Available
- **Member Management**: Full CRUD operations on user accounts with role management
- **Inventory Management**: Complete item and category management with custom attributes
- **Event Management**: Full event lifecycle including attendance and payment processing
- **Competition Management**: Complete competition workflow from creation to completion
- **Payment Management**: Comprehensive charge management with search and status updates

### User Interface (Current Admin Pages)
- **Dashboard** (`/dashboard`): Central admin hub with statistics and quick actions
- **Member Management** (`/members/`): Directory with admin controls for all members
- **Inventory Management** (`/inventory/`): Item listing with admin creation/edit controls
- **Category Management** (`/inventory/categories`): Admin-only category management
- **Event Management** (`/events/`): Event calendar with admin creation/edit controls  
- **Competition Management** (`/competitions/`): Competition listing with full admin workflow
- **Payment Management** (`/events/payments`): Outstanding payments dashboard

### Access Control (Current System)
- **Route Protection**: Admin routes protected with `@admin_required` decorator
- **Template Controls**: Admin-only content conditionally displayed based on role
- **Navigation**: Admin-specific menu items and action buttons
- **Error Handling**: 403 Forbidden responses for unauthorized access attempts

### Key Features Not Implemented
The current admin system does NOT include:
- System-wide settings or configuration management
- Audit logging or administrative action tracking
- User activity monitoring or security alerts
- Data export/import functionality
- Bulk operations or batch processing
- System health monitoring or performance metrics
- Advanced reporting or analytics dashboards
- Email notifications or communication systems
- Database backup/restore through the interface
- Multi-factor authentication for admin accounts
