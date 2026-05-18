import json
import secrets
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from app import db
from models import Form, FormQuestion, FormOption, FormResponse, FormAnswer
from functools import wraps

forms_bp = Blueprint('forms', __name__)


def creator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('role') not in ['user', 'admin', 'public_user']:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@forms_bp.route('/forms')
def list_public_forms():
    now = datetime.utcnow()
    forms = Form.query.filter(Form.is_published.is_(True)).all()

    visible = []
    for f in forms:
        if f.opens_at and f.opens_at > now:
            continue
        if f.closes_at and f.closes_at < now:
            continue
        visible.append(f)

    return render_template('forms_public_list.html', forms=visible)


@forms_bp.route('/forms/<string:public_id>')
def answer_form(public_id):
    form = Form.query.filter_by(public_id=public_id, is_published=True).first_or_404()
    return render_template('form_answer.html', form=form)


@forms_bp.route('/forms/<string:public_id>/submit', methods=['POST'])
def submit_form(public_id):
    form = Form.query.filter_by(public_id=public_id, is_published=True).first_or_404()
    payload = request.get_json() or {}

    respondent_name = (payload.get('respondent_name') or '').strip() or None
    answers = payload.get('answers') or {}

    response = FormResponse(
        form_id=form.id,
        respondent_user_id=None,
        respondent_name=respondent_name
    )
    db.session.add(response)
    db.session.flush()

    for q in form.questions:
        raw = answers.get(str(q.id))

        if q.required and (raw is None or raw == '' or raw == []):
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Question "{q.label}" is required'}), 400

        answer = FormAnswer(response_id=response.id, question_id=q.id)
        if raw is None:
            db.session.add(answer)
            continue

        if q.question_type == 'text':
            answer.value_text = str(raw)
        elif q.question_type in ['dropdown', 'multiple_choice']:
            answer.value_choice = str(raw)
        elif q.question_type == 'checkbox':
            if isinstance(raw, list):
                answer.value_choices_json = json.dumps(raw)
            else:
                answer.value_choices_json = json.dumps([raw])
        else:
            answer.value_text = str(raw)

        db.session.add(answer)

    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Response submitted successfully'})


@forms_bp.route('/creator/dashboard')
@creator_required
def creator_dashboard():
    forms = Form.query.filter_by(creator_id=session['user_id']).order_by(Form.created_at.desc()).all()
    return render_template('creator_dashboard.html', forms=forms)


@forms_bp.route('/creator/responses')
@creator_required
def creator_responses_dashboard():
    forms = Form.query.filter_by(creator_id=session['user_id']).order_by(Form.created_at.desc()).all()

    response_groups = []
    for form in forms:
        responses = FormResponse.query.filter_by(form_id=form.id).order_by(FormResponse.submitted_at.desc()).all()
        grouped_responses = []

        for response in responses:
            answers = []
            for answer in response.answers:
                question = answer.question
                if answer.value_choices_json:
                    try:
                        value = json.loads(answer.value_choices_json)
                    except json.JSONDecodeError:
                        value = []
                elif answer.value_choice is not None:
                    value = answer.value_choice
                else:
                    value = answer.value_text

                answers.append({
                    'question': question.label,
                    'type': question.question_type,
                    'value': value,
                })

            grouped_responses.append({
                'id': response.id,
                'respondent_name': response.respondent_name,
                'submitted_at': response.submitted_at,
                'answers': answers,
            })

        response_groups.append({
            'form': form,
            'responses': grouped_responses,
        })

    return render_template('creator_responses_dashboard.html', response_groups=response_groups)


def _serialize_form(form):
    return {
        'id': form.id,
        'public_id': form.public_id,
        'title': form.title,
        'description': form.description or '',
        'is_published': bool(form.is_published),
        'opens_at': form.opens_at.isoformat() if form.opens_at else '',
        'closes_at': form.closes_at.isoformat() if form.closes_at else '',
        'questions': [
            {
                'id': q.id,
                'label': q.label,
                'type': q.question_type,
                'required': bool(q.required),
                'position': q.position,
                'options': [opt.value for opt in q.options],
            }
            for q in form.questions
        ],
    }


@forms_bp.route('/creator/forms/new', methods=['GET', 'POST'])
@forms_bp.route('/creator/forms/<int:form_id>/edit', methods=['GET', 'POST'])
@creator_required
def creator_new_form(form_id=None):
    form = None
    if form_id is not None:
        form = Form.query.filter_by(id=form_id, creator_id=session['user_id']).first_or_404()

    if request.method == 'GET':
        return render_template('creator_new_form.html', form_data=_serialize_form(form) if form else None)

    data = request.get_json() or {}
    title = (data.get('title') or '').strip()
    description = (data.get('description') or '').strip()
    questions = data.get('questions') or []

    if not title:
        return jsonify({'status': 'error', 'message': 'Form title is required'}), 400

    if not questions:
        return jsonify({'status': 'error', 'message': 'At least one question is required'}), 400

    if form is None:
        form = Form(
            public_id=secrets.token_urlsafe(8),
            title=title,
            description=description,
            creator_id=session['user_id'],
            is_published=bool(data.get('is_published', True))
        )
        db.session.add(form)
        db.session.flush()
    else:
        form.title = title
        form.description = description
        form.is_published = bool(data.get('is_published', form.is_published))

    opens_at = data.get('opens_at')
    closes_at = data.get('closes_at')
    form.opens_at = datetime.fromisoformat(opens_at) if opens_at else None
    form.closes_at = datetime.fromisoformat(closes_at) if closes_at else None

    # Replace the question set wholesale so creators can delete/change types safely.
    existing_questions = list(form.questions)
    for existing_question in existing_questions:
        db.session.delete(existing_question)
    db.session.flush()

    for idx, q in enumerate(questions):
        q_type = q.get('type')
        if q_type not in ['text', 'multiple_choice', 'checkbox']:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Unsupported question type: {q_type}'}), 400

        label = (q.get('label') or '').strip()
        if not label:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': 'Question label is required'}), 400

        options = [str(opt).strip() for opt in (q.get('options') or []) if str(opt).strip()]
        if q_type in ['multiple_choice', 'checkbox'] and not options:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'Options are required for question: {label}'}), 400

        fq = FormQuestion(
            form_id=form.id,
            label=label,
            question_type=q_type,
            required=bool(q.get('required', False)),
            position=idx
        )
        db.session.add(fq)
        db.session.flush()

        for o_idx, val in enumerate(options):
            db.session.add(FormOption(question_id=fq.id, value=val, position=o_idx))

    db.session.commit()
    return jsonify({
        'status': 'success',
        'message': 'Form saved',
        'form': {
            'id': form.id,
            'public_id': form.public_id,
            'title': form.title,
            'public_url': url_for('forms.answer_form', public_id=form.public_id),
            'edit_url': url_for('forms.creator_new_form', form_id=form.id)
        }
    }), 201


@forms_bp.route('/creator/forms/<int:form_id>/delete', methods=['POST'])
@creator_required
def creator_delete_form(form_id):
    form = Form.query.filter_by(id=form_id, creator_id=session['user_id']).first_or_404()
    db.session.delete(form)
    db.session.commit()
    return jsonify({'status': 'success', 'message': 'Form deleted'})


@forms_bp.route('/creator/forms/<int:form_id>/toggle', methods=['POST'])
@creator_required
def creator_toggle_form(form_id):
    form = Form.query.filter_by(id=form_id, creator_id=session['user_id']).first_or_404()
    form.is_published = not bool(form.is_published)
    db.session.commit()
    return jsonify({'status': 'success', 'is_published': bool(form.is_published)})
