from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DecimalField, SelectField, DateField, PasswordField, SubmitField, BooleanField
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
    password = PasswordField('Password', validators=[DataRequired(), Length(6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])
    is_admin = BooleanField('Make this user an administrator')
    submit = SubmitField('Register')

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
    target_size_cm = IntegerField('Target Size (cm)', validators=[DataRequired(), NumberRange(min=40, max=200)], default=122)
    arrows_per_round = IntegerField('Arrows per Round', validators=[DataRequired(), NumberRange(min=3, max=12)], default=6)
    max_team_size = SelectField('Team Size', coerce=int, choices=[(3, '3 members per team'), (4, '4 members per team')], default=4)
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
