# Competition Management System

## Overview

The Competition Management System provides comprehensive functionality for organizing and managing archery competitions within the club. It supports multiple competition formats, team management, scoring systems, and results tracking.

## Key Features

### 1. Competition Setup
- **Event Integration**: Competitions are linked to shooting events
- **Flexible Configuration**: Customizable rounds, arrows per round, and target sizes
- **Team Management**: Support for teams of 3-4 members
- **Group Categories**: Age-based or skill-based groupings (Adults, Juniors, Seniors)

### 2. Competition Lifecycle
- **Setup Phase**: Create competition, configure parameters
- **Registration Open**: Accept participant registrations and organize into groups
- **Team Generation**: Automatic team assignment with target allocation
- **In Progress**: Live scoring and progress tracking
- **Completed**: Final results with comprehensive statistics

### 3. Scoring System
- **Individual Arrow Scoring**: 0-10 points per arrow with X-ring tracking
- **Round-based Progress**: Track completion across multiple rounds
- **Real-time Calculations**: Automatic score totals and progress indicators
- **Auto-completion**: Fill missing arrows with 0-point scores when competition ends

### 4. Results & Analytics
- **Group-based Results**: Rankings within each competition group
- **Team Standings**: Combined team scores and averages
- **Individual Performance**: Detailed scoring breakdown per participant
- **Completion Statistics**: Progress tracking and missing arrow counts

## Database Models

### Competition
```python
class Competition(db.Model):
    # Core configuration
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'))
    number_of_rounds = db.Column(db.Integer, default=6)
    target_size_cm = db.Column(db.Integer, default=122)
    arrows_per_round = db.Column(db.Integer, default=6)
    max_team_size = db.Column(db.Integer, default=4)
    status = db.Column(db.String(20), default='setup')
```

**Status Values:**
- `setup`: Initial creation, parameters being configured
- `registration_open`: Accepting participant registrations
- `in_progress`: Competition active, scoring in progress
- `completed`: Competition finished, results finalized

### CompetitionGroup
Age or skill-based categories within a competition:
```python
class CompetitionGroup(db.Model):
    name = db.Column(db.String(100))  # "Adults", "Juniors", "Seniors"
    min_age = db.Column(db.Integer)   # Optional age restrictions
    max_age = db.Column(db.Integer)   # Optional age restrictions
```

### CompetitionTeam
Teams within groups for collaborative scoring:
```python
class CompetitionTeam(db.Model):
    group_id = db.Column(db.Integer, db.ForeignKey('competition_group.id'))
    team_number = db.Column(db.Integer)  # Team 1, 2, 3, etc.
    target_number = db.Column(db.Integer)  # Target assignment
```

### CompetitionRegistration
Individual participant entries:
```python
class CompetitionRegistration(db.Model):
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'))
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('competition_group.id'))
    team_id = db.Column(db.Integer, db.ForeignKey('competition_team.id'))
```

### ArrowScore
Individual arrow scoring records:
```python
class ArrowScore(db.Model):
    registration_id = db.Column(db.Integer, db.ForeignKey('competition_registration.id'))
    arrow_number = db.Column(db.Integer)  # Sequential arrow number
    points = db.Column(db.Integer)        # 0-10 points
    is_x = db.Column(db.Boolean)          # Inner X-ring hit
    round_number = db.Column(db.Integer)  # Which round
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
```

## Competition Flow

### 1. Competition Creation
1. Admin creates competition linked to shooting event
2. Configure rounds, arrows per round, target size
3. Set maximum team size (3 or 4 members)

### 2. Group Setup
1. Create competition groups (e.g., "Adults", "Juniors")
2. Set age restrictions if applicable
3. Groups organize participants for fair competition

### 3. Registration Phase
1. Competition status set to `registration_open`
2. Members can register for competition
3. Admin assigns participants to appropriate groups

### 4. Team Generation
1. Algorithm distributes group members into teams
2. Teams assigned to specific targets
3. Ensures balanced team sizes within max_team_size

### 5. Competition Start
1. Status changed to `in_progress`
2. Scoring interface becomes available
3. Teams shoot at assigned targets

