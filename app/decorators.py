"""
Shared decorators for multi-tenant authorization and club context enforcement.

This module provides reusable decorators that ensure proper club context
and authorization across all blueprints in the application.
"""

from flask import g, flash, redirect, url_for, abort
from flask_login import current_user
from functools import wraps


def require_club_context(f):
    """
    Decorator to ensure a club context is set before accessing a view.
    
    Redirects to login if no club is currently selected.
    Should be used after @login_required.
    
    Usage:
        @login_required
        @require_club_context
        def my_view():
            # g.current_club is guaranteed to exist here
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_club') or g.current_club is None:
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def require_club_admin(f):
    """
    Decorator to require admin role in the current club.
    
    Returns 403 if user is not an admin of the current club.
    Redirects to club selection if no club context is set.
    Must be used after @login_required.
    
    Usage:
        @login_required
        @require_club_admin
        def admin_only_view():
            # user is guaranteed to be admin of g.current_club
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if club context exists
        if not hasattr(g, 'current_club') or g.current_club is None:
            flash('Your session has expired. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        
        # Check if user is authenticated (should be, but double-check)
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is admin of the current club
        if not current_user.is_admin_of_club(g.current_club.id):
            flash('Administrator access required for this action.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def require_club_member(f):
    """
    Decorator to require membership (any role) in the current club.
    
    Returns 403 if user is not a member of the current club.
    Redirects to club selection if no club context is set.
    Must be used after @login_required.
    
    Usage:
        @login_required
        @require_club_member
        def member_view():
            # user is guaranteed to be a member of g.current_club
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # First check if club context exists
        if not hasattr(g, 'current_club') or g.current_club is None:
            flash('Please select a club first.', 'warning')
            return redirect(url_for('auth.select_club'))
        
        # Check if user is authenticated
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Check if user is a member of the current club
        if not current_user.is_member_of_club(g.current_club.id):
            flash('You must be a member of this club to access this page.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    DEPRECATED: Use @require_club_admin instead.
    
    This decorator is maintained for backward compatibility during migration.
    It checks the deprecated User.role field rather than club-specific roles.
    
    Will be removed in a future version.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        # Try club-specific admin check first if club context exists
        if hasattr(g, 'current_club') and g.current_club:
            if not current_user.is_admin_of_club(g.current_club.id):
                flash('Administrator access required.', 'error')
                abort(403)
        # Fall back to deprecated global role check
        elif not hasattr(current_user, 'role') or current_user.role != 'admin':
            flash('Administrator access required.', 'error')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
