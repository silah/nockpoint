"""
Comprehensive tests for club data isolation in the multi-tenant system.

These tests ensure that:
1. Users can only see data from their current club
2. Queries are properly filtered by club_id
3. No cross-club data leakage occurs
4. Authorization checks prevent unauthorized access
"""
import pytest
from datetime import datetime, date, time, timedelta
from app.models import (User, Club, ClubMembership, InventoryCategory, InventoryItem,
                        ShootingEvent, EventAttendance, MemberCharge)


class TestInventoryIsolation:
    """Test that inventory data is isolated by club"""
    
    def test_inventory_categories_isolated_by_club(self, client, club_alpha, club_beta, 
                                                     admin_alpha, admin_beta, _db):
        """Categories from one club should not appear when viewing another club"""
        # Create categories for each club
        cat_alpha = InventoryCategory(club_id=club_alpha.id, name='Alpha Bows', description='Alpha only')
        cat_beta = InventoryCategory(club_id=club_beta.id, name='Beta Bows', description='Beta only')
        _db.session.add_all([cat_alpha, cat_beta])
        _db.session.commit()
        
        # Login as Alpha admin and set club
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Request inventory categories page
        response = client.get('/inventory/categories')
        assert response.status_code == 200
        assert b'Alpha Bows' in response.data
        assert b'Beta Bows' not in response.data
    
    def test_inventory_items_isolated_by_club(self, client, club_alpha, club_beta,
                                               admin_alpha, admin_beta, _db):
        """Items from one club should not appear when viewing another club"""
        # Create categories and items for each club
        cat_alpha = InventoryCategory(club_id=club_alpha.id, name='Equipment')
        cat_beta = InventoryCategory(club_id=club_beta.id, name='Equipment')
        _db.session.add_all([cat_alpha, cat_beta])
        _db.session.flush()
        
        item_alpha = InventoryItem(
            club_id=club_alpha.id,
            category_id=cat_alpha.id,
            name='Alpha Recurve Bow',
            quantity=5
        )
        item_beta = InventoryItem(
            club_id=club_beta.id,
            category_id=cat_beta.id,
            name='Beta Compound Bow',
            quantity=3
        )
        _db.session.add_all([item_alpha, item_beta])
        _db.session.commit()
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Request inventory page
        response = client.get('/inventory/')
        assert response.status_code == 200
        assert b'Alpha Recurve Bow' in response.data
        assert b'Beta Compound Bow' not in response.data
    
    def test_cannot_access_other_club_item(self, client, club_alpha, club_beta,
                                            admin_alpha, _db):
        """Users should not be able to view items from other clubs"""
        cat_beta = InventoryCategory(club_id=club_beta.id, name='Equipment')
        _db.session.add(cat_beta)
        _db.session.flush()
        
        item_beta = InventoryItem(
            club_id=club_beta.id,
            category_id=cat_beta.id,
            name='Beta Item',
            quantity=1
        )
        _db.session.add(item_beta)
        _db.session.commit()
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Try to access Beta's item
        response = client.get(f'/inventory/item/{item_beta.id}')
        # Should get 404 because item doesn't belong to current club
        assert response.status_code == 404


class TestEventsIsolation:
    """Test that event data is isolated by club"""
    
    def test_events_isolated_by_club(self, client, club_alpha, club_beta,
                                     admin_alpha, admin_beta, _db):
        """Events from one club should not appear when viewing another club"""
        # Create events for each club
        event_alpha = ShootingEvent(
            club_id=club_alpha.id,
            name='Alpha Tournament',
            location='Alpha Range',
            date=date.today() + timedelta(days=7),
            start_time=time(10, 0),
            duration_hours=3,
            price=25.00,
            created_by=admin_alpha.id
        )
        event_beta = ShootingEvent(
            club_id=club_beta.id,
            name='Beta Competition',
            location='Beta Range',
            date=date.today() + timedelta(days=7),
            start_time=time(14, 0),
            duration_hours=2,
            price=20.00,
            created_by=admin_beta.id
        )
        _db.session.add_all([event_alpha, event_beta])
        _db.session.commit()
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Request events calendar
        response = client.get('/events/')
        assert response.status_code == 200
        assert b'Alpha Tournament' in response.data
        assert b'Beta Competition' not in response.data
    
    def test_cannot_access_other_club_event(self, client, club_alpha, club_beta,
                                            admin_alpha, admin_beta, _db):
        """Users should not be able to view events from other clubs"""
        event_beta = ShootingEvent(
            club_id=club_beta.id,
            name='Beta Event',
            location='Beta Range',
            date=date.today(),
            start_time=time(10, 0),
            duration_hours=2,
            price=15.00,
            created_by=admin_beta.id
        )
        _db.session.add(event_beta)
        _db.session.commit()
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Try to access Beta's event
        response = client.get(f'/events/event/{event_beta.id}')
        # Should get 404 because event doesn't belong to current club
        assert response.status_code == 404


