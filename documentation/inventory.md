# Inventory Management Documentation

## Overview

The inventory management system tracks archery equipment and supplies with categorization, quantity management, and admin controls. It provides a comprehensive solution for managing club equipment.

**Blueprint**: `app/inventory/`  
**Models**: `InventoryItem`, `InventoryCategory` in `app/models.py`  
**Forms**: `InventoryItemForm`, `InventoryCategoryForm` in `app/forms.py`

## Database Models

### InventoryCategory Model

**Purpose**: Organizes inventory items into logical groups  
**Table**: `inventory_category`

```python
class InventoryCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    items = db.relationship('InventoryItem', backref='category', lazy=True)
```

**Key Features**:
- Unique category names prevent duplicates
- Optional descriptions for category details
- One-to-many relationship with inventory items
- Automatic timestamp tracking

**Default Categories**:
- Bows (Recurve, compound, and traditional bows)
- Arrows (Carbon, aluminum, and wooden arrows)
- Targets (Target faces and backstops)
- Safety Equipment (Arm guards, finger tabs, chest guards)
- Accessories (Quivers, bow stands, and other accessories)

### InventoryItem Model

**Purpose**: Individual items in the club's inventory  
**Table**: `inventory_item`

```python
class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('inventory_category.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    attributes = db.Column(db.JSON)  # Category-specific attributes
    
    # Relationships
    creator = db.relationship('User', backref='inventory_items')
```

**Key Features**:
- Flexible item naming and descriptions
- Quantity tracking with non-negative validation
- Category assignment for organization
- Creator tracking for accountability
- Automatic timestamp recording

## Forms

### InventoryCategoryForm

**Purpose**: Create and edit inventory categories

```python
class InventoryCategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description')
    submit = SubmitField('Save Category')
```

**Validation**:
- Category name is required and must be 1-100 characters
- Description is optional
- Unique name validation handled at database level

### InventoryItemForm

**Purpose**: Create and edit inventory items

```python
class InventoryItemForm(FlaskForm):
    name = StringField('Item Name', validators=[DataRequired(), Length(min=1, max=200)])
    description = TextAreaField('Description')
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Save Item')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate categories dynamically
        self.category_id.choices = [(c.id, c.name) for c in InventoryCategory.query.all()]
        self.category_id.choices.insert(0, (0, 'Select Category'))
```

**Features**:
- Dynamic category selection from database
- Quantity validation (non-negative integers)
- Optional description field
- Real-time form validation

## Routes and Views

### Item Management

#### View All Items (`/inventory/`)

**Template**: `inventory/index.html`  
**Access**: All authenticated users

**Features**:
- Paginated item listing
- Search functionality by name/description
- Category-based filtering
- Quantity status indicators
- Admin action buttons (Edit/Delete)

**Implementation**:
```python
@inventory_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    category_id = request.args.get('category', 0, type=int)
    
    query = InventoryItem.query
    
    # Apply search filter
    if search:
        query = query.filter(InventoryItem.name.contains(search))
    
    # Apply category filter
    if category_id:
        query = query.filter(InventoryItem.category_id == category_id)
    
    items = query.order_by(InventoryItem.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    categories = InventoryCategory.query.all()
    
    return render_template('inventory/index.html', 
                         items=items, 
                         categories=categories, 
                         current_search=search,
                         current_category=category_id)
```

#### Create Item (`/inventory/new`)

**Template**: `inventory/item_form.html`  
**Access**: Admin only  
**Form**: `InventoryItemForm`

**Process**:
1. Display form with category dropdown
2. Validate form data
3. Create new inventory item
4. Associate with selected category
5. Record creator information
6. Redirect to item list

#### View Item (`/inventory/<int:id>`)

**Template**: `inventory/view_item.html`  
**Access**: All authenticated users

**Information Displayed**:
- Complete item details
- Category information
- Creation metadata
- Admin action buttons
- Related category link

#### Edit Item (`/inventory/<int:id>/edit`)

**Template**: `inventory/item_form.html`  
**Access**: Admin only  
**Form**: `InventoryItemForm` (pre-populated)

**Features**:
- Form pre-filled with existing data
- Validation maintains data integrity
- Update tracking
- Success/error feedback

#### Delete Item (`/inventory/<int:id>/delete`)

**Method**: POST only  
**Access**: Admin only  
**Response**: JSON

**Implementation**:
```python
@inventory_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})
```

### Category Management

#### View Categories (`/inventory/categories`)

**Template**: `inventory/categories.html`  
**Access**: Admin only

**Features**:
- List all categories with item counts
- Create new category option
- Edit/delete existing categories
- Category usage statistics

#### Create Category (`/inventory/categories/new`)

**Template**: `inventory/category_form.html`  
**Access**: Admin only  
**Form**: `InventoryCategoryForm`

**Validation**:
- Unique category name checking
- Description optional
- Form-level error handling

#### Edit Category (`/inventory/categories/<int:id>/edit`)

**Template**: `inventory/category_form.html`  
**Access**: Admin only

**Constraints**:
- Cannot delete categories with associated items
- Name changes must maintain uniqueness
- Description updates allowed

## User Interface

### Item Listing Template

**Features**:
- Responsive table design
- Search and filter controls
- Pagination navigation
- Status indicators for quantity
- Admin action buttons

**Search and Filter**:
```html
<div class="row mb-3">
    <div class="col-md-8">
        <form method="GET" class="d-flex">
            <input type="text" class="form-control me-2" 
                   name="search" value="{{ current_search }}" 
                   placeholder="Search items...">
            <button type="submit" class="btn btn-outline-secondary">Search</button>
        </form>
    </div>
    <div class="col-md-4">
        <select class="form-select" onchange="filterByCategory(this.value)">
            <option value="0">All Categories</option>
            {% for category in categories %}
                <option value="{{ category.id }}" 
                        {% if category.id == current_category %}selected{% endif %}>
                    {{ category.name }}
                </option>
            {% endfor %}
        </select>
    </div>
</div>
```

**Item Display**:
```html
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Quantity</th>
                <th>Created</th>
                {% if current_user.is_admin() %}
                    <th>Actions</th>
                {% endif %}
            </tr>
        </thead>
        <tbody>
            {% for item in items.items %}
                <tr>
                    <td>
                        <a href="{{ url_for('inventory.view_item', id=item.id) }}">
                            <strong>{{ item.name }}</strong>
                        </a>
                        {% if item.description %}
                            <br><small class="text-muted">{{ item.description[:100] }}...</small>
                        {% endif %}
                    </td>
                    <td>
                        <a href="{{ url_for('inventory.categories') }}" class="badge bg-secondary text-decoration-none">
                            {{ item.category.name }}
                        </a>
                    </td>
                    <td>
                        <span class="badge bg-{% if item.quantity > 0 %}success{% else %}danger{% endif %}">
                            {{ item.quantity }}
                        </span>
                    </td>
                    <td>
                        <small class="text-muted">{{ item.created_at.strftime('%Y-%m-%d') }}</small>
                    </td>
                    {% if current_user.is_admin() %}
                        <td>
                            <div class="btn-group btn-group-sm">
                                <a href="{{ url_for('inventory.edit_item', id=item.id) }}" 
                                   class="btn btn-outline-primary">Edit</a>
                                <button class="btn btn-outline-danger" 
                                        onclick="deleteItem({{ item.id }})">Delete</button>
                            </div>
                        </td>
                    {% endif %}
                </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
```

### Form Templates

**Item Form**:
- Dynamic category selection
- Quantity validation with spinner controls
- Rich text description area
- Form validation display
- Cancel/save button group

**Category Form**:
- Simple name/description fields
- Usage statistics display
- Item count warnings for deletion

## JavaScript Functionality

### Item Deletion

**AJAX Delete Implementation**:
```javascript
function deleteItem(itemId) {
    if (confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
        fetch(`/inventory/${itemId}/delete`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + (data.error || 'Failed to delete item'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while deleting the item.');
        });
    }
}
```

### Category Filtering

**Client-side Filter Function**:
```javascript
function filterByCategory(categoryId) {
    const currentUrl = new URL(window.location);
    if (categoryId == '0') {
        currentUrl.searchParams.delete('category');
    } else {
        currentUrl.searchParams.set('category', categoryId);
    }
    currentUrl.searchParams.delete('page'); // Reset pagination
    window.location.href = currentUrl.toString();
}
```

### Form Enhancement

