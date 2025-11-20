"""
Club utility functions and decorators for multi-tenancy support.

This module provides helper functions and decorators to manage club context
in the multi-tenant Nockpoint application.
"""

from flask import g, session, abort, flash, redirect, url_for
from flask_login import current_user
from functools import wraps


def get_current_club():
    """
    Get the current club from request context.
    
    Returns:
        Club or None: The current club object if set, None otherwise
    """
    return getattr(g, 'current_club', None)


def get_current_membership():
    """
    Get the current user's membership in the current club.
    
    Returns:
        ClubMembership or None: The membership object if exists, None otherwise
    """
    return getattr(g, 'current_membership', None)


def set_current_club(club_id):
    """
    Set the current club in the session.
    
    Args:
        club_id (int): The ID of the club to set as current
    """
    session['current_club_id'] = club_id


def clear_current_club():
    """Clear the current club from the session."""
    session.pop('current_club_id', None)


def require_club_context(f):
    """
    Decorator to ensure a club context is set.
    
    Redirects to club selection if no club is set.
    
    Usage:
        @require_club_context
        def my_view():
            # club context is guaranteed here
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_club():
            flash('Please select a club first.', 'warning')
            return redirect(url_for('auth.select_club'))
        return f(*args, **kwargs)
    return decorated_function


def require_club_admin(f):
    """
    Decorator to require admin role in the current club.
    
    Returns 403 if user is not an admin of the current club.
    Redirects to club selection if no club context.
    
    Usage:
        @login_required
        @require_club_admin
        def admin_view():
            # user is guaranteed to be admin of current club
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        club = get_current_club()
        
        if not club:
            flash('Please select a club first.', 'warning')
            return redirect(url_for('auth.select_club'))
        
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin_of_club(club.id):
            flash('Admin access required for this club.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def require_club_member(f):
    """
    Decorator to require membership in the current club.
    
    Returns 403 if user is not a member of the current club.
    Redirects to club selection if no club context.
    
    Usage:
        @login_required
        @require_club_member
        def member_view():
            # user is guaranteed to be a member of current club
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        club = get_current_club()
        
        if not club:
            flash('Please select a club first.', 'warning')
            return redirect(url_for('auth.select_club'))
        
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_member_of_club(club.id):
            flash('You are not a member of this club.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def club_query(model_class):
    """
    Helper function to filter queries by current club.
    
    Automatically adds club_id filter if the model has a club_id attribute
    and a club context is set.
    
    Args:
        model_class: The SQLAlchemy model class to query
        
    Returns:
        Query: A query object filtered by current club
        
    Usage:
        items = club_query(InventoryItem).all()
        event = club_query(ShootingEvent).filter_by(id=event_id).first()
    """
    club = get_current_club()
    
    if club and hasattr(model_class, 'club_id'):
        return model_class.query.filter_by(club_id=club.id)
    
    return model_class.query


def verify_club_access(club_id):
    """
    Verify that the current user has access to a specific club.
    
    Args:
        club_id (int): The ID of the club to verify access to
        
    Returns:
        bool: True if user has access, False otherwise
    """
    if not current_user.is_authenticated:
        return False
    
    return current_user.is_member_of_club(club_id)


def get_user_clubs():
    """
    Get all clubs the current user is a member of.
    
    Returns:
        list: List of Club objects the user is a member of
    """
    if not current_user.is_authenticated:
        return []
    
    return current_user.get_clubs()
