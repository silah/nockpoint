# Example: Using pro features in Python code

from app.pro_features import check_pro_feature
from app.models import ClubSettings

def generate_report():
    """Generate different reports based on pro status"""
    
    if check_pro_feature('member_analytics'):
        # Generate advanced analytics report
        return generate_advanced_analytics()
    else:
        # Generate basic report
        return generate_basic_report()

def get_available_features():
    """Get list of available features for current subscription"""
    settings = ClubSettings.get_settings()
    
    features = {
        'basic': ['inventory', 'events', 'members', 'competitions'],
        'pro': []
    }
    
    if settings.is_pro_active():
        # Add all enabled pro features
        enabled_features = settings.pro_features_enabled or []
        features['pro'] = enabled_features
    
    return features

def customize_dashboard_widgets():
    """Return different dashboard widgets based on pro features"""
    widgets = ['events', 'members', 'inventory']
    
    if check_pro_feature('member_analytics'):
        widgets.append('member_stats')
    
    if check_pro_feature('financial_reporting'):
        widgets.append('revenue_chart')
    
    if check_pro_feature('advanced_competitions'):
        widgets.append('tournament_bracket')
    
    return widgets