**Dynamic Form Validation**:
```javascript
// Quantity validation
document.querySelector('input[name="quantity"]').addEventListener('input', function() {
    const value = parseInt(this.value);
    if (value < 0) {
        this.setCustomValidity('Quantity cannot be negative');
    } else {
        this.setCustomValidity('');
    }
});

// Category selection validation
document.querySelector('select[name="category_id"]').addEventListener('change', function() {
    if (this.value == '0') {
        this.setCustomValidity('Please select a category');
    } else {
        this.setCustomValidity('');
    }
});
```

## Dynamic Category-Specific Forms

### Overview
The inventory system features **dynamic forms** that adapt based on the selected item category. Different categories can have different attributes (e.g., bows have handedness, length, and draw weight).

### Technical Implementation

#### Category-Specific Attributes
Items store category-specific attributes in a JSON field in the database:

```python
class InventoryItem(db.Model):
    # ...existing fields...
    attributes = db.Column(db.JSON)  # Category-specific attributes
    
    def get_attributes(self):
        """Get category-specific attributes as dictionary"""
        return self.attributes or {}
    
    def set_attributes(self, attrs_dict):
        """Set category-specific attributes"""
        self.attributes = attrs_dict
```

#### Dynamic Form System
Forms automatically load different fields based on selected category:

**JavaScript Implementation**:
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const categorySelect = document.getElementById('category_id');
    const dynamicFields = document.getElementById('dynamic-fields');
    
    if (categorySelect) {
        categorySelect.addEventListener('change', function() {
            loadCategoryFields(this.value);
        });
    }
    
    function loadCategoryFields(categoryId) {
        if (!categoryId || categoryId == '0') {
            dynamicFields.innerHTML = '';
            return;
        }
        
        fetch(`/inventory/api/category-fields/${categoryId}`)
            .then(response => response.json())
            .then(data => {
                dynamicFields.innerHTML = data.fields_html;
            })
            .catch(error => console.error('Error loading fields:', error));
    }
});
```

#### JSON API Endpoints
Two JSON endpoints support the dynamic form system:

**Get Category Fields**:
```python
@bp.route('/api/category-fields/<int:category_id>')
@login_required
def get_category_fields(category_id):
    """Return HTML form fields for specific category"""
    category = InventoryCategory.query.get_or_404(category_id)
    
    # Define fields for each category type
    if category.name.lower() == 'bow':
        fields_html = render_template_string('''
            <div class="mb-3">
                <label class="form-label">Handedness</label>
                <select name="handedness" class="form-select">
                    <option value="">Select handedness</option>
                    <option value="left">Left Handed</option>
                    <option value="right">Right Handed</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Length (inches)</label>
                <input type="number" name="length" class="form-control" min="48" max="72">
            </div>
            <div class="mb-3">
                <label class="form-label">Draw Weight (lbs)</label>
                <input type="number" name="draw_weight" class="form-control" min="10" max="70">
            </div>
        ''')
    else:
        fields_html = ''
    
    return jsonify({'fields_html': fields_html})
```

**Get Item Attributes**:
```python
@bp.route('/api/item-attributes/<int:item_id>')
@login_required
def get_item_attributes(item_id):
    """Return item's category-specific attributes"""
    item = InventoryItem.query.get_or_404(item_id)
    return jsonify(item.get_attributes())
```

### Category-Specific Forms

#### BowForm
For bow items, additional fields are dynamically loaded:

```python
class BowForm(InventoryItemForm):
    """Extended form for bow-specific attributes"""
    handedness = SelectField('Handedness', choices=[
        ('', 'Select handedness'),
        ('left', 'Left Handed'),
        ('right', 'Right Handed')
    ])
    length = IntegerField('Length (inches)', validators=[
        Optional(), NumberRange(min=48, max=72)
    ])
    draw_weight = IntegerField('Draw Weight (lbs)', validators=[
        Optional(), NumberRange(min=10, max=70)
    ])
```

#### Form Processing
The form processor extracts category-specific attributes:

```python
def extract_category_attributes(form, category_name):
    """Extract category-specific attributes from form data"""
    attributes = {}
    
    if category_name.lower() == 'bow':
        if form.get('handedness'):
            attributes['handedness'] = form.get('handedness')
        if form.get('length'):
            attributes['length'] = int(form.get('length'))
        if form.get('draw_weight'):
            attributes['draw_weight'] = int(form.get('draw_weight'))
    
    return attributes
