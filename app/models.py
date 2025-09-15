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
    attended_at = db.Column(db.DateTime, default=datetime.utcnow)
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
