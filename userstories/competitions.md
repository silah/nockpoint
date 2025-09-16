# Competition User Stories (Current System)

## As a Club Member

### Competition Discovery
- **As a member**, I want to view a list of all upcoming competitions (next 60 days) so I can plan my participation
- **As a member**, I want to see past competitions (last 10) to review what competitions have been held
- **As a member**, I want to view competition details including format, number of rounds, arrows per round, and target size
- **As a member**, I want to see which event a competition is associated with including date, time and location

### Competition Registration
- **As a member**, I want to register for competitions when registration is open
- **As a member**, I want to select which group/division I want to compete in during registration
- **As a member**, I want to add optional notes when registering for a competition
- **As a member**, I want to see if I'm already registered for a competition to avoid duplicate registrations
- **As a member**, I want to see my registration status and group assignment on the competition page

### Viewing Competition Status
- **As a member**, I want to see the current status of competitions (setup, registration_open, in_progress, completed)
- **As a member**, I want to see how many total participants are registered
- **As a member**, I want to see participants organized by groups with team assignments
- **As a member**, I want to view competition results once the competition is completed or in progress

### Results Viewing
- **As a member**, I want to view final competition results organized by group
- **As a member**, I want to see individual rankings within each group sorted by total score
- **As a member**, I want to see each participant's total score, completed rounds, and completion status
- **As a member**, I want to see team assignments and target numbers in the results

## As an Admin

### Competition Creation and Setup
- **As an admin**, I want to create competitions for existing shooting events
- **As an admin**, I want to configure competition parameters including number of rounds, arrows per round, target size, and max team size
- **As an admin**, I want to prevent creating multiple competitions for the same event
- **As an admin**, I want to set up competition groups with names, descriptions, and optional age limits
- **As an admin**, I want to delete competition groups that have no registered participants

### Registration Management  
- **As an admin**, I want to open registration for competitions only after groups are created
- **As an admin**, I want to register members for competitions on their behalf
- **As an admin**, I want to see available unregistered members when doing admin registration
- **As an admin**, I want to assign members to specific groups during admin registration

### Team Management
- **As an admin**, I want to automatically generate balanced teams based on registered participants
- **As an admin**, I want the system to create optimal team distribution with balanced member counts
- **As an admin**, I want to assign unique target numbers to each team
- **As an admin**, I want to regenerate teams if needed (deletes existing teams and creates new ones)

### Competition Workflow Control
- **As an admin**, I want to start competitions only after teams have been generated
- **As an admin**, I want the system to change status from 'registration_open' to 'in_progress' when starting
- **As an admin**, I want to prevent starting competitions that don't have teams set up

### Score Recording and Management
- **As an admin**, I want to access a scoring interface that shows all registered participants
- **As an admin**, I want to see completion statistics including total participants and completed participants
- **As an admin**, I want to record scores for individual participants round by round
- **As an admin**, I want to enter arrow-by-arrow scores with point values (0-10) and X-ring designation
- **As an admin**, I want the system to automatically calculate running totals and round completion
- **As an admin**, I want to validate that all arrow scores are entered correctly before saving

### Competition Completion
- **As an admin**, I want to complete competitions and have the system automatically fill missing arrows with 0-point scores
- **As an admin**, I want to see how many arrows were auto-filled when completing a competition
- **As an admin**, I want the competition status to change to 'completed' when finished
- **As an admin**, I want to complete competitions even if some participants haven't finished scoring

### Competition Management
- **As an admin**, I want to delete competitions and all associated data
- **As an admin**, I want to view upcoming events without competitions in a dropdown for easy competition creation
- **As an admin**, I want to access all competition management functions through a clean administrative interface
## Current System Implementation

### Competition Workflow (Current State)
The competition system follows this workflow:
1. **Setup**: Admin creates competition linked to an event and defines groups
2. **Registration Open**: Admin opens registration, members and admin can register participants  
3. **Team Generation**: Admin creates balanced teams with automatic target assignment
4. **In Progress**: Admin starts competition and can record scores round-by-round
5. **Completed**: Admin completes competition with automatic 0-fill for missing arrows

### Technical Architecture (Current Implementation)
- **Database Models**: Competition, CompetitionGroup, CompetitionTeam, CompetitionRegistration, ArrowScore
- **Scoring System**: Round-by-round arrow entry with points (0-10) and X-ring tracking
- **Team Balancing**: Smart algorithm distributes members evenly across teams
- **Results Calculation**: Automatic ranking by total score within groups
- **Competition States**: setup → registration_open → in_progress → completed

### User Interface (Current Pages)
- **Competition List** (`/competitions/`): Shows upcoming and past competitions
- **Competition View** (`/competitions/<id>`): Details, registration, and management
- **Group Setup** (`/competitions/<id>/setup-groups`): Admin creates competition groups  
- **Registration** (`/competitions/<id>/register`): Member self-registration
- **Scoring Interface** (`/competitions/<id>/scoring`): Admin scoring overview
- **Individual Scoring** (`/competitions/<id>/score/<registration_id>`): Round-by-round score entry
- **Results** (`/competitions/<id>/results`): Final rankings by group

### Access Control (Current System)
- **Members**: Can view competitions, register, view results
- **Admins**: Full competition management, scoring, team generation, completion
- **Authentication**: All competition functions require login
- **Authorization**: Admin functions protected with `@admin_required` decorator

### Key Features Not Implemented
The current system does NOT include:
- Payment processing for competition fees
- Equipment requirements or verification
- Advanced analytics or historical tracking  
- Real-time leaderboards during competition
- Certificate generation or awards processing
- Integration with external archery organizations
- Mobile applications or offline capability
- Competition scheduling or calendar integration
- Communication systems or notifications
- Live scoring updates or spectator views
