from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, DateField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional
from wtforms.widgets import TextArea
from app.models import InventoryCategory

class ClubSettingsForm(FlaskForm):
    # Basic info
    club_name = StringField('Club Name', validators=[DataRequired(), Length(1, 200)])
    default_location = StringField('Default Location', validators=[Optional(), Length(0, 200)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 2000)])
    website_url = StringField('Website URL', validators=[Optional(), Length(0, 200)])
    facebook_url = StringField('Facebook URL', validators=[Optional(), Length(0, 200)])
    instagram_url = StringField('Instagram URL', validators=[Optional(), Length(0, 200)])
    twitter_url = StringField('Twitter URL', validators=[Optional(), Length(0, 200)])
    email = StringField('Contact Email', validators=[Optional(), Email(), Length(0, 120)])
    phone = StringField('Phone', validators=[Optional(), Length(0, 20)])
    address = TextAreaField('Address', validators=[Optional(), Length(0, 1000)])

    # Pricing
    annual_membership_price = DecimalField('Annual Membership Price', validators=[Optional(), NumberRange(min=0)], places=2)
    quarterly_membership_price = DecimalField('Quarterly Membership Price', validators=[Optional(), NumberRange(min=0)], places=2)
    monthly_membership_price = DecimalField('Monthly Membership Price', validators=[Optional(), NumberRange(min=0)], places=2)
    per_event_price = DecimalField('Per Event Price', validators=[Optional(), NumberRange(min=0)], places=2)

    # Registration settings
    activation_code = StringField('Activation Code', validators=[Optional(), Length(0, 50)])

    # Pro subscription (toggle only here)
    is_pro_enabled = BooleanField('Enable Pro Features')

    submit = SubmitField('Save Settings')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    # Membership activation code (required only if configured in Club Settings)
    activation_code = StringField('Activation Code', validators=[Optional(), Length(0, 50)])
    is_admin = BooleanField('Make this user an administrator')
    submit = SubmitField('Register')


class ClubRegistrationForm(FlaskForm):
    """Form for registering a new club with its first admin user"""
    # Club information
    club_name = StringField('Club Name', validators=[DataRequired(), Length(1, 200)])
    club_slug = StringField('Club URL Slug', validators=[Optional(), Length(1, 100)],
                           render_kw={'placeholder': 'leave blank to auto-generate'})
    club_description = TextAreaField('Club Description', validators=[Optional(), Length(0, 2000)])
    club_email = StringField('Club Contact Email', validators=[Optional(), Email()])
    
    # Admin user information
    username = StringField('Admin Username', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Admin Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Register Club')

class InventoryCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Save Category')

class InventoryItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    unit = SelectField('Unit', choices=[
        ('piece', 'Piece'),
        ('set', 'Set'),
        ('pair', 'Pair'),
        ('box', 'Box'),
        ('kg', 'Kilogram'),
        ('meter', 'Meter')
    ], default='piece')
    location = StringField('Location', validators=[Optional(), Length(0, 100)])
    purchase_date = DateField('Purchase Date', validators=[Optional()])
    purchase_price = DecimalField('Purchase Price', validators=[Optional(), NumberRange(min=0)], places=2)
    condition = SelectField('Condition', choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('damaged', 'Damaged')
    ], default='good')
    notes = TextAreaField('Notes', validators=[Optional(), Length(0, 1000)])
    submit = SubmitField('Save Item')
    
    def __init__(self, *args, **kwargs):
        super(InventoryItemForm, self).__init__(*args, **kwargs)
        # Populate category choices dynamically - filter by current club if available
        from flask import g
        if hasattr(g, 'current_club') and g.current_club:
            self.category_id.choices = [(c.id, c.name) for c in InventoryCategory.query.filter_by(club_id=g.current_club.id).all()]
        else:
            # Fallback for contexts without club (e.g., tests)
            self.category_id.choices = [(c.id, c.name) for c in InventoryCategory.query.all()]

