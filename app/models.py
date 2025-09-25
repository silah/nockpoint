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
    membership_type = db.Column(db.String(20), nullable=False, default='monthly')  # 'annual', 'quarterly', 'monthly', 'per_event'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_membership_price(self):
        """Get the price for this user's membership type"""
        from app.models import ClubSettings
        settings = ClubSettings.get_settings()
        
        if self.membership_type == 'annual':
            return settings.annual_membership_price or 0.00
        elif self.membership_type == 'quarterly':
            return settings.quarterly_membership_price or 0.00
        elif self.membership_type == 'monthly':
            return settings.monthly_membership_price or 0.00
        elif self.membership_type == 'per_event':
            return settings.per_event_price or 0.00
        return 0.00
    
    def get_event_price(self):
        """Get the price this user pays for events based on their membership type"""
        from app.models import ClubSettings
        settings = ClubSettings.get_settings()
        
        # Members with annual, quarterly, or monthly memberships have already paid
        # and events are free for them
        if self.membership_type in ['annual', 'quarterly', 'monthly']:
            return 0.00
        # Only per-event members pay per event
        elif self.membership_type == 'per_event':
            return settings.per_event_price or 0.00
        return 0.00
    
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
    event_type = db.Column(db.String(50), nullable=False, default='regular')  # 'regular' or 'beginners_course'
    is_free_event = db.Column(db.Boolean, nullable=False, default=False)  # True if event is free of charge
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
    
    def is_regular_event(self):
        """Check if this is a regular shooting event"""
        return self.event_type == 'regular'
    
    def is_beginners_course(self):
        """Check if this is a beginners course"""
        return self.event_type == 'beginners_course'

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
    
    def check_target_face_inventory(self):
        """Check if there are enough target faces in inventory for this competition"""
        # Get total number of teams across all groups
        total_teams = sum(len(group.teams) for group in self.groups)
        
        if total_teams == 0:
            return {
                'has_enough': True,
                'required': 0,
                'available': 0,
                'shortage': 0,
                'message': 'No teams created yet'
            }
        
        # Find target faces in inventory matching this competition's target size
        target_face_category = InventoryCategory.query.filter_by(name='Target Faces').first()
        available_faces = 0
        
        if target_face_category:
            # Get all target face items of the correct size
            target_face_items = InventoryItem.query.filter_by(category_id=target_face_category.id).all()
            
            for item in target_face_items:
                # Handle both dict and string formats for attributes
                attributes = item.attributes or {}
                if isinstance(attributes, str):
                    try:
                        import json
                        attributes = json.loads(attributes)
                    except (json.JSONDecodeError, TypeError):
                        attributes = {}
                
                # Check if attributes has face_size, or try to infer from item name
                face_size = None
                if isinstance(attributes, dict) and 'face_size' in attributes:
                    face_size = str(attributes['face_size'])
                else:
                    # Try to extract size from item name as fallback (e.g., "60cm Target Face")
                    import re
                    name_match = re.search(r'(\d+)cm', item.name, re.IGNORECASE)
                    if name_match:
                        face_size = name_match.group(1)
                
                # Compare face size with competition requirement
                if face_size and str(face_size) == str(self.target_size_cm):
                    available_faces += item.quantity
        
        has_enough = available_faces >= total_teams
        shortage = max(0, total_teams - available_faces)
        
        return {
            'has_enough': has_enough,
            'required': total_teams,
            'available': available_faces,
            'shortage': shortage,
            'message': self._get_inventory_message(has_enough, total_teams, available_faces, shortage)
        }
    
    def _get_inventory_message(self, has_enough, required, available, shortage):
        """Generate appropriate message for target face inventory status"""
        if has_enough:
            if available == required:
                return f'✅ Perfect! You have exactly {available} target faces ({self.target_size_cm}cm) for {required} teams.'
            else:
                return f'✅ Good! You have {available} target faces ({self.target_size_cm}cm) for {required} teams.'
        else:
            return f'⚠️ Warning! You need {shortage} more {self.target_size_cm}cm target faces. You have {available} but need {required} for all teams.'

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

class ClubSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_name = db.Column(db.String(200), nullable=False, default='Nockpoint Archery Club')
    default_location = db.Column(db.String(200))
    description = db.Column(db.Text)
    website_url = db.Column(db.String(200))
    facebook_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    
    # Membership pricing
    annual_membership_price = db.Column(db.Numeric(10, 2), default=0.00)
    quarterly_membership_price = db.Column(db.Numeric(10, 2), default=0.00)
    monthly_membership_price = db.Column(db.Numeric(10, 2), default=0.00)
    per_event_price = db.Column(db.Numeric(10, 2), default=0.00)
    
    # Registration settings
    activation_code = db.Column(db.String(50), nullable=True)
    
    # Pro subscription settings
    is_pro_enabled = db.Column(db.Boolean, nullable=False, default=False)
    pro_subscription_id = db.Column(db.String(100), nullable=True)  # External subscription ID
    pro_expires_at = db.Column(db.DateTime, nullable=True)
    pro_features_enabled = db.Column(db.JSON, default=lambda: [])  # List of enabled pro features
    
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    updater = db.relationship('User', backref='club_settings_updates')
    
    def __repr__(self):
        return f'<ClubSettings {self.club_name}>'
    
    @staticmethod
    def get_settings():
        """Get club settings, create default if none exist"""
        settings = ClubSettings.query.first()
        if not settings:
            settings = ClubSettings()
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def is_pro_active(self):
        """Check if pro subscription is currently active"""
        if not self.is_pro_enabled:
            return False
        
        # If no expiration date is set, assume it's active
        if not self.pro_expires_at:
            return True
        
        # Check if subscription hasn't expired
        from datetime import datetime
        return datetime.utcnow() < self.pro_expires_at
    
    def has_pro_feature(self, feature_name):
        """Check if a specific pro feature is enabled"""
        if not self.is_pro_active():
            return False
        
        # If no specific features are configured, all pro features are enabled
        if not self.pro_features_enabled:
            return True
        
        return feature_name in self.pro_features_enabled
    
    def get_pro_status(self):
        """Get comprehensive pro status information"""
        return {
            'is_active': self.is_pro_active(),
            'expires_at': self.pro_expires_at,
            'subscription_id': self.pro_subscription_id,
            'enabled_features': self.pro_features_enabled or []
        }


class BeginnersStudent(db.Model):
    """Model for non-member participants in beginners courses"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('shooting_event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height_cm = db.Column(db.Integer, nullable=True)  # Height in centimeters
    gender = db.Column(db.String(20), nullable=False)  # Male, Female, Other
    orientation = db.Column(db.String(20), nullable=False)  # Right-handed, Left-handed
    has_paid = db.Column(db.Boolean, default=False)
    insurance_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    notes = db.Column(db.Text)  # Additional notes about the student
    
    # Relationship to event
    event = db.relationship('ShootingEvent', backref='beginners_students')
    
    def __repr__(self):
        return f'<BeginnersStudent {self.name} (Age: {self.age})>'
