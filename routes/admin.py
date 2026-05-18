from functools import wraps

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import func

from app import db
from models import Form, FormResponse, User, Question, Feedback

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('auth.admin_login'))
        return f(*args, **kwargs)

    return decorated_function


@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    return render_template('admin_dashboard.html')


@admin_bp.route('/api/stats', methods=['GET'])
@admin_required
def get_stats():
    return jsonify(
        {
            'status': 'success',
            'stats': {
                'users': User.query.count(),
                'forms': Form.query.count(),
                'responses': FormResponse.query.count(),
                'feedback': Feedback.query.count(),
                'questions': Question.query.count(),
            },
        }
    )


@admin_bp.route('/api/users', methods=['GET'])
@admin_required
def get_users():
    rows = (
        db.session.query(
            User.id,
            User.username,
            User.email,
            User.role,
            User.is_active,
            User.created_at,
            func.count(Form.id).label('form_count'),
        )
        .outerjoin(Form, Form.creator_id == User.id)
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .all()
    )

    return jsonify(
        {
            'status': 'success',
            'users': [
                {
                    'id': r.id,
                    'username': r.username,
                    'email': r.email,
                    'role': r.role,
                    'is_active': bool(r.is_active),
                    'created_at': r.created_at.isoformat(),
                    'form_count': int(r.form_count or 0),
                }
                for r in rows
            ],
        }
    )


@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json() or {}

    # Protect current admin account from being deactivated accidentally.
    if user.id == session.get('user_id') and data.get('is_active') is False:
        return jsonify({'status': 'error', 'message': 'You cannot deactivate your own account'}), 400

    role = data.get('role')
    if role in ['admin', 'public_user']:
        user.role = role

    if 'is_active' in data:
        user.is_active = bool(data.get('is_active'))

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User updated'})


@admin_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == session.get('user_id'):
        return jsonify({'status': 'error', 'message': 'You cannot delete your own account'}), 400
    db.session.delete(user)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'User deleted'})


@admin_bp.route('/api/forms', methods=['GET'])
@admin_required
def get_forms():
    rows = (
        db.session.query(
            Form.id,
            Form.public_id,
            Form.title,
            Form.is_published,
            Form.created_at,
            User.username,
            func.count(FormResponse.id).label('response_count'),
        )
        .join(User, User.id == Form.creator_id)
        .outerjoin(FormResponse, FormResponse.form_id == Form.id)
        .group_by(Form.id, User.username)
        .order_by(Form.created_at.desc())
        .all()
    )

    return jsonify(
        {
            'status': 'success',
            'forms': [
                {
                    'id': r.id,
                    'public_id': r.public_id,
                    'title': r.title,
                    'is_published': bool(r.is_published),
                    'creator_username': r.username,
                    'created_at': r.created_at.isoformat(),
                    'response_count': int(r.response_count or 0),
                }
                for r in rows
            ],
        }
    )


@admin_bp.route('/api/forms/<int:form_id>', methods=['PUT'])
@admin_required
def update_form(form_id):
    form = Form.query.get_or_404(form_id)
    data = request.get_json() or {}

    if 'is_published' in data:
        form.is_published = bool(data.get('is_published'))

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Form updated'})


@admin_bp.route('/api/forms/<int:form_id>', methods=['DELETE'])
@admin_required
def delete_form(form_id):
    form = Form.query.get_or_404(form_id)
    db.session.delete(form)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Form deleted'})


@admin_bp.route('/api/responses', methods=['GET'])
@admin_required
def get_responses():
    rows = (
        db.session.query(
            FormResponse.id,
            Form.title,
            FormResponse.respondent_name,
            User.username,
            FormResponse.submitted_at,
        )
        .join(Form, Form.id == FormResponse.form_id)
        .outerjoin(User, User.id == FormResponse.respondent_user_id)
        .order_by(FormResponse.submitted_at.desc())
        .limit(300)
        .all()
    )

    responses = []
    for r in rows:
        who = r.respondent_name or r.username or 'Anonymous'
        responses.append(
            {
                'id': r.id,
                'form_title': r.title,
                'respondent': who,
                'submitted_at': r.submitted_at.isoformat(),
            }
        )

    return jsonify({'status': 'success', 'responses': responses})