# Specialized forms for different inventory categories
class BowForm(InventoryItemForm):
    draw_weight = IntegerField('Draw Weight (lbs)', validators=[Optional(), NumberRange(min=10, max=80)])
    draw_length = DecimalField('Draw Length (inches)', validators=[Optional(), NumberRange(min=20, max=35)], places=1)
    bow_type = SelectField('Bow Type', choices=[
        ('recurve', 'Recurve'),
        ('compound', 'Compound'),
        ('longbow', 'Longbow'),
        ('barebow', 'Barebow')
    ], validators=[Optional()])
    handedness = SelectField('Handedness', choices=[
        ('right', 'Right Hand'),
        ('left', 'Left Hand')
    ], validators=[Optional()])

class ArrowForm(InventoryItemForm):
    spine = IntegerField('Spine', validators=[Optional(), NumberRange(min=200, max=1000)])
    length = DecimalField('Length (inches)', validators=[Optional(), NumberRange(min=20, max=35)], places=1)
    point_weight = IntegerField('Point Weight (grains)', validators=[Optional(), NumberRange(min=60, max=300)])
    fletching_type = SelectField('Fletching Type', choices=[
        ('feather', 'Feather'),
        ('plastic', 'Plastic Vane'),
        ('carbon', 'Carbon Vane')
    ], validators=[Optional()])

class TargetForm(InventoryItemForm):
    face_size = IntegerField('Face Size (cm)', validators=[Optional(), NumberRange(min=20, max=150)])
    target_type = SelectField('Target Type', choices=[
        ('10-ring', '10-Ring Target'),
        ('3-spot', '3-Spot Vertical'),
        ('field', 'Field Target'),
        ('3d', '3D Target')
    ], validators=[Optional()])
    material = SelectField('Material', choices=[
        ('straw', 'Straw'),
        ('foam', 'Foam'),
        ('paper', 'Paper'),
        ('cardboard', 'Cardboard')
    ], validators=[Optional()])

class MemberEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('New Password (leave blank to keep current)', validators=[Optional(), Length(6)])
    password2 = PasswordField('Repeat New Password', 
                             validators=[EqualTo('password', message='Passwords must match')])
    is_admin = BooleanField('Administrator privileges')
    is_active = BooleanField('Active member', default=True)
    submit = SubmitField('Update Member')

class ShootingEventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 1000)])
    location = StringField('Location', validators=[DataRequired(), Length(1, 200)])
    date = DateField('Event Date', validators=[DataRequired()])
    start_time = StringField('Start Time', validators=[DataRequired()], render_kw={'placeholder': 'HH:MM (24-hour format)'})
    duration_hours = IntegerField('Duration (hours)', validators=[DataRequired(), NumberRange(min=1, max=12)], default=2)
    price = DecimalField('Price per Person', validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    max_participants = IntegerField('Max Participants', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Event')

class AttendanceForm(FlaskForm):
    member_id = SelectField('Member', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Mark Attendance')
    
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        from app.models import User, ClubMembership
        from flask import g
        
        # Only show active members from current club
        if hasattr(g, 'current_club') and g.current_club:
            memberships = ClubMembership.query.filter_by(
                club_id=g.current_club.id,
                is_active=True
            ).join(User).order_by(User.first_name, User.last_name).all()
            self.member_id.choices = [(m.user.id, f"{m.user.first_name} {m.user.last_name} ({m.user.username})") 
                                     for m in memberships]
        else:
            # Fallback for contexts without club
            self.member_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                                     for u in User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()]

class PaymentUpdateForm(FlaskForm):
    payment_notes = TextAreaField('Payment Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Mark as Paid')


class CSVImportForm(FlaskForm):
    """Form for importing members from CSV file"""
    csv_file = FileField('CSV File', validators=[
        FileRequired(),
        FileAllowed(['csv'], 'CSV files only!')
    ])
    membership_type = SelectField('Default Membership Type', choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annual', 'Annual'),
        ('per_event', 'Per Event')
    ], default='monthly')
    make_admin = BooleanField('Make all imported users administrators', default=False)
    submit = SubmitField('Import Members')
