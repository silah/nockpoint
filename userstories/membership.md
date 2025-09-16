# Member Management User Stories (Current System)

## As a Club Member

### Profile Access and Viewing
- **As a member**, I want to view my own profile information so I can see my account details
- **As a member**, I want to see my basic information including name, username, email, role, and account status
- **As a member**, I want to see when I joined the club as a "member since" date
- **As a member**, I want to access my profile through a profile shortcut (`/members/profile`) that redirects to my profile page
- **As a member**, I want to be prevented from viewing other members' detailed profiles (non-admins see access denied)

### Profile Editing (Self-Service)
- **As a member**, I want to edit my own profile information (name, email, password) so I can keep it current
- **As a member**, I want the system to validate that my email is unique when I change it
- **As a member**, I want the system to validate that my username is unique when I change it
- **As a member**, I want to optionally update my password during profile editing
- **As a member**, I want to be restricted from changing my own role or account status

### Member Directory Access
- **As a member**, I want to view a directory of all club members with pagination (20 members per page)
- **As a member**, I want to search for members by name, username, or email
- **As a member**, I want to filter the member list by role (all/admin/member) or status (all/active/inactive)
- **As a member**, I want to see basic member information including name, role badge, and member since date
- **As a member**, I want to see member statistics (total members, active members, admin count) at the top

## As an Admin

### Member Creation
- **As an admin**, I want to create new member accounts through a dedicated form
- **As an admin**, I want to set basic member information (username, email, first/last name, password)
- **As an admin**, I want to assign admin role during member creation with a checkbox
- **As an admin**, I want the system to prevent duplicate usernames and emails during creation
- **As an admin**, I want to be redirected to the new member's profile after successful creation

### Member Profile Management
- **As an admin**, I want to view any member's detailed profile information
- **As an admin**, I want to edit any member's profile information through the same form interface
- **As an admin**, I want to change member roles (promote to admin or remove admin privileges)
- **As an admin**, I want to change member account status (activate/deactivate accounts)
- **As an admin**, I want to reset or update member passwords when needed

### Member Directory Administration
- **As an admin**, I want the same search and filter capabilities as regular members
- **As an admin**, I want to see additional management controls on member cards
- **As an admin**, I want quick access to view and edit functions for each member
- **As an admin**, I want to see all members including inactive ones when filtering

### Account Status Management
- **As an admin**, I want to toggle member account status (activate/deactivate) with POST requests
- **As an admin**, I want the system to prevent deactivating the last active admin
- **As an admin**, I want status changes to show clear success messages
- **As an admin**, I want to completely delete member accounts when necessary

### Member Deletion
- **As an admin**, I want to permanently delete member accounts (hard delete from database)
- **As an admin**, I want the system to prevent me from deleting my own account
- **As an admin**, I want the system to prevent deletion of the last active admin
- **As an admin**, I want deletion to redirect back to the member directory with confirmation

## Current System Implementation

### Member Management Workflow
1. **Admin Creates Members**: Admin uses `/members/new` to create accounts with role assignment
2. **Member Profile Access**: Members view own profiles, admins view any profile
3. **Profile Editing**: Both members and admins can edit profiles with role-appropriate permissions
4. **Status Management**: Admins can activate/deactivate accounts and delete members entirely
5. **Directory Browsing**: All users can search/filter the member directory with pagination

### Technical Architecture (Current Implementation)
- **Database Model**: Single `User` model with role and status fields
- **Role System**: Binary admin/member roles with `is_admin()` method
- **Account Status**: Boolean `is_active` field for soft activation/deactivation  
- **Authentication**: Integration with Flask-Login for session management
- **Access Control**: `@admin_required` decorator protects administrative functions

### User Interface (Current Pages)
- **Member Directory** (`/members/`): Paginated list with search/filter controls
- **Member Profile** (`/members/member/<id>`): Detailed view with admin controls
- **Create Member** (`/members/new`): Admin form for new member creation
- **Edit Member** (`/members/member/<id>/edit`): Profile editing with role-appropriate fields
- **Profile Shortcut** (`/members/profile`): Redirects to current user's profile

### Access Control (Current System)
- **Members**: Can view directory, own profile, edit own profile only
- **Admins**: Full member management, can create/edit/delete/status change any member
- **Self-Protection**: Users cannot delete own accounts, cannot remove last admin
- **Authentication**: All member functions require login with `@login_required`

### Key Features Not Implemented
The current system does NOT include:
- Member communication or messaging systems
- Activity tracking or engagement metrics
- Member export functionality or reporting
- Email verification for profile changes
- Member photo/avatar upload capabilities
- Advanced member categories or groups beyond admin/member
- Member onboarding workflows or welcome emails
- Integration with external member databases
- Audit logs of member changes or administrative actions
- Member self-registration (only admin can create accounts)