```

### User Experience

#### Dynamic Field Loading
1. User selects category from dropdown
2. JavaScript detects change event
3. AJAX request fetches category-specific fields
4. Form fields dynamically inserted without page reload
5. User completes category-specific attributes
6. Form submission includes both standard and category fields

#### Benefits
- **Flexible**: Easy to add new categories and attributes
- **User-Friendly**: Only relevant fields displayed
- **Maintainable**: Category logic centralized in one place
- **Extensible**: JSON storage allows complex attribute structures

## Access Control

### Permission Levels

**All Users (Members and Admins)**:
- View inventory items
- View item details
- Search and filter items
- View categories

**Admin Only**:
- Create new items
- Edit existing items
- Delete items
- Manage categories
- Access admin interfaces

### Template Access Control

```html
{% if current_user.is_admin() %}
    <div class="mb-3">
        <a href="{{ url_for('inventory.new_item') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Add New Item
        </a>
        <a href="{{ url_for('inventory.categories') }}" class="btn btn-outline-secondary">
            <i class="bi bi-folder"></i> Manage Categories
        </a>
    </div>
{% endif %}
```

## Data Management

### Default Data Setup

**Initial Categories**:
The system includes a CLI command to create default categories:

```python
@app.cli.command("init-db")
def init_db_command():
    """Create database tables and default data."""
    db.create_all()
    
    # Create default categories
    default_categories = [
        {'name': 'Bows', 'description': 'Recurve, compound, and traditional bows'},
        {'name': 'Arrows', 'description': 'Carbon, aluminum, and wooden arrows'},
        {'name': 'Targets', 'description': 'Target faces and backstops'},
        {'name': 'Safety Equipment', 'description': 'Arm guards, finger tabs, chest guards'},
        {'name': 'Accessories', 'description': 'Quivers, bow stands, and other accessories'},
    ]
    
    for cat_data in default_categories:
        existing = InventoryCategory.query.filter_by(name=cat_data['name']).first()
        if not existing:
            category = InventoryCategory(**cat_data)
            db.session.add(category)
    
    db.session.commit()
```

### Data Validation

**Database Constraints**:
- Unique category names
- Non-null item names
- Foreign key relationships
- Non-negative quantities

**Application Validation**:
- Form field validation
- Custom validation methods
- CSRF protection
- Access control checks

## Dashboard Integration

### Statistics Display

**Dashboard Metrics**:
```python
def dashboard():
    total_items = InventoryItem.query.count()
    total_categories = InventoryCategory.query.count()
    recent_items = InventoryItem.query.order_by(
        InventoryItem.created_at.desc()
    ).limit(5).all()
    
    return render_template('dashboard.html',
                         total_items=total_items,
                         total_categories=total_categories,
                         recent_items=recent_items)
```

**Dashboard Display**:
- Total item count with trend indicators
- Category count statistics
- Recent items with quick links
- Quick action buttons for admins
- Low stock alerts (future enhancement)

## Reporting Features

### Basic Reports

**Category Summary**:
```python
def category_summary():
    categories = db.session.query(
        InventoryCategory.name,
        func.count(InventoryItem.id).label('item_count'),
        func.sum(InventoryItem.quantity).label('total_quantity')
    ).outerjoin(InventoryItem).group_by(InventoryCategory.id).all()
    
    return categories
```

**Low Stock Report**:
```python
def low_stock_items(threshold=5):
    return InventoryItem.query.filter(
        InventoryItem.quantity <= threshold
    ).order_by(InventoryItem.quantity.asc()).all()
```

## Future Enhancements

### Planned Features

**Item Images**:
- Photo upload for items
- Multiple image support
- Thumbnail generation
- Image gallery view

**Barcode Support**:
- Barcode generation for items
- Barcode scanning for inventory
- Quick lookup by barcode

**Location Tracking**:
- Storage location fields
- Multi-location inventory
- Location-based reporting

**Usage Tracking**:
- Check-out/check-in system
- Usage history logging
- Member borrowing records

**Advanced Reporting**:
- Usage statistics
- Category analysis
- Inventory valuation
- Export capabilities (CSV, PDF)

### System Improvements

**Performance Optimization**:
- Database indexing
- Query optimization
- Caching for categories
- Pagination improvements

**User Experience**:
- Advanced search filters
- Bulk operations
- Import/export functionality
- Mobile-responsive improvements

**Integration**:
- Equipment maintenance tracking
- Purchase order integration
- Vendor management
- Cost tracking
