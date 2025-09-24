from app import create_app, db
from app.models import User, InventoryCategory, InventoryItem
from flask.cli import with_appcontext
import click

app = create_app()

@app.cli.command("init-db")
@with_appcontext
def init_db_command():
    """Create database tables."""
    db.create_all()
    
    # Create default categories
    default_categories = [
        {'name': 'Bows', 'description': 'Recurve, compound, and traditional bows'},
        {'name': 'Arrows', 'description': 'Carbon, aluminum, and wooden arrows'},
        {'name': 'Targets', 'description': 'Target backstops, stands, and boss materials (straw, foam)'},
        {'name': 'Target Faces', 'description': 'Paper and plastic target faces in standard sizes (20, 40, 60, 80, 122 cm)'},
        {'name': 'Safety Equipment', 'description': 'Arm guards, finger tabs, chest guards'},
        {'name': 'Accessories', 'description': 'Quivers, bow stands, and other accessories'},
        {'name': 'Maintenance', 'description': 'Bow strings, wax, tools'},
        {'name': 'Arrow Consumables', 'description': 'Tips, vanes, feathers, nocks, shafts'},
    ]
    
    for cat_data in default_categories:
        if not InventoryCategory.query.filter_by(name=cat_data['name']).first():
            category = InventoryCategory(**cat_data)
            db.session.add(category)
    
    # Create default admin user
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin = User(
            username='admin',
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
    
    db.session.commit()
    click.echo('Database initialized with default data.')

@app.cli.command("create-admin")
@click.argument("username")
@click.argument("email")
@click.argument("password")
@with_appcontext
def create_admin_command(username, email, password):
    """Create an admin user."""
    if User.query.filter_by(username=username).first():
        click.echo(f'User {username} already exists.')
        return
    
    admin = User(
        username=username,
        email=email,
        first_name='Admin',
        last_name='User',
        role='admin'
    )
    admin.set_password(password)
    db.session.add(admin)
    db.session.commit()
    click.echo(f'Admin user {username} created.')

if __name__ == '__main__':
    app.run(debug=True)
