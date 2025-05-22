import pytest
from flaskr.db import get_db

def test_create(client, app):
    assert client.get('/contact/create').status_code == 200
    client.post('/contact/create', data={
        'name': 'Created Contact',
        'email': 'created@example.com',
        'phone': '987-654-3210',
        'rating': '4'
    })

    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM contact').fetchone()[0]
        assert count == 2

def test_create_validate(client):
    response = client.post('/contact/create', data={'name': '', 'email': '', 'phone': '', 'rating': ''})
    assert b'Name is required.' in response.data