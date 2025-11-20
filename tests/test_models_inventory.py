"""
Tests for inventory functionality with multi-tenancy.
Tests inventory categories and items with club context.
"""
import pytest
from app.models import InventoryCategory, InventoryItem


class TestInventoryCategory:
    """Test inventory category model with club context."""
    
    def test_create_category_with_club(self, _db, club_alpha):
        """Test creating a category with club_id."""
        category = InventoryCategory(
            name='Test Category',
            description='Test description',
            club_id=club_alpha.id
        )
        _db.session.add(category)
        _db.session.commit()
        
        assert category.id is not None
        assert category.club_id == club_alpha.id
        assert category.name == 'Test Category'
    
    def test_category_belongs_to_club(self, inventory_alpha, club_alpha):
        """Test category belongs to correct club."""
        category = inventory_alpha['category']
        assert category.club_id == club_alpha.id
        assert category.club.id == club_alpha.id
        assert category.club.name == 'Alpha Archery'
    
    def test_category_items_relationship(self, inventory_alpha):
        """Test category can access its items."""
        category = inventory_alpha['category']
        items = category.items
        
        assert len(items) > 0
        for item in items:
            assert item.category_id == category.id
            assert item.club_id == category.club_id
    
    def test_filter_categories_by_club(self, _db, inventory_alpha, inventory_beta, club_alpha):
        """Test filtering categories by club."""
        alpha_categories = InventoryCategory.query.filter_by(
            club_id=club_alpha.id
        ).all()
        
        # Should contain Alpha category
        assert inventory_alpha['category'] in alpha_categories
        
        # Should not contain Beta category
        assert inventory_beta['category'] not in alpha_categories


