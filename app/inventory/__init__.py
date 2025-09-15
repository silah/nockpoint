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
    category_id = request.args.get('category', type=int)
    
    # Get category to determine which form to use
    category = None
    if category_id:
        category = InventoryCategory.query.get_or_404(category_id)
    
    # Choose form based on category
    form = get_form_for_category(category)
    
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
        
        # Add category-specific attributes
        if category:
            item.attributes = get_category_attributes(form, category.name)
        
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
    
    # Get form for the item's category
    form = get_form_for_category(item.category)
    
    if request.method == 'GET':
        # Populate form with existing data
        populate_form_from_item(form, item)
    
    if form.validate_on_submit():
        # Update base fields
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
        
        # Update category-specific attributes
        item.attributes = get_category_attributes(form, item.category.name)
        
        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('inventory.view_item', id=id))
    
    return render_template('inventory/item_form.html', form=form, title='Edit Item')

@inventory_bp.route('/item/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_item(id):
    item = InventoryItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('inventory.index'))

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
        if hasattr(form, 'draw_length') and form.draw_length.data:
            attributes['draw_length'] = float(form.draw_length.data)
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
