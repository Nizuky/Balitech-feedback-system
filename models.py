from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='public_user')  # 'public_user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedbacks = db.relationship('Feedback', backref='author', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    feedbacks = db.relationship('Feedback', backref='menu_item', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MenuItem {self.item_name}>'

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)  # NULL = Overall Experience
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    feedbacks = db.relationship('Feedback', backref='question', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Question {self.question_text[:50]}...>'

class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_items.id'), nullable=True)
    # Note: the system stores generic responses/comments for questions/topics
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback user={self.user_id}>'


# =========================
# Generic Forms System
# =========================

class Form(db.Model):
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(64), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_published = db.Column(db.Boolean, default=False)
    opens_at = db.Column(db.DateTime, nullable=True)
    closes_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tag = db.Column(db.String(255), nullable=True)

    creator = db.relationship('User', backref=db.backref('created_forms', lazy=True))
    questions = db.relationship('FormQuestion', backref='form', lazy=True, cascade='all, delete-orphan', order_by='FormQuestion.position')
    responses = db.relationship('FormResponse', backref='form', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Form {self.title}>'


class FormQuestion(db.Model):
    __tablename__ = 'form_questions'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    label = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(32), nullable=False)  # text, dropdown, multiple_choice, checkbox
    required = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    options = db.relationship('FormOption', backref='question', lazy=True, cascade='all, delete-orphan', order_by='FormOption.position')
    answers = db.relationship('FormAnswer', backref='question', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FormQuestion {self.question_type}>'


class FormOption(db.Model):
    __tablename__ = 'form_options'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('form_questions.id'), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<FormOption {self.value}>'


class FormResponse(db.Model):
    __tablename__ = 'form_responses'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    respondent_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    respondent_name = db.Column(db.String(120), nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    respondent_user = db.relationship('User', backref=db.backref('submitted_form_responses', lazy=True), foreign_keys=[respondent_user_id])
    answers = db.relationship('FormAnswer', backref='response', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<FormResponse form={self.form_id}>'


class FormAnswer(db.Model):
    __tablename__ = 'form_answers'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('form_responses.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('form_questions.id'), nullable=False)
    value_text = db.Column(db.Text, nullable=True)
    value_choice = db.Column(db.String(255), nullable=True)
    value_choices_json = db.Column(db.Text, nullable=True)  # for checkbox multi-select

    def __repr__(self):
        return f'<FormAnswer question={self.question_id}>'
