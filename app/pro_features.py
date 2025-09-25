"""
Pro Feature Management for Nockpoint Archery Club
Defines available pro features and provides utilities for checking access
"""

# Define all available pro features
PRO_FEATURES = {
    'advanced_inventory': {
        'name': 'Advanced Inventory Management',
        'description': 'Enhanced inventory tracking with maintenance schedules, depreciation, and detailed analytics',
        'category': 'inventory'
    },
    'advanced_competitions': {
        'name': 'Advanced Competition Features',
        'description': 'Tournament brackets, team management, advanced scoring systems, and leaderboards',
        'category': 'competitions'
    },
    'member_analytics': {
        'name': 'Member Analytics & Reporting',
        'description': 'Detailed member activity reports, attendance analytics, and performance tracking',
        'category': 'analytics'
    },
    'advanced_events': {
        'name': 'Advanced Event Management',
        'description': 'Recurring events, event templates, advanced scheduling, and event series',
        'category': 'events'
    },
    'financial_reporting': {
        'name': 'Financial Reporting',
        'description': 'Revenue tracking, expense management, financial reports, and budget planning',
        'category': 'finances'
    },
    'communication_tools': {
        'name': 'Communication Tools',
        'description': 'Email campaigns, SMS notifications, member messaging, and announcements',
        'category': 'communication'
    },
    'api_access': {
        'name': 'Enhanced API Access',
        'description': 'Full API access with higher rate limits for integrations and mobile apps',
        'category': 'api'
    },
    'custom_branding': {
        'name': 'Custom Branding',
        'description': 'Custom logo, colors, and club branding throughout the application',
        'category': 'branding'
    },
    'data_export': {
        'name': 'Advanced Data Export',
        'description': 'Export data in multiple formats (CSV, PDF, Excel) with custom reports',
        'category': 'data'
    },
    'coaching_tools': {
        'name': 'Coaching & Training Tools',
        'description': 'Training plans, progress tracking, skill assessments, and coaching notes',
        'category': 'coaching'
    }
}

# Feature categories for organization
FEATURE_CATEGORIES = {
    'inventory': 'Inventory & Equipment',
    'competitions': 'Competitions & Scoring',
    'analytics': 'Analytics & Reporting',
    'events': 'Event Management',
    'finances': 'Financial Management',
    'communication': 'Communication',
    'api': 'API & Integrations',
    'branding': 'Branding & Customization',
    'data': 'Data & Reports',
    'coaching': 'Coaching & Training'
}

def get_pro_features_by_category():
    """Get pro features organized by category"""
    categories = {}
    for feature_key, feature_info in PRO_FEATURES.items():
        category = feature_info['category']
        if category not in categories:
            categories[category] = {
                'name': FEATURE_CATEGORIES.get(category, category.title()),
                'features': []
            }
        categories[category]['features'].append({
            'key': feature_key,
            **feature_info
        })
    return categories

def is_pro_feature_available(feature_name):
    """Check if a pro feature exists in our feature list"""
    return feature_name in PRO_FEATURES

def check_pro_feature(feature_name=None):
    """Check if pro features are enabled for the current club - simplified to all-or-nothing"""
    from app.models import ClubSettings
    settings = ClubSettings.get_settings()
    return settings.is_pro_active()

def get_pro_status():
    """Get current pro subscription status"""
    from app.models import ClubSettings
    settings = ClubSettings.get_settings()
    return settings.get_pro_status()

# Decorator for protecting pro routes
def pro_feature_required(feature_name):
    """Decorator to require a specific pro feature for route access"""
    def decorator(f):
        from functools import wraps
        from flask import flash, redirect, url_for
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not check_pro_feature(feature_name):
                feature_info = PRO_FEATURES.get(feature_name, {})
                feature_display_name = feature_info.get('name', feature_name)
                flash(f'This feature ({feature_display_name}) requires a Pro subscription.', 'warning')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Template function for checking pro features in templates
def register_pro_template_functions(app):
    """Register pro feature functions for use in templates"""
    
    @app.template_global()
    def has_pro_feature(feature_name):
        """Template function to check if pro feature is enabled"""
        return check_pro_feature(feature_name)
    
    @app.template_global()
    def is_pro_active():
        """Template function to check if pro subscription is active"""
        from app.models import ClubSettings
        settings = ClubSettings.get_settings()
        return settings.is_pro_active()
    
    @app.template_global()
    def get_pro_feature_info(feature_name):
        """Template function to get pro feature information"""
        return PRO_FEATURES.get(feature_name, {})
    
    @app.template_global()
    def pro_status():
        """Template function to get pro status information"""
        return get_pro_status()