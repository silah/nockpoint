from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, DateField, DateTimeField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NumberRange, Optional, ValidationError
from wtforms.widgets import TextArea
from app.models import InventoryCategory

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 50)])
    membership_type = SelectField('Membership Type', choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),  
        ('annual', 'Annual'),
        ('per_event', 'Per-Event')
    ], default='monthly', validators=[DataRequired()])
    activation_code = StringField('Activation Code', validators=[DataRequired(), Length(1, 50)])
    password = PasswordField('Password', validators=[DataRequired(), Length(6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Make this user an administrator')
    submit = SubmitField('Register')
    
    def validate_activation_code(self, field):
        from app.models import ClubSettings
        settings = ClubSettings.get_settings()
        if not settings.activation_code:
            raise ValidationError('Registration is currently disabled. Please contact an administrator.')
        if field.data != settings.activation_code:
            raise ValidationError('Invalid activation code.')

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
        # Populate category choices dynamically
        self.category_id.choices = [(c.id, c.name) for c in InventoryCategory.query.all()]

# Specialized forms for different inventory categories
class BowForm(InventoryItemForm):
    draw_weight = IntegerField('Draw Weight (lbs)', validators=[Optional(), NumberRange(min=10, max=80)])
    length = DecimalField('Length (inches)', validators=[Optional(), NumberRange(min=48, max=72)], places=1)
    bow_type = SelectField('Bow Type', choices=[
        ('recurve', 'Recurve'),
        ('compound', 'Compound'),
        ('longbow', 'Longbow'),
        ('barebow', 'Barebow')
    ], validators=[Optional()])
    handedness = SelectField('Direction', choices=[
        ('right', 'Right Handed'),
        ('left', 'Left Handed')
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
        ('other', 'Other')
    ], validators=[Optional()])

class TargetFaceForm(InventoryItemForm):
    face_size = SelectField('Face Size (cm)', choices=[
        ('20', '20 cm'),
        ('40', '40 cm'),
        ('60', '60 cm'),
        ('80', '80 cm'),
        ('122', '122 cm')
    ], validators=[Optional()])
    target_type = SelectField('Target Type', choices=[
        ('10-ring', '10-Ring Target'),
        ('3-spot', '3-Spot Vertical'),
        ('field', 'Field Target'),
        ('3d', '3D Target')
    ], validators=[Optional()])
    material = SelectField('Material', choices=[
        ('paper', 'Paper'),
        ('plastic', 'Plastic')
    ], validators=[Optional()])

class MemberEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired(), Length(1, 50)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(1, 50)])
    membership_type = SelectField('Membership Type', choices=[
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),  
        ('annual', 'Annual'),
        ('per_event', 'Per-Event')
    ], validators=[DataRequired()])
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
    event_type = SelectField('Event Type', choices=[
        ('regular', 'Regular Shooting Event'),
        ('beginners_course', 'Beginners Course')
    ], default='regular', validators=[DataRequired()])
    is_free_event = BooleanField('Free of charge', default=False)
    max_participants = IntegerField('Max Participants', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Event')
    
    def __init__(self, *args, **kwargs):
        # Extract auto_populate flag if present
        auto_populate_location = kwargs.pop('auto_populate_location', False)
        
        super(ShootingEventForm, self).__init__(*args, **kwargs)
        
        # Auto-populate location with club default if creating new event
        if auto_populate_location and not self.location.data:
            from app.models import ClubSettings
            settings = ClubSettings.get_settings()
            if settings.default_location:
                self.location.data = settings.default_location

class AttendanceForm(FlaskForm):
    member_id = SelectField('Member', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Mark Attendance')
    
    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        from app.models import User
        # Only show active members
        self.member_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                                 for u in User.query.filter_by(is_active=True).order_by(User.first_name, User.last_name).all()]

class PaymentUpdateForm(FlaskForm):
    payment_notes = TextAreaField('Payment Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Mark as Paid')

# Competition Forms

class CompetitionForm(FlaskForm):
    number_of_rounds = IntegerField('Number of Rounds', validators=[DataRequired(), NumberRange(min=1, max=20)], default=6)
    target_size_cm = SelectField('Target Size (cm)', coerce=int, choices=[
        (20, '20 cm'),
        (40, '40 cm'),
        (60, '60 cm'),
        (80, '80 cm'),
        (122, '122 cm')
    ], default=122, validators=[DataRequired()])
    arrows_per_round = IntegerField('Arrows per Round', validators=[DataRequired(), NumberRange(min=3, max=12)], default=6)
    max_team_size = SelectField('Team Size', coerce=int, choices=[(2, '2 members per team'), (3, '3 members per team'), (4, '4 members per team')], default=4)
    submit = SubmitField('Create Competition')

class CompetitionGroupForm(FlaskForm):
    name = StringField('Group Name', validators=[DataRequired(), Length(1, 100)])
    description = TextAreaField('Description', validators=[Optional(), Length(0, 500)])
    min_age = IntegerField('Minimum Age', validators=[Optional(), NumberRange(min=1, max=100)])
    max_age = IntegerField('Maximum Age', validators=[Optional(), NumberRange(min=1, max=100)])
    submit = SubmitField('Add Group')
    
    def validate_max_age(self, max_age):
        if self.min_age.data and max_age.data:
            if max_age.data <= self.min_age.data:
                raise ValidationError('Maximum age must be greater than minimum age.')

class CompetitionRegistrationForm(FlaskForm):
    group_id = SelectField('Competition Group', coerce=int, validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Register for Competition')
    
    def __init__(self, competition_id=None, *args, **kwargs):
        super(CompetitionRegistrationForm, self).__init__(*args, **kwargs)
        if competition_id:
            from app.models import CompetitionGroup
            self.group_id.choices = [(g.id, g.name) for g in CompetitionGroup.query.filter_by(competition_id=competition_id).all()]

class ArrowScoreForm(FlaskForm):
    points = IntegerField('Points', validators=[DataRequired(), NumberRange(min=0, max=10)])
    is_x = BooleanField('Inner X')
    notes = TextAreaField('Notes', validators=[Optional(), Length(0, 200)])
    submit = SubmitField('Record Score')

class BulkArrowScoreForm(FlaskForm):
    """Form for entering multiple arrow scores at once"""
    def __init__(self, arrows_per_round=6, *args, **kwargs):
        super(BulkArrowScoreForm, self).__init__(*args, **kwargs)
        # Dynamically create fields for each arrow in the round
        for i in range(arrows_per_round):
            setattr(self, f'arrow_{i+1}', IntegerField(f'Arrow {i+1}', validators=[DataRequired(), NumberRange(min=0, max=10)]))
            setattr(self, f'is_x_{i+1}', BooleanField(f'X{i+1}'))
    
    round_number = IntegerField('Round Number', validators=[DataRequired()])
    submit = SubmitField('Record Round')

class TeamAssignmentForm(FlaskForm):
    """Form for assigning teams and targets"""
    submit = SubmitField('Generate Teams')

class ClubSettingsForm(FlaskForm):
    club_name = StringField('Club Name', validators=[DataRequired(), Length(1, 200)])
    description = TextAreaField('Club Description', validators=[Optional(), Length(0, 1000)])
    default_location = StringField('Default Event Location', validators=[Optional(), Length(0, 200)])
    address = TextAreaField('Club Address', validators=[Optional(), Length(0, 500)])
    email = StringField('Contact Email', validators=[Optional(), Email(), Length(0, 120)])
    phone = StringField('Phone Number', validators=[Optional(), Length(0, 20)])
    
    # Pro subscription fields
    is_pro_enabled = BooleanField('Enable Pro Features')
    pro_subscription_id = StringField('Subscription ID', validators=[Optional(), Length(0, 100)])
    pro_expires_at = DateTimeField('Pro Expires At', validators=[Optional()], format='%Y-%m-%d %H:%M:%S')
    
    submit = SubmitField('Save Settings')

class ProFeaturesForm(FlaskForm):
    """Form for managing pro feature activation"""
    def __init__(self, *args, **kwargs):
        super(ProFeaturesForm, self).__init__(*args, **kwargs)
        
        # Dynamically create checkboxes for each pro feature
        from app.pro_features import PRO_FEATURES, get_pro_features_by_category
        
        categories = get_pro_features_by_category()
        for category_key, category_info in categories.items():
            for feature in category_info['features']:
                field_name = f"feature_{feature['key']}"
                setattr(self, field_name, BooleanField(feature['name']))
    
    submit = SubmitField('Update Pro Features')
    
    # Membership pricing
    annual_membership_price = DecimalField('Annual Membership Price', validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    quarterly_membership_price = DecimalField('Quarterly Membership Price', validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    monthly_membership_price = DecimalField('Monthly Membership Price', validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    per_event_price = DecimalField('Per-Event Price', validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    
    # Registration settings
    activation_code = StringField('Registration Activation Code', validators=[Optional(), Length(0, 50)], 
                                 description='Leave empty to disable new registrations')
    
    website_url = StringField('Website URL', validators=[Optional(), Length(0, 200)])
    facebook_url = StringField('Facebook URL', validators=[Optional(), Length(0, 200)])
    instagram_url = StringField('Instagram URL', validators=[Optional(), Length(0, 200)])
    twitter_url = StringField('Twitter URL', validators=[Optional(), Length(0, 200)])
    submit = SubmitField('Save Settings')
    
    def validate_website_url(self, field):
        if field.data and not field.data.startswith(('http://', 'https://')):
            raise ValidationError('Website URL must start with http:// or https://')
    
    def validate_facebook_url(self, field):
        if field.data and 'facebook.com' not in field.data:
            raise ValidationError('Please enter a valid Facebook URL')
    
    def validate_instagram_url(self, field):
        if field.data and 'instagram.com' not in field.data:
            raise ValidationError('Please enter a valid Instagram URL')
    
    def validate_twitter_url(self, field):
        if field.data and 'twitter.com' not in field.data and 'x.com' not in field.data:
            raise ValidationError('Please enter a valid Twitter/X URL')


class BeginnersStudentForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(1, 100)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=5, max=100)])
    height_cm = IntegerField('Height (cm)', validators=[Optional(), NumberRange(min=50, max=250)])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    orientation = SelectField('Shooting Hand', choices=[
        ('right_handed', 'Right-handed'),
        ('left_handed', 'Left-handed')
    ], validators=[DataRequired()])
    has_paid = BooleanField('Payment Received', default=False)
    insurance_done = BooleanField('Insurance Completed', default=False)
    notes = TextAreaField('Additional Notes', validators=[Optional(), Length(0, 500)])
    submit = SubmitField('Save Student')
