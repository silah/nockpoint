# Example: Adding a pro feature to inventory blueprint

from app.pro_features import pro_feature_required

@inventory_bp.route('/analytics')
@login_required
@admin_required
@pro_feature_required('advanced_inventory')
def inventory_analytics():
    """Advanced inventory analytics - Pro feature"""
    # This route will automatically check if 'advanced_inventory' pro feature is enabled
    # If not, it redirects to dashboard with a flash message
    return render_template('inventory/analytics.html')

@competitions_bp.route('/tournament-bracket/<int:id>')
@login_required
@pro_feature_required('advanced_competitions')
def tournament_bracket(id):
    """Tournament bracket view - Pro feature"""
    competition = Competition.query.get_or_404(id)
    return render_template('competitions/tournament_bracket.html', competition=competition)