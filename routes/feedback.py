from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from models import Feedback, MenuItem, Question, User
from functools import wraps

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@feedback_bp.route('/success')
@login_required
def success():
    """Success page after feedback submission."""
    return render_template('feedback_success.html')

@feedback_bp.route('/api/menu_items')
@login_required
def get_menu_items():
    """API endpoint to fetch menu items."""
    items = MenuItem.query.all()
    return jsonify({
        'status': 'success',
        'items': [{'id': item.id, 'name': item.item_name, 'description': item.description} for item in items]
    })

@feedback_bp.route('/api/questions/<int:item_id>')
@login_required
def get_item_questions(item_id):
    """API endpoint to fetch questions for a specific menu item."""
    questions = Question.query.filter_by(menu_item_id=item_id).all()
    return jsonify({
        'status': 'success',
        'questions': [{'id': q.id, 'text': q.question_text} for q in questions]
    })

@feedback_bp.route('/api/overall_questions')
@login_required
def get_overall_questions():
    """API endpoint to fetch overall experience questions."""
    questions = Question.query.filter_by(menu_item_id=None).all()
    return jsonify({
        'status': 'success',
        'questions': [{'id': q.id, 'text': q.question_text} for q in questions]
    })

@feedback_bp.route('/api/submit_feedback', methods=['POST'])
@login_required
def submit_feedback():
    """API endpoint to submit feedback."""
    data = request.get_json()
    user_id = session.get('user_id')
    
    # Validate input
    if not data or 'question_id' not in data:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
    
    question_id = data.get('question_id')
    menu_item_id = data.get('menu_item_id')  # Can be null for overall experience
    comment = data.get('comment', '').strip()
    
    # Verify question exists
    question = Question.query.get(question_id)
    if not question:
        return jsonify({'status': 'error', 'message': 'Question not found'}), 404
    
    # Create feedback (generic response/comment stored)
    feedback = Feedback(
        user_id=user_id,
        question_id=question_id,
        menu_item_id=menu_item_id,
        comment=comment
    )
    
    db.session.add(feedback)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Thank you for your feedback!',
        'feedback_id': feedback.id
    }), 201


@feedback_bp.route('/api/menu_summaries')
@login_required
def menu_summaries():
    """Return topics with response counts."""
    from sqlalchemy import func
    summaries = db.session.query(
        MenuItem.id,
        MenuItem.item_name,
        MenuItem.description,
        func.count(Feedback.id).label('response_count')
    ).outerjoin(Feedback, MenuItem.id == Feedback.menu_item_id).group_by(MenuItem.id).all()

    items = []
    for s in summaries:
        items.append({
            'id': s.id,
            'name': s.item_name,
            'description': s.description,
            'response_count': int(s.response_count)
        })

    return jsonify({'status': 'success', 'items': items})


@feedback_bp.route('/api/menu/<int:item_id>/reviews')
@login_required
def menu_reviews(item_id):
    """Return reviews for a specific menu item. Query param `limit` (default 5)"""
    limit = request.args.get('limit', default=5, type=int)
    reviews_q = db.session.query(Feedback, User.username).join(User, User.id == Feedback.user_id).filter(Feedback.menu_item_id == item_id).order_by(Feedback.created_at.desc()).limit(limit).all()

    reviews = []
    for fb, username in reviews_q:
        reviews.append({
            'id': fb.id,
            'username': username,
            'comment': fb.comment,
            'created_at': fb.created_at.isoformat()
        })

    return jsonify({'status': 'success', 'reviews': reviews})


@feedback_bp.route('/menu/<int:item_id>/reviews')
@login_required
def menu_reviews_page(item_id):
    """Page showing all reviews for a menu item."""
    item = MenuItem.query.get_or_404(item_id)
    # fetch all feedback rows for this item and aggregate them per user so each user shows once
    reviews_q = db.session.query(Feedback, User.username).join(User, User.id == Feedback.user_id).filter(Feedback.menu_item_id == item_id).order_by(Feedback.created_at.desc()).all()

    # Aggregate responses per user: count and latest comment
    aggregated = {}
    for fb, username in reviews_q:
        key = username
        if key not in aggregated:
            aggregated[key] = {
                'username': username,
                'count': 0,
                'latest_comment': None,
                'latest_ts': fb.created_at
            }
        aggregated[key]['count'] += 1
        # prefer most recent non-empty comment
        if fb.comment and (aggregated[key]['latest_comment'] is None or fb.created_at > aggregated[key]['latest_ts']):
            aggregated[key]['latest_comment'] = fb.comment
            aggregated[key]['latest_ts'] = fb.created_at

    reviews = []
    for user, info in aggregated.items():
        reviews.append({'username': info['username'], 'response_count': info['count'], 'comment': info['latest_comment'] or '', 'created_at': info['latest_ts']})

    # sort by created_at desc
    reviews.sort(key=lambda r: r['created_at'], reverse=True)

    return render_template('menu_reviews.html', item=item, reviews=reviews)
