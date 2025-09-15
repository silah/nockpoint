# Forms Documentation

## Overview

The application uses Flask-WTF and WTForms for form handling, validation, and CSRF protection. All forms inherit from `FlaskForm` and include comprehensive validation.

**File**: `app/forms.py`

## Authentication Forms

### LoginForm
Handles user authentication.

```python
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
```

**Validators**:
- `DataRequired()` - Ensures fields are not empty

**Usage**: Login page (`/auth/login`)

### RegistrationForm
Handles new user registration.

```python
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
```

**Validators**:
- `Length()` - Username must be 4-20 characters
- `Email()` - Email format validation
- `EqualTo()` - Password confirmation matching

**Custom Validation**:
- `validate_username()` - Checks for existing username
- `validate_email()` - Checks for existing email

## Inventory Management Forms

### InventoryCategoryForm
Creates and edits inventory categories.

```python
class InventoryCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Category')
```

**Validators**:
- `Length()` - Name must be 1-100 characters

### InventoryItemForm
Creates and edits inventory items.

```python
class InventoryItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Item')
```

**Dynamic Fields**:
- `category_id` - Populated from database categories in `__init__()`

**Validators**:
- `NumberRange()` - Quantity must be non-negative

## Member Management Forms

### MemberForm
Creates and edits member accounts.

```python
class MemberForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    is_admin = BooleanField('Administrator')
    password = PasswordField('Password')
    password2 = PasswordField('Repeat Password', validators=[EqualTo('password')])
    submit = SubmitField('Save Member')
```

**Features**:
- Optional password (for editing existing members)
- Admin checkbox for role assignment
- Conditional validation based on edit vs. create mode

### ProfileForm
Allows users to edit their own profiles.

```python
class ProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Update Profile')
```

**Security**: Users cannot change their own username or admin status

## Events System Forms

### ShootingEventForm
Creates and edits shooting events.

```python
class ShootingEventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    location = StringField('Location', validators=[DataRequired(), Length(min=1, max=200)])
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    duration_hours = IntegerField('Duration (hours)', validators=[DataRequired(), NumberRange(min=1, max=24)])
    price = DecimalField('Price ($)', validators=[DataRequired(), NumberRange(min=0, max=999.99)], places=2)
    max_participants = IntegerField('Max Participants', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Save Event')
```

**Validators**:
- `DateField()` - HTML5 date picker
- `TimeField()` - HTML5 time picker
- `DecimalField()` - Precise monetary amounts
- `Optional()` - Max participants can be empty (unlimited)

### AttendanceForm
Manages event attendance (used internally).

```python
class AttendanceForm(FlaskForm):
    member_id = SelectField('Member', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Add Attendee')
```

**Dynamic Population**:
```python
def __init__(self, event_id=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if event_id:
        # Populate with members not already registered
        already_registered = [a.member_id for a in EventAttendance.query.filter_by(event_id=event_id).all()]
        available_users = User.query.filter(~User.id.in_(already_registered)).all()
        self.member_id.choices = [(u.id, f"{u.first_name} {u.last_name} ({u.username})") 
                                  for u in available_users]
```

### PaymentUpdateForm
Updates payment status for charges.

```python
class PaymentUpdateForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0, max=999.99)], places=2)
    notes = TextAreaField('Payment Notes')
    submit = SubmitField('Update Payment')
```

## Form Features

### CSRF Protection
All forms automatically include CSRF tokens:
```html
{{ form.hidden_tag() }}
```

### Validation Display
Templates display validation errors:
```html
{% if form.field.errors %}
    <div class="text-danger small">
        {% for error in form.field.errors %}
            <div>{{ error }}</div>
        {% endfor %}
    </div>
{% endif %}
```

### Dynamic Field Population
Forms dynamically populate select fields from the database:

```python
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.category_id.choices = [(c.id, c.name) for c in InventoryCategory.query.all()]
    self.category_id.choices.insert(0, (0, 'Select Category'))
```

### Custom Validation Methods
Forms include custom validation for business logic:

```python
def validate_username(self, username):
    if self.original_username != username.data:
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
```

## Form Security

### Input Sanitization
- All text inputs are automatically escaped by Jinja2
- Forms validate data types and ranges
- SQL injection prevention through SQLAlchemy ORM

### CSRF Protection
- Flask-WTF provides automatic CSRF protection
- All forms must include `{{ form.hidden_tag() }}`
- AJAX requests must include CSRF tokens

### Access Control
- Form access controlled by login_required decorators
- Admin-only forms protected by custom decorators
- Users can only edit their own profiles

## Form Styling

All forms use Bootstrap 5 classes for consistent styling:

```html
{{ form.field(class="form-control") }}
{{ form.field.label(class="form-label") }}
{{ form.submit(class="btn btn-primary") }}
```

**Common Classes**:
- `form-control` - Input styling
- `form-label` - Label styling  
- `form-check-input` - Checkbox styling
- `btn btn-primary` - Button styling

## Error Handling

### Field-Level Validation
```html
{% if form.field.errors %}
    <div class="text-danger small">
        {% for error in form.field.errors %}
            <div>{{ error }}</div>
        {% endfor %}
    </div>
{% endif %}
```

### Form-Level Validation
```python
@bp.route('/create', methods=['GET', 'POST'])
def create():
    form = MyForm()
    if form.validate_on_submit():
        # Process valid form
        return redirect(url_for('index'))
    # Re-display form with errors
    return render_template('form.html', form=form)
```

### Flash Messages
```python
if form.validate_on_submit():
    flash('Success message', 'success')
else:
    flash('Error message', 'error')
```

## Testing Forms

### Unit Testing
```python
def test_form_validation():
    form = MyForm(data={'field': 'value'})
    assert form.validate()
    assert form.field.data == 'value'
```

### Integration Testing
Forms should be tested with actual HTTP requests to verify CSRF protection and proper form processing.

## Best Practices

1. **Validation**: Always validate on both client and server side
2. **Security**: Include CSRF protection on all forms
3. **UX**: Provide clear error messages and field descriptions
4. **Accessibility**: Use proper labels and form structure
5. **Performance**: Cache dynamic field choices when possible
