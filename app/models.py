from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')  # 'admin' or 'member'
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class InventoryCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with inventory items
    items = db.relationship('InventoryItem', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<InventoryCategory {self.name}>'

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(20), default='piece')  # piece, set, pair, etc.
    location = db.Column(db.String(100))  # Storage location
    purchase_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(10, 2))
    condition = db.Column(db.String(20), default='good')  # good, fair, poor, damaged
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign key to category
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_category.id'), nullable=False)
    
    # Specific attributes for different categories (JSON field for flexibility)
    attributes = db.Column(db.JSON)  # Store category-specific attributes
    
    def __repr__(self):
        return f'<InventoryItem {self.name}>'

# Sample category-specific attributes structure:
# For Bows: {"draw_weight": 45, "draw_length": 28, "bow_type": "recurve", "handedness": "right"}
# For Arrows: {"spine": 500, "length": 30, "point_weight": 125, "fletching_type": "feather"}
# For Targets: {"face_size": 122, "target_type": "10-ring", "material": "straw"}
# For Safety Equipment: {"size": "large", "material": "leather", "certification": "CE"}

class ShootingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration_hours = db.Column(db.Integer, nullable=False, default=2)  # Duration in hours
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    max_participants = db.Column(db.Integer)  # Optional capacity limit
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    attendances = db.relationship('EventAttendance', backref='event', lazy=True, cascade='all, delete-orphan')
    creator = db.relationship('User', backref='created_events')
    
    def __repr__(self):
        return f'<ShootingEvent {self.name}>'
    
    @property
    def end_time(self):
        """Calculate end time based on start time and duration"""
        from datetime import timedelta
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = start_datetime + timedelta(hours=self.duration_hours)
        return end_datetime.time()
    
    @property
    def is_past(self):
        """Check if the event is in the past"""
        event_datetime = datetime.combine(self.date, self.start_time)
        return event_datetime < datetime.now()
    
    @property
    def attendance_count(self):
        """Get number of attendees"""
        return len(self.attendances)

class EventAttendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # When registered for event
    attended_at = db.Column(db.DateTime, nullable=True)  # When actually attended (None if not attended)
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notes = db.Column(db.Text)  # Optional notes about attendance
    
    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], backref='event_attendances')
    recorder = db.relationship('User', foreign_keys=[recorded_by])
    
    # Unique constraint to prevent duplicate attendance
    __table_args__ = (db.UniqueConstraint('event_id', 'member_id', name='unique_event_attendance'),)
    
    def __repr__(self):
        return f'<EventAttendance {self.member.username} at {self.event.name}>'
    
    @property
    def attended(self):
        """Check if member actually attended (not just registered)"""
        return self.attended_at is not None
    
    @property
    def charge(self):
        """Get the associated charge for this attendance"""
        return MemberCharge.query.filter_by(
            member_id=self.member_id,
            event_id=self.event_id
        ).first()
    
    @property
    def attended(self):
        """Check if member actually attended (has attended_at timestamp)"""
        return self.attended_at is not None
    
    @property
    def charge(self):
        """Get the charge associated with this attendance"""
        return MemberCharge.query.filter_by(
            member_id=self.member_id,
            event_id=self.event_id
        ).first()

