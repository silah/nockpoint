# Events User Stories (Current System)

## As a Club Member

### Event Calendar Access
- **As a member**, I want to view all upcoming events in a calendar format so I can plan my participation
- **As a member**, I want to see past events (last 10) to review what activities have been held
- **As a member**, I want to see event details including name, date, time, location, duration, price, and participant limits
- **As a member**, I want to see who attended past events with attendee lists

### Event Information Viewing
- **As a member**, I want to view detailed event information including description and maximum participants
- **As a member**, I want to see the current attendance count and who has registered for upcoming events
- **As a member**, I want to see if an event has an associated competition with registration details
- **As a member**, I want to view my own attendance history for events

### Personal Charges and Payments
- **As a member**, I want to view all my outstanding charges from events I attended
- **As a member**, I want to see payment details including event name, amount, and payment status
- **As a member**, I want to see charges automatically created when I attend paid events
- **As a member**, I want to see when charges have been marked as paid by administrators

## As an Admin

### Event Creation and Management
- **As an admin**, I want to create new shooting events with all necessary details (name, description, location, date, time, duration, price, max participants)
- **As an admin**, I want to edit existing events to update any event information
- **As an admin**, I want to delete events and all associated attendance/charge records
- **As an admin**, I want to see which user created each event for administrative tracking

### Attendance Management
- **As an admin**, I want to manage event attendance through a dedicated attendance interface
- **As an admin**, I want to see all registered attendees with their attendance status (attended/not attended)
- **As an admin**, I want to mark individual attendees as having attended the event
- **As an admin**, I want to add walk-in attendees who weren't pre-registered
- **As an admin**, I want to remove attendees from events when necessary
- **As an admin**, I want to see attendance statistics (total registered vs. actually attended)

### Financial Management
- **As an admin**, I want to view all outstanding payments across all members and events
- **As an admin**, I want to search and filter charges by member name, event, or payment status
- **As an admin**, I want to mark charges as paid when payment is received
- **As an admin**, I want to update charge amounts and add notes explaining changes
- **As an admin**, I want to delete charges when necessary
- **As an admin**, I want automatic charge creation when marking paid event attendance

### Event-Attendance Integration
- **As an admin**, I want attendance marking to automatically create charges for paid events
- **As an admin**, I want to see total money collected from event attendance
- **As an admin**, I want walk-in registration to create both attendance and charge records
- **As an admin**, I want the system to prevent duplicate charges for the same member/event combination

## Current System Implementation

### Event Management Workflow
1. **Event Creation**: Admin creates events with complete details including pricing
2. **Attendance Tracking**: Admin manages who attended each event through attendance interface
3. **Automatic Charging**: System creates charges when members attend paid events
4. **Payment Management**: Admin tracks and marks payments as received
5. **Event History**: All members can view event calendar and attendance history

### Technical Architecture (Current Implementation)
- **Database Models**: ShootingEvent, EventAttendance, MemberCharge with proper relationships
- **Attendance System**: Manual admin tracking with automatic charge generation
- **Payment Integration**: Simple charge tracking with paid/unpaid status and notes
- **Event Calendar**: Chronological display of upcoming and past events
- **Access Control**: Member viewing, admin full management

### User Interface (Current Pages)
- **Events Calendar** (`/events/`): Lists upcoming and past events for all users
- **Event Details** (`/events/event/<id>`): Shows event info, attendees, and admin controls
- **Event Form** (`/events/new`, `/events/event/<id>/edit`): Admin event creation/editing
- **Attendance Management** (`/events/event/<id>/attendance`): Admin attendance interface
- **Payment Dashboard** (`/events/payments`): Admin view of all outstanding charges
- **Personal Charges** (`/events/my-charges`): Member view of their own charges

### Payment System (Current Implementation)
- **Charge Creation**: Automatic when marking attendance for paid events
- **Payment Tracking**: Admin marks charges as paid with optional notes
- **Search and Filter**: Admin can find charges by member or event name
- **Amount Updates**: Admin can modify charge amounts with reason tracking
- **Status Updates**: Simple paid/unpaid boolean with payment notes

### Attendance Features (Current System)
- **Event Attendance List**: Shows all attendees with attendance status
- **Walk-in Registration**: Admin can add unregistered members to events
- **Attendance Marking**: Toggle attendance status for each registered member
- **Statistics Display**: Shows attended vs. registered counts
- **Automatic Integration**: Links attendance to charge creation for paid events

### Access Control (Current System)
- **Members**: Can view events calendar, event details, their own charges
- **Admins**: Full event management, attendance tracking, payment management
- **Authentication**: All event functions require login with `@login_required`
- **Authorization**: Admin functions protected with `@admin_required` decorator

### Key Features Not Implemented
The current event system does NOT include:
- Online event registration by members (admin-only attendance management)
- Event categories, filtering, or search functionality
- Integration with external calendars or calendar exports
- Event templates or recurring event creation
- Automated notifications or reminders about events
- Event capacity enforcement or waitlists
- Member self-service event registration
- Event feedback or rating systems
- Photo sharing or event documentation features
- Integration with external venue or equipment booking systems