### 6. Scoring Process
1. Admins access scoring management interface
2. Individual participant scoring forms available
3. Real-time progress tracking and validation
4. Round-by-round score entry with X-ring tracking

### 7. Competition Completion
1. Admin marks competition as `completed`
2. Missing arrows automatically filled with 0-point scores
3. Final results calculated and rankings determined

## Scoring Rules

### Arrow Scoring
- **Points Range**: 0-10 points per arrow
- **X-Ring**: Inner ring of 10-point zone (for tie-breaking)
- **Validation**: Client-side and server-side score validation

### Round Calculation
- **Total per Round**: Sum of all arrows in the round
- **Maximum per Round**: arrows_per_round × 10 points
- **Progress Tracking**: Completed rounds vs. total rounds

### Competition Totals
- **Individual Total**: Sum of all arrow scores
- **Team Total**: Sum of all team member scores
- **Team Average**: Team total ÷ number of team members

## User Interface Components

### Competition List (`/competitions`)
- Upcoming and past competitions
- Status indicators and quick actions
- Admin creation tools

### Competition View (`/competitions/<id>`)
- Competition details and configuration
- Participant lists and team assignments
- Status-based action menus (Start, Complete, Delete)

### Scoring Management (`/competitions/<id>/scoring`)
- Overview of all participants and progress
- Quick access to individual scoring
- Completion statistics and missing arrow tracking
- Competition completion controls

### Individual Scoring (`/competitions/<id>/score/<registration_id>`)
- Round-by-round arrow score entry
- Real-time total calculation
- X-ring selection with auto-handling for 10-point shots
- Form validation and progress saving

### Results View (`/competitions/<id>/results`)
- Group-based rankings
- Individual and team standings
- Score breakdowns and statistics

## Security & Access Control

### Admin Functions
- Create and configure competitions
- Manage groups and teams
- Access all scoring interfaces
- Complete competitions
- Delete competitions

### Member Functions
- View competition listings
- View results and standings
- Register for competitions (when registration open)

### Data Validation
- Score range validation (0-10)
- Unique arrow scoring per participant
- Proper round number calculation
- CSRF protection on all forms

## API Endpoints

### Competition Management
- `GET /competitions` - List all competitions
- `POST /competitions` - Create new competition
- `GET /competitions/<id>` - View competition details
- `POST /competitions/<id>/start` - Start competition
- `POST /competitions/<id>/complete` - Complete competition
- `DELETE /competitions/<id>` - Delete competition

### Group & Team Management
- `GET /competitions/<id>/groups` - Setup groups
- `POST /competitions/<id>/generate-teams` - Generate teams
- `POST /competitions/<id>/register` - Register participant

### Scoring System
- `GET /competitions/<id>/scoring` - Scoring management
- `GET /competitions/<id>/score/<reg_id>` - Individual scoring
- `POST /competitions/<id>/score/<reg_id>` - Submit scores

### Results & Data
- `GET /competitions/<id>/results` - Competition results
- `GET /competitions/<id>/export` - Export competition data

## Integration Points

### Event System Integration
- Competitions linked to ShootingEvent records
- Event attendance can trigger competition registration
- Event pricing may include competition fees

### Member Management Integration
- User roles control competition access
- Member profiles provide participant information
- Competition history tracked per member

### Charge System Integration
- Competition fees can generate MemberCharge records
- Payment tracking for competition participation
- Admin controls for fee management

## Testing Strategy

### Unit Tests
- Model methods and property calculations
- Score validation and round calculations
- Team generation algorithms
- Completion statistics accuracy

### Integration Tests
- End-to-end competition workflow
- Multi-user scoring scenarios
- Data consistency across operations
- Security and access control validation

### Manual Testing Scenarios
- Complete competition lifecycle from creation to results
- Multiple participants scoring simultaneously
- Edge cases: incomplete scoring, competition abandonment
- User experience across different roles and devices

## Performance Considerations

### Database Optimization
- Proper indexing on foreign keys
- Efficient queries for large participant lists
- Bulk operations for team generation

### UI Performance
- Real-time score calculations using JavaScript
- Minimal server round-trips for scoring updates
- Progressive loading for large competition lists

### Scalability
- Support for competitions with 100+ participants
- Efficient team generation algorithms
- Optimized results calculation for large datasets
