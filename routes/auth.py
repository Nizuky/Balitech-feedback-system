from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from models import User
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Validation
        if not username or not email or not password:
            return jsonify({'status': 'error', 'message': 'All fields required'}), 400
        
        if len(password) < 6:
            return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=username).first():
            return jsonify({'status': 'error', 'message': 'Username already exists'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'status': 'error', 'message': 'Email already registered'}), 400
        
        # Create public creator account
        user = User(username=username, email=email, role='public_user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Registration successful! Please log in.'}), 201
    
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Unified login for both creator and admin accounts."""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'status': 'error', 'message': 'Username and password required'}), 400
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

        if not user.is_active:
            return jsonify({'status': 'error', 'message': 'This account is deactivated.'}), 403
        
        # Create session
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role
        
        # Route based on user role
        if user.role == 'admin':
            redirect_url = url_for('admin.dashboard')
        else:
            redirect_url = url_for('forms.creator_dashboard')
        
        return jsonify({'status': 'success', 'message': 'Login successful!', 'redirect': redirect_url}), 200
    
    return render_template('login.html')


@auth_bp.route('/admin-login', methods=['GET'])
def admin_login():
    """Redirect admin login attempts to unified login page."""
    return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    """User logout."""
    session.clear()
    return redirect(url_for('forms.list_public_forms'))

@auth_bp.before_app_request
def load_logged_in_user():
    """Load user from session for every request."""
    if 'user_id' in session:
        # Could load full user object if needed
        pass
