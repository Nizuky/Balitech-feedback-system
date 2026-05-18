"""
Database initialization script for PostgreSQL.
This script creates the database schema and inserts seed data.

Usage:
    Local: DATABASE_URL="postgresql://user:password@localhost:5432/balitech_db" python init_db_postgres.py
    Render: DATABASE_URL="<render-db-url>" python init_db_postgres.py
"""

import os
import sys


def load_env_file(env_path='.env'):
    """Load simple KEY=VALUE pairs from a local .env file if present."""
    if not os.path.exists(env_path):
        return

    with open(env_path, 'r', encoding='utf-8') as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


# Load environment variables
load_env_file()

# Add parent directory to path so we can import app module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, MenuItem, Question, Feedback
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with schema and seed data."""
    # Get the environment (default to development)
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create app context
    app = create_app(env)
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Tables created successfully")
        
        # Check if data already exists
        if User.query.first():
            print("\n⚠ Database already contains data. Skipping seed data insertion.")
            return
        
        print("\nInserting seed data...")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@balitech.com',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create test user
        test_user = User(
            username='customer1',
            email='customer1@example.com',
            role='user'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        
        db.session.commit()
        print("✓ Users created")
        
        # Create sample topics (formerly menu items)
        menu_items = [
            MenuItem(item_name='Website Usability', description='Questions about site navigation and ease of use'),
            MenuItem(item_name='Course Content', description='Questions about the helpfulness and clarity of course material'),
            MenuItem(item_name='Customer Support', description='Questions about support responsiveness and usefulness'),
            MenuItem(item_name='Product Features', description='Questions about feature completeness and usefulness'),
            MenuItem(item_name='Onboarding Experience', description='Questions about the onboarding process'),
        ]
        db.session.add_all(menu_items)
        db.session.commit()
        print("✓ Menu items created")
        
        # Create overall survey questions
        overall_questions = [
            Question(question_text='How would you describe your overall experience?', menu_item_id=None),
            Question(question_text='Did the content meet your expectations?', menu_item_id=None),
            Question(question_text='Would you recommend this to a colleague?', menu_item_id=None),
        ]
        db.session.add_all(overall_questions)
        db.session.commit()
        print("✓ Overall questions created")
        
        # Create menu-specific questions
        for item in menu_items:
            q1 = Question(
                question_text=f'Please share your thoughts about {item.item_name}.',
                menu_item_id=item.id
            )
            q2 = Question(
                question_text=f'What could be improved about {item.item_name}?',
                menu_item_id=item.id
            )
            db.session.add(q1)
            db.session.add(q2)
        
        db.session.commit()
        print("✓ Item-specific questions created")
        
        # Create sample feedback
        feedback_samples = [
            Feedback(
                user_id=test_user.id,
                question_id=1,
                menu_item_id=None,
                comment='Clear and helpful content overall.'
            ),
            Feedback(
                user_id=test_user.id,
                question_id=overall_questions[0].id,
                menu_item_id=menu_items[0].id,
                comment='The website navigation was intuitive and fast.'
            ),
        ]
        db.session.add_all(feedback_samples)
        db.session.commit()
        print("✓ Sample feedback created")
        
        print("\n" + "="*50)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*50)
        print("\nTest Credentials:")
        print("  Admin User:")
        print("    Username: admin")
        print("    Password: admin123")
        print("\n  Test User:")
        print("    Username: customer1")
        print("    Password: password123")
        print("\n" + "="*50)

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n✗ Error initializing database: {e}")
        sys.exit(1)