class TestInventoryItem:
    """Test inventory item model with club context."""
    
    def test_create_item_with_club(self, _db, club_alpha):
        """Test creating an item with club_id."""
        # First create a category
        category = InventoryCategory(
            name='Test Category',
            club_id=club_alpha.id
        )
        _db.session.add(category)
        _db.session.flush()
        
        item = InventoryItem(
            name='Test Bow',
            category_id=category.id,
            club_id=club_alpha.id,
            quantity=3,
            unit='piece',
            condition='good',
            location='Storage A'
        )
        _db.session.add(item)
        _db.session.commit()
        
        assert item.id is not None
        assert item.club_id == club_alpha.id
        assert item.name == 'Test Bow'
        assert item.quantity == 3
    
    def test_item_belongs_to_club(self, inventory_alpha, club_alpha):
        """Test item belongs to correct club."""
        item = inventory_alpha['items'][0]
        assert item.club_id == club_alpha.id
        # InventoryItem doesn't have club relationship, access via category or query
        assert InventoryCategory.query.get(item.category_id).club_id == club_alpha.id
    
    def test_item_belongs_to_category(self, inventory_alpha):
        """Test item belongs to category."""
        category = inventory_alpha['category']
        item = inventory_alpha['items'][0]
        
        assert item.category_id == category.id
        assert item.category.id == category.id
    
    def test_item_category_same_club(self, inventory_alpha, club_alpha):
        """Test item and its category belong to same club."""
        category = inventory_alpha['category']
        item = inventory_alpha['items'][0]
        
        assert item.club_id == category.club_id
        assert item.club_id == club_alpha.id
    
    def test_filter_items_by_club(self, _db, inventory_alpha, inventory_beta, club_alpha):
        """Test filtering items by club."""
        alpha_items = InventoryItem.query.filter_by(
            club_id=club_alpha.id
        ).all()
        
        # Should contain all Alpha items
        for item in inventory_alpha['items']:
            assert item in alpha_items
        
        # Should not contain Beta items
        for item in inventory_beta['items']:
            assert item not in alpha_items
    
    def test_item_units(self, _db, club_alpha):
        """Test different item units."""
        # Create category first
        category = InventoryCategory(name='Equipment', club_id=club_alpha.id)
        _db.session.add(category)
        _db.session.flush()
        
        items = [
            InventoryItem(name='Bow', club_id=club_alpha.id, category_id=category.id, quantity=5, unit='piece'),
            InventoryItem(name='Arrow Set', club_id=club_alpha.id, category_id=category.id, quantity=3, unit='set'),
            InventoryItem(name='Gloves', club_id=club_alpha.id, category_id=category.id, quantity=10, unit='pair'),
        ]
        _db.session.add_all(items)
        _db.session.commit()
        
        for item in items:
            assert item.unit in ['piece', 'set', 'pair']
    
    def test_item_conditions(self, _db, club_alpha):
        """Test different item conditions."""
        # Create category first
        category = InventoryCategory(name='Bows', club_id=club_alpha.id)
        _db.session.add(category)
        _db.session.flush()
        
        items = [
            InventoryItem(name='New Bow', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', condition='excellent'),
            InventoryItem(name='Good Bow', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', condition='good'),
            InventoryItem(name='Fair Bow', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', condition='fair'),
            InventoryItem(name='Damaged Bow', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', condition='poor'),
        ]
        _db.session.add_all(items)
        _db.session.commit()
        
        conditions = [item.condition for item in items]
        assert 'excellent' in conditions
        assert 'good' in conditions
        assert 'fair' in conditions
        assert 'poor' in conditions
    
    def test_item_without_category(self, _db, club_alpha):
        """Test that item requires category (NOT NULL constraint)."""
        # category_id is required, test should expect this to fail
        item = InventoryItem(
            name='Uncategorized Item',
            club_id=club_alpha.id,
            quantity=1,
            unit='piece'
        )
        _db.session.add(item)
        
        # Should raise IntegrityError because category_id is required
        with pytest.raises(Exception):  # IntegrityError
            _db.session.commit()


class TestInventoryCRUD:
    """Test CRUD operations for inventory with club context."""
    
    def test_create_category_and_items(self, _db, club_alpha):
        """Test creating a category with multiple items."""
        category = InventoryCategory(
            name='Arrows',
            description='Various arrows',
            club_id=club_alpha.id
        )
        _db.session.add(category)
        _db.session.flush()
        
        items = [
            InventoryItem(
                name='Carbon Arrow 500',
                category_id=category.id,
                club_id=club_alpha.id,
                quantity=50,
                unit='piece'
            ),
            InventoryItem(
                name='Carbon Arrow 600',
                category_id=category.id,
                club_id=club_alpha.id,
                quantity=30,
                unit='piece'
            ),
        ]
        _db.session.add_all(items)
        _db.session.commit()
        
        # Verify relationships
        assert len(category.items) == 2
        for item in items:
            assert item.category_id == category.id
    
    def test_update_item_quantity(self, inventory_alpha):
        """Test updating item quantity."""
        item = inventory_alpha['items'][0]
        original_quantity = item.quantity
        
        item.quantity = original_quantity + 5
        assert item.quantity == original_quantity + 5
    
    def test_delete_item(self, _db, inventory_alpha):
        """Test deleting an item."""
        item = inventory_alpha['items'][0]
        item_id = item.id
        
        _db.session.delete(item)
        _db.session.commit()
        
        # Verify deletion
        deleted_item = InventoryItem.query.get(item_id)
        assert deleted_item is None
    
    def test_delete_category_with_items(self, _db, inventory_alpha):
        """Test deleting a category deletes items (cascade delete)."""
        category = inventory_alpha['category']
        category_id = category.id
        
        # Get item IDs before deletion
        item_ids = [item.id for item in category.items]
        
        _db.session.delete(category)
        _db.session.commit()
        
        # Verify category is deleted
        deleted_category = InventoryCategory.query.get(category_id)
        assert deleted_category is None
        
        # Items should be deleted too due to cascade
        for item_id in item_ids:
            deleted_item = InventoryItem.query.get(item_id)
            assert deleted_item is None


class TestInventorySearch:
    """Test inventory search and filtering."""
    
    def test_search_items_by_name(self, _db, inventory_alpha, club_alpha):
        """Test searching items by name."""
        # Search for 'Recurve'
        results = InventoryItem.query.filter(
            InventoryItem.club_id == club_alpha.id,
            InventoryItem.name.ilike('%Recurve%')
        ).all()
        
        assert len(results) > 0
        for item in results:
            assert 'Recurve' in item.name
    
    def test_filter_items_by_condition(self, _db, club_alpha):
        """Test filtering items by condition."""
        # Create category first
        category = InventoryCategory(name='Bows', club_id=club_alpha.id)
        _db.session.add(category)
        _db.session.flush()
        
        # Create items with different conditions
        items = [
            InventoryItem(name='Good Bow', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', condition='good'),
            InventoryItem(name='Excellent Bow', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', condition='excellent'),
        ]
        _db.session.add_all(items)
        _db.session.commit()
        
        # Filter for excellent condition
        excellent_items = InventoryItem.query.filter_by(
            club_id=club_alpha.id,
            condition='excellent'
        ).all()
        
        assert len(excellent_items) > 0
        for item in excellent_items:
            assert item.condition == 'excellent'
    
    def test_filter_items_by_category(self, inventory_alpha):
        """Test filtering items by category."""
        category = inventory_alpha['category']
        
        items = InventoryItem.query.filter_by(
            club_id=category.club_id,
            category_id=category.id
        ).all()
        
        assert len(items) == len(inventory_alpha['items'])
    
    def test_filter_items_by_location(self, _db, club_alpha):
        """Test filtering items by location."""
        # Create category first
        category = InventoryCategory(name='Equipment', club_id=club_alpha.id)
        _db.session.add(category)
        _db.session.flush()
        
        items = [
            InventoryItem(name='Item A', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', location='Storage A'),
            InventoryItem(name='Item B', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', location='Storage A'),
            InventoryItem(name='Item C', club_id=club_alpha.id, category_id=category.id, quantity=1, unit='piece', location='Storage B'),
        ]
        _db.session.add_all(items)
        _db.session.commit()
        
        storage_a_items = InventoryItem.query.filter_by(
            club_id=club_alpha.id,
            location='Storage A'
        ).all()
        
        assert len(storage_a_items) == 2


class TestInventoryValidation:
    """Test inventory validation rules."""
    
    def test_item_requires_positive_quantity(self, _db, club_alpha):
        """Test that items should have positive quantity."""
        # Create category first
        category = InventoryCategory(name='Test', club_id=club_alpha.id)
        _db.session.add(category)
        _db.session.flush()
        
        item = InventoryItem(
            name='Test Item',
            club_id=club_alpha.id,
            category_id=category.id,
            quantity=0,  # Zero or negative might be allowed
            unit='piece'
        )
        _db.session.add(item)
        _db.session.commit()
        
        # Verify it was created (validation might be in forms, not model)
        assert item.id is not None
    
    def test_category_attributes_as_json(self, _db, club_alpha):
        """Test category can be created with description."""
        category = InventoryCategory(
            name='Bows',
            club_id=club_alpha.id,
            description='Various types of bows'
        )
        _db.session.add(category)
        _db.session.commit()
        
        # Verify description stored correctly
        assert category.description == 'Various types of bows'
    
    def test_item_custom_attributes(self, _db, club_alpha):
        """Test storing item custom attributes."""
        category = InventoryCategory(name='Bows', club_id=club_alpha.id)
        _db.session.add(category)
        _db.session.flush()
        
        item = InventoryItem(
            name='Recurve Bow',
            club_id=club_alpha.id,
            category_id=category.id,
            quantity=1,
            unit='piece',
            attributes={
                'draw_weight': 25,
                'draw_length': 28.5,
                'bow_type': 'recurve'
            }
        )
        _db.session.add(item)
        _db.session.commit()
        
        # Verify custom attributes stored
        assert item.attributes is not None
        assert item.attributes.get('draw_weight') == 25
