import json

from models import User, MenuItem, Question, Feedback
from app import db


def create_user(username='tester', email='tester@example.com', password='pass'):
    u = User(username=username, email=email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    return u


def test_submit_feedback_and_summaries(client, app):
    with app.app_context():
        # create a menu item and question
        item = MenuItem(item_name='Topic A', description='A topic')
        db.session.add(item)
        db.session.commit()

        q = Question(question_text='What do you think?', menu_item_id=item.id)
        db.session.add(q)
        db.session.commit()

        user = create_user()

        # attach session user_id
        with client.session_transaction() as sess:
            sess['user_id'] = user.id

        # submit feedback
        payload = {'question_id': q.id, 'menu_item_id': item.id, 'comment': 'This is a test response.'}
        resp = client.post('/feedback/api/submit_feedback', data=json.dumps(payload), content_type='application/json')
        assert resp.status_code == 201
        data = resp.get_json()
        assert data['status'] == 'success'

        # summary should show 1 response
        resp2 = client.get('/feedback/api/menu_summaries')
        assert resp2.status_code == 200
        sdata = resp2.get_json()
        assert sdata['status'] == 'success'
        assert any(item['response_count'] == 1 for item in sdata['items'])

        # reviews endpoint for item
        resp3 = client.get(f'/feedback/api/menu/{item.id}/reviews')
        assert resp3.status_code == 200
        rdata = resp3.get_json()
        assert rdata['status'] == 'success'
        assert len(rdata['reviews']) >= 1
        assert rdata['reviews'][0]['comment'] == 'This is a test response.'
