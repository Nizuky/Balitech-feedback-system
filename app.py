import os
import sys
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import HTTPException
from datetime import datetime
from sqlalchemy import inspect, text
from config import config

# When running `python app.py`, ensure imports like `from app import db`
# point to this same module instance (not a second copy named `app`).
if __name__ == '__main__':
    sys.modules['app'] = sys.modules[__name__]

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Import models
        from models import User, MenuItem, Question, Feedback, Form, FormQuestion, FormOption, FormResponse, FormAnswer
        
        # Register blueprints (routes)
        from routes.auth import auth_bp
        from routes.feedback import feedback_bp
        from routes.admin import admin_bp
        from routes.forms import forms_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(feedback_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(forms_bp)
        
        # Create tables if they don't exist
        db.create_all()

        # Lightweight schema alignment for older databases (without migrations yet).
        try:
            inspector = inspect(db.engine)
            user_columns = [c['name'] for c in inspector.get_columns('users')]
            if 'is_active' not in user_columns:
                db.session.execute(text('ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE'))
                db.session.commit()
        except Exception:
            db.session.rollback()

        @app.route('/')
        def index():
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('forms.list_public_forms'))

        @app.route('/health')
        def health():
            return jsonify({'status': 'ok'}), 200

        @app.errorhandler(404)
        def not_found(error):
            if request.path.startswith('/api/') or request.path.startswith('/admin/api/') or request.path.startswith('/feedback/api/'):
                return jsonify({'status': 'error', 'message': 'Resource not found'}), 404
            # Return a simple error page instead of login for 404s
            return f"<h1>Page Not Found</h1><p>The page {request.path} was not found. <a href='/feedback/dashboard'>Return to Dashboard</a></p>", 404

        @app.errorhandler(Exception)
        def handle_exception(error):
            if isinstance(error, HTTPException):
                if request.path.startswith('/api/') or request.path.startswith('/admin/api/') or request.path.startswith('/feedback/api/'):
                    return jsonify({'status': 'error', 'message': error.description}), error.code
                return error

            # For unexpected server errors, keep API responses JSON-consistent.
            if request.path.startswith('/api/') or request.path.startswith('/admin/api/') or request.path.startswith('/feedback/api/'):
                return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

            # Log the error and return an error message
            import traceback
            error_msg = traceback.format_exc()
            print(f"Server error: {error_msg}", file=sys.stderr)
            return f"<h1>Server Error</h1><p>{str(error)}</p><p><a href='/feedback/dashboard'>Return to Dashboard</a></p>", 500
    
    return app

if __name__ == '__main__':
    app = create_app(os.environ.get('FLASK_ENV', 'development'))
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