class MemberCharge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=True)  # Null for non-event charges
    description = db.Column(db.String(500), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    charge_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_paid = db.Column(db.Boolean, default=False)
    paid_date = db.Column(db.DateTime)
    paid_by_admin = db.Column(db.Integer, db.ForeignKey('user.id'))  # Admin who marked as paid
    payment_notes = db.Column(db.Text)
    
    # Relationships
    member = db.relationship('User', foreign_keys=[member_id], backref='charges')
    event = db.relationship('ShootingEvent', backref='charges')
    admin = db.relationship('User', foreign_keys=[paid_by_admin])
    
    def __repr__(self):
        return f'<MemberCharge {self.member.username}: ${self.amount}>'

# Competition Models

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=False)
    number_of_rounds = db.Column(db.Integer, nullable=False, default=6)
    target_size_cm = db.Column(db.Integer, nullable=False, default=122)  # Target face size in cm
    arrows_per_round = db.Column(db.Integer, nullable=False, default=6)
    max_team_size = db.Column(db.Integer, nullable=False, default=4)  # Can be 3 or 4
    status = db.Column(db.String(20), nullable=False, default='setup')  # setup, registration_open, in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    event = db.relationship('ShootingEvent', backref='competition')
    creator = db.relationship('User', backref='created_competitions')
    groups = db.relationship('CompetitionGroup', backref='competition', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('CompetitionRegistration', backref='competition', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Competition for {self.event.name}>'
    
    @property
    def total_arrows(self):
        """Calculate total arrows per archer"""
        return self.number_of_rounds * self.arrows_per_round
    
    @property
    def max_possible_score(self):
        """Calculate maximum possible score (assuming 10 points per arrow)"""
        return self.total_arrows * 10
    
    @property
    def registration_count(self):
        """Get total number of registered participants"""
        return len(self.registrations)
    
    def get_results_by_group(self):
        """Get competition results organized by group"""
        results = {}
        for group in self.groups:
            group_registrations = [r for r in self.registrations if r.group_id == group.id]
            # Sort by total score descending
            group_registrations.sort(key=lambda x: x.total_score, reverse=True)
            results[group.name] = group_registrations
        return results
    
    def get_completion_stats(self):
        """Get completion statistics for the competition"""
        if not self.registrations:
            return {
                'total_participants': 0,
                'completed_participants': 0,
                'completion_percentage': 0,
                'missing_arrows_total': 0
            }
        
        total_participants = len(self.registrations)
        completed_participants = sum(1 for reg in self.registrations if reg.is_complete)
        missing_arrows_total = sum(
            max(0, self.total_arrows - len(reg.arrow_scores)) 
            for reg in self.registrations
        )
        
        return {
            'total_participants': total_participants,
            'completed_participants': completed_participants,
            'completion_percentage': (completed_participants / total_participants * 100) if total_participants > 0 else 0,
            'missing_arrows_total': missing_arrows_total
        }

class CompetitionGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g., "Adults", "Juniors", "Seniors"
    description = db.Column(db.Text)
    min_age = db.Column(db.Integer)  # Optional age restrictions
    max_age = db.Column(db.Integer)  # Optional age restrictions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teams = db.relationship('CompetitionTeam', backref='group', lazy=True, cascade='all, delete-orphan')
    registrations = db.relationship('CompetitionRegistration', backref='group', lazy=True)
    
    def __repr__(self):
        return f'<CompetitionGroup {self.name}>'
    
    @property
    def participant_count(self):
        """Get number of participants in this group"""
        return len(self.registrations)
    
    @property
    def team_count(self):
        """Get number of teams in this group"""
        return len(self.teams)

class CompetitionTeam(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('competition_group.id'), nullable=False)
    team_number = db.Column(db.Integer, nullable=False)  # Team 1, 2, 3, etc. within the group
    target_number = db.Column(db.Integer, nullable=False)  # Target assignment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('CompetitionRegistration', backref='team', lazy=True)
    
    # Unique constraint: one team number per group
    __table_args__ = (db.UniqueConstraint('group_id', 'team_number', name='unique_team_per_group'),)
    
    def __repr__(self):
        return f'<CompetitionTeam {self.group.name} Team {self.team_number}>'
    
    @property
    def member_count(self):
        """Get number of members in this team"""
        return len(self.registrations)
    
    @property
    def team_total_score(self):
        """Calculate total score for all team members"""
        return sum(reg.total_score for reg in self.registrations)
    
    @property
    def team_average_score(self):
        """Calculate average score per team member"""
        if self.member_count == 0:
            return 0
        return self.team_total_score / self.member_count

class CompetitionRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('competition_group.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('competition_team.id'), nullable=True)  # Assigned when teams are created
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    
    # Relationships
    member = db.relationship('User', backref='competition_registrations')
    arrow_scores = db.relationship('ArrowScore', backref='registration', lazy=True, cascade='all, delete-orphan')
    
    # Unique constraint: one registration per member per competition
    __table_args__ = (db.UniqueConstraint('competition_id', 'member_id', name='unique_member_per_competition'),)
    
    def __repr__(self):
        return f'<CompetitionRegistration {self.member.username} in {self.competition.event.name}>'
    
    @property
    def total_score(self):
        """Calculate total score from all arrows"""
        return sum(score.points for score in self.arrow_scores)
    
    @property
    def completed_rounds(self):
        """Get number of completed rounds"""
        total_arrows = len(self.arrow_scores)
        return total_arrows // self.competition.arrows_per_round
    
    @property
    def is_complete(self):
        """Check if all rounds are completed"""
        expected_arrows = self.competition.total_arrows
        return len(self.arrow_scores) >= expected_arrows
    
    def get_round_score(self, round_number):
        """Get score for a specific round (1-indexed)"""
        start_arrow = (round_number - 1) * self.competition.arrows_per_round
        end_arrow = start_arrow + self.competition.arrows_per_round
        
        round_arrows = [score for score in self.arrow_scores 
                       if start_arrow < score.arrow_number <= end_arrow]
        return sum(score.points for score in round_arrows)
    
    def get_round_scores(self):
        """Get scores for all rounds"""
        scores = []
        for round_num in range(1, self.competition.number_of_rounds + 1):
            scores.append(self.get_round_score(round_num))
        return scores

class ArrowScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    registration_id = db.Column(db.Integer, db.ForeignKey('competition_registration.id'), nullable=False)
    arrow_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3... up to total_arrows
    points = db.Column(db.Integer, nullable=False)  # 0-10 points per arrow
    is_x = db.Column(db.Boolean, default=False)  # Inner X ring (for tie-breaking)
    round_number = db.Column(db.Integer, nullable=False)  # Which round this arrow belongs to
    recorded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # Optional notes about the shot
    
    # Relationships
    recorder = db.relationship('User', backref='recorded_arrow_scores')
    
    # Unique constraint: one score per arrow per registration
    __table_args__ = (db.UniqueConstraint('registration_id', 'arrow_number', name='unique_arrow_per_registration'),)
    
    def __repr__(self):
        return f'<ArrowScore {self.points} points for arrow {self.arrow_number}>'
    
    @property
    def is_bullseye(self):
        """Check if this is a bullseye (10 points)"""
        return self.points == 10
    
    @property
    def is_inner_ring(self):
        """Check if this hit the inner ring (9 or 10 points)"""
        return self.points >= 9
