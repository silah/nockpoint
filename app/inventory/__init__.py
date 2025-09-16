from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import InventoryItem, InventoryCategory
from app.forms import InventoryItemForm, InventoryCategoryForm, BowForm, ArrowForm, TargetForm
from datetime import datetime
import json

inventory_bp = Blueprint('inventory', __name__)

def admin_required(f):
    """Decorator to require admin role"""
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Admin access required.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@inventory_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    query = InventoryItem.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(InventoryItem.name.contains(search) | 
                           InventoryItem.description.contains(search))
    
    items = query.order_by(InventoryItem.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    categories = InventoryCategory.query.all()
    
    return render_template('inventory/index.html', 
                         items=items, 
                         categories=categories,
                         current_category=category_id,
                         search=search)

@inventory_bp.route('/categories')
@login_required
def categories():
    categories = InventoryCategory.query.order_by(InventoryCategory.name).all()
    return render_template('inventory/categories.html', categories=categories)

@inventory_bp.route('/categories/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_category():
    form = InventoryCategoryForm()
    if form.validate_on_submit():
        category = InventoryCategory(
            name=form.name.data,
            description=form.description.data
        )
        db.session.add(category)
        db.session.commit()
        flash('Category created successfully!', 'success')
        return redirect(url_for('inventory.categories'))
    
    return render_template('inventory/category_form.html', form=form, title='New Category')

@inventory_bp.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_category(id):
    category = InventoryCategory.query.get_or_404(id)
    form = InventoryCategoryForm(obj=category)
    
    if form.validate_on_submit():
        category.name = form.name.data
        category.description = form.description.data
        db.session.commit()
        flash('Category updated successfully!', 'success')
        return redirect(url_for('inventory.categories'))
    
    return render_template('inventory/category_form.html', form=form, title='Edit Category')

@inventory_bp.route('/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_item():
    form = InventoryItemForm()
    
    if form.validate_on_submit():
        # Create base item
        item = InventoryItem(
            name=form.name.data,
            description=form.description.data,
            quantity=form.quantity.data,
            unit=form.unit.data,
            location=form.location.data,
            purchase_date=form.purchase_date.data,
            purchase_price=form.purchase_price.data,
            condition=form.condition.data,
            notes=form.notes.data,
            category_id=form.category_id.data
        )
        
        # Add category-specific attributes from form data
        category = InventoryCategory.query.get(form.category_id.data)
        if category:
            item.attributes = extract_category_attributes(request.form, category.name)
        
        db.session.add(item)
        db.session.commit()
        flash('Item added successfully!', 'success')
        return redirect(url_for('inventory.index'))
    
    return render_template('inventory/item_form.html', form=form, title='New Item')

@inventory_bp.route('/item/<int:id>')
@login_required
def view_item(id):
    item = InventoryItem.query.get_or_404(id)
    return render_template('inventory/view_item.html', item=item)

@inventory_bp.route('/item/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(id):
    item = InventoryItem.query.get_or_404(id)
    form = InventoryItemForm(obj=item)
    
    if form.validate_on_submit():
        item.name = form.name.data
        item.description = form.description.data
        item.quantity = form.quantity.data
        item.unit = form.unit.data
        item.location = form.location.data
        item.purchase_date = form.purchase_date.data
        item.purchase_price = form.purchase_price.data
        item.condition = form.condition.data
        item.notes = form.notes.data
        item.category_id = form.category_id.data
        item.updated_at = datetime.utcnow()
        
        # Update category-specific attributes from form data
        category = InventoryCategory.query.get(form.category_id.data)
        if category:
            item.attributes = extract_category_attributes(request.form, category.name)
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('inventory.view_item', id=id))
    
    return render_template('inventory/item_form.html', form=form, title='Edit Item', item=item)

@inventory_bp.route('/item/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/api/category-fields/<int:category_id>')
@login_required
def get_category_fields(category_id):
    """API endpoint to get form fields for a specific category"""
    category = InventoryCategory.query.get_or_404(category_id)
    
    fields = []
    
    if category.name.lower() == 'bows':
        fields = [
            {
                'name': 'draw_weight',
                'label': 'Draw Weight (lbs)',
                'type': 'number',
                'min': 10,
                'max': 80,
                'required': False
            },
            {
                'name': 'length', 
                'label': 'Length (inches)',
                'type': 'number',
                'min': 48,
                'max': 72,
                'step': '0.1',
                'required': False
            },
            {
                'name': 'bow_type',
                'label': 'Bow Type',
                'type': 'select',
                'options': [
                    {'value': '', 'label': 'Select Type'},
                    {'value': 'recurve', 'label': 'Recurve'},
                    {'value': 'compound', 'label': 'Compound'},
                    {'value': 'longbow', 'label': 'Longbow'},
                    {'value': 'barebow', 'label': 'Barebow'}
                ],
                'required': False
            },
            {
                'name': 'handedness',
                'label': 'Direction',
                'type': 'select',
                'options': [
                    {'value': '', 'label': 'Select Direction'},
                    {'value': 'right', 'label': 'Right Handed'},
                    {'value': 'left', 'label': 'Left Handed'}
                ],
                'required': False
            }
        ]
    elif category.name.lower() == 'arrows':
        fields = [
            {
                'name': 'spine',
                'label': 'Spine',
                'type': 'number',
                'min': 200,
                'max': 1000,
                'required': False
            },
            {
                'name': 'length',
                'label': 'Length (inches)',
                'type': 'number',
                'min': 20,
                'max': 35,
                'step': '0.1',
                'required': False
            },
            {
                'name': 'point_weight',
                'label': 'Point Weight (grains)',
                'type': 'number',
                'min': 60,
                'max': 300,
                'required': False
            },
            {
                'name': 'fletching_type',
                'label': 'Fletching Type',
                'type': 'select',
                'options': [
                    {'value': '', 'label': 'Select Type'},
                    {'value': 'feather', 'label': 'Feather'},
                    {'value': 'plastic', 'label': 'Plastic Vane'},
                    {'value': 'carbon', 'label': 'Carbon Vane'}
                ],
                'required': False
            }
        ]
    elif category.name.lower() == 'targets':
        fields = [
            {
                'name': 'face_size',
                'label': 'Face Size (cm)', 
                'type': 'number',
                'min': 20,
                'max': 150,
                'required': False
            },
            {
                'name': 'target_type',
                'label': 'Target Type',
                'type': 'select',
                'options': [
                    {'value': '', 'label': 'Select Type'},
                    {'value': '10-ring', 'label': '10-Ring Target'},
                    {'value': '3-spot', 'label': '3-Spot Vertical'},
                    {'value': 'field', 'label': 'Field Target'},
                    {'value': '3d', 'label': '3D Target'}
                ],
                'required': False
            },
            {
                'name': 'material',
                'label': 'Material',
                'type': 'select',
                'options': [
                    {'value': '', 'label': 'Select Material'},
                    {'value': 'straw', 'label': 'Straw'},
                    {'value': 'foam', 'label': 'Foam'},
                    {'value': 'paper', 'label': 'Paper'},
                    {'value': 'cardboard', 'label': 'Cardboard'}
                ],
                'required': False
            }
        ]
    
    return jsonify({'fields': fields})

@inventory_bp.route('/api/item-attributes/<int:item_id>')
@login_required 
def get_item_attributes(item_id):
    """API endpoint to get existing attributes for an item (for edit forms)"""
    item = InventoryItem.query.get_or_404(item_id)
    return jsonify({'attributes': item.attributes or {}})

def get_form_for_category(category):
    """Return appropriate form class based on category"""
    if not category:
        return InventoryItemForm()
    
    category_forms = {
        'bows': BowForm,
        'arrows': ArrowForm,
        'targets': TargetForm,
    }
    
    form_class = category_forms.get(category.name.lower(), InventoryItemForm)
    return form_class()

def get_category_attributes(form, category_name):
    """Extract category-specific attributes from form"""
    attributes = {}
    
    if category_name.lower() == 'bows':
        if hasattr(form, 'draw_weight') and form.draw_weight.data:
            attributes['draw_weight'] = form.draw_weight.data
        if hasattr(form, 'length') and form.length.data:
            attributes['length'] = float(form.length.data)
        if hasattr(form, 'bow_type') and form.bow_type.data:
            attributes['bow_type'] = form.bow_type.data
        if hasattr(form, 'handedness') and form.handedness.data:
            attributes['handedness'] = form.handedness.data
    
    elif category_name.lower() == 'arrows':
        if hasattr(form, 'spine') and form.spine.data:
            attributes['spine'] = form.spine.data
        if hasattr(form, 'length') and form.length.data:
            attributes['length'] = float(form.length.data)
        if hasattr(form, 'point_weight') and form.point_weight.data:
            attributes['point_weight'] = form.point_weight.data
        if hasattr(form, 'fletching_type') and form.fletching_type.data:
            attributes['fletching_type'] = form.fletching_type.data
    
    elif category_name.lower() == 'targets':
        if hasattr(form, 'face_size') and form.face_size.data:
            attributes['face_size'] = form.face_size.data
        if hasattr(form, 'target_type') and form.target_type.data:
            attributes['target_type'] = form.target_type.data
        if hasattr(form, 'material') and form.material.data:
            attributes['material'] = form.material.data
    
    return attributes

def populate_form_from_item(form, item):
    """Populate form with item data including category-specific attributes"""
    form.name.data = item.name
    form.description.data = item.description
    form.quantity.data = item.quantity
    form.unit.data = item.unit
    form.location.data = item.location
    form.purchase_date.data = item.purchase_date
    form.purchase_price.data = item.purchase_price
    form.condition.data = item.condition
    form.notes.data = item.notes
    form.category_id.data = item.category_id
    
    # Populate category-specific attributes
    if item.attributes:
        for attr_name, attr_value in item.attributes.items():
            if hasattr(form, attr_name):
                getattr(form, attr_name).data = attr_value

def extract_category_attributes(form_data, category_name):
    """Extract category-specific attributes from form data"""
    attributes = {}
    
    if category_name.lower() == 'bows':
        if form_data.get('draw_weight'):
            attributes['draw_weight'] = int(form_data['draw_weight'])
        if form_data.get('length'):
            attributes['length'] = float(form_data['length'])
        if form_data.get('bow_type'):
            attributes['bow_type'] = form_data['bow_type']
        if form_data.get('handedness'):
            attributes['handedness'] = form_data['handedness']
    
    elif category_name.lower() == 'arrows':
        if form_data.get('spine'):
            attributes['spine'] = int(form_data['spine'])
        if form_data.get('length'):
            attributes['length'] = float(form_data['length'])
        if form_data.get('point_weight'):
            attributes['point_weight'] = int(form_data['point_weight'])
        if form_data.get('fletching_type'):
            attributes['fletching_type'] = form_data['fletching_type']
    
    elif category_name.lower() == 'targets':
        if form_data.get('face_size'):
            attributes['face_size'] = int(form_data['face_size'])
        if form_data.get('target_type'):
            attributes['target_type'] = form_data['target_type']
        if form_data.get('material'):
            attributes['material'] = form_data['material']
    
    return attributes