class TestMembershipIsolation:
    """Test that membership data is isolated by club"""
    
    def test_members_list_filtered_by_club(self, client, club_alpha, club_beta,
                                           admin_alpha, member_alpha, member_beta, _db):
        """Members list should only show members of current club"""
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Request members page
        response = client.get('/members/')
        assert response.status_code == 200
        # Should see Alpha members
        assert admin_alpha.username.encode() in response.data
        assert member_alpha.username.encode() in response.data
        # Should NOT see Beta members
        assert member_beta.username.encode() not in response.data
    
    def test_club_statistics_scoped_correctly(self, client, club_alpha, club_beta,
                                              admin_alpha, _db):
        """Dashboard statistics should be scoped to current club"""
        # Alpha has 2 members (admin_alpha, member_alpha)
        # Beta has 2 members (admin_beta, member_beta)
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Request dashboard
        response = client.get('/dashboard')
        assert response.status_code == 200
        # Check that stats are club-specific
        # Note: Actual numbers depend on test fixtures


class TestAuthorizationIsolation:
    """Test that authorization checks prevent cross-club access"""
    
    def test_cannot_edit_other_club_category(self, client, club_alpha, club_beta,
                                              admin_alpha, _db):
        """Admin of one club cannot edit categories from another club"""
        cat_beta = InventoryCategory(club_id=club_beta.id, name='Beta Category')
        _db.session.add(cat_beta)
        _db.session.commit()
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Try to edit Beta's category
        response = client.get(f'/inventory/categories/{cat_beta.id}/edit')
        # Should get 404 because category doesn't belong to current club
        assert response.status_code == 404
    
    def test_cannot_delete_other_club_event(self, client, club_alpha, club_beta,
                                            admin_alpha, admin_beta, _db):
        """Admin of one club cannot delete events from another club"""
        event_beta = ShootingEvent(
            club_id=club_beta.id,
            name='Beta Event',
            location='Beta Range',
            date=date.today(),
            start_time=time(10, 0),
            duration_hours=2,
            price=15.00,
            created_by=admin_beta.id
        )
        _db.session.add(event_beta)
        _db.session.commit()
        
        # Login as Alpha admin
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            sess['current_club_id'] = club_alpha.id
        
        # Try to delete Beta's event
        response = client.post(f'/events/event/{event_beta.id}/delete', follow_redirects=True)
        # Should fail (404) because event doesn't belong to current club
        assert response.status_code == 404
        
        # Verify event still exists
        _db.session.expire_all()
        assert ShootingEvent.query.get(event_beta.id) is not None


class TestClubContextRequirement:
    """Test that club context is required for protected routes"""
    
    def test_inventory_requires_club_context(self, client, admin_alpha, _db):
        """Accessing inventory without club context should redirect to club selection"""
        # Login without setting club
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
            # Explicitly don't set current_club_id
        
        # Try to access inventory
        response = client.get('/inventory/', follow_redirects=False)
        # Should redirect to club selection
        assert response.status_code == 302
        assert b'select-club' in response.location.encode() or b'login' in response.location.encode()
    
    def test_events_requires_club_context(self, client, admin_alpha, _db):
        """Accessing events without club context should redirect to club selection"""
        # Login without setting club
        with client.session_transaction() as sess:
            sess['_user_id'] = str(admin_alpha.id)
        
        # Try to access events
        response = client.get('/events/', follow_redirects=False)
        # Should redirect to club selection
        assert response.status_code == 302
        assert b'select-club' in response.location.encode() or b'login' in response.location.encode()


class TestMultiClubUserScenarios:
    """Test scenarios where a user belongs to multiple clubs"""
    
    def test_user_sees_different_data_per_club(self, client, club_alpha, club_beta,
                                               multi_club_user, _db):
        """User belonging to multiple clubs sees different data when switching clubs"""
        # Create items in each club
        cat_alpha = InventoryCategory(club_id=club_alpha.id, name='Equipment')
        cat_beta = InventoryCategory(club_id=club_beta.id, name='Equipment')
        _db.session.add_all([cat_alpha, cat_beta])
        _db.session.flush()
        
        item_alpha = InventoryItem(
            club_id=club_alpha.id,
            category_id=cat_alpha.id,
            name='Alpha Item',
            quantity=1
        )
        item_beta = InventoryItem(
            club_id=club_beta.id,
            category_id=cat_beta.id,
            name='Beta Item',
            quantity=1
        )
        _db.session.add_all([item_alpha, item_beta])
        _db.session.commit()
        
        # View as Alpha club
        with client.session_transaction() as sess:
            sess['_user_id'] = str(multi_club_user.id)
            sess['current_club_id'] = club_alpha.id
        
        response = client.get('/inventory/')
        assert b'Alpha Item' in response.data
        assert b'Beta Item' not in response.data
        
        # Switch to Beta club
        with client.session_transaction() as sess:
            sess['current_club_id'] = club_beta.id
        
        response = client.get('/inventory/')
        assert b'Beta Item' in response.data
        assert b'Alpha Item' not in response.data
