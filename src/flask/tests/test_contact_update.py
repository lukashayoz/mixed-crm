import pytest
from flaskr.db import get_db

def test_update(client, app):
    assert client.get('/contact/1/update').status_code == 200
    client.post('/contact/1/update', data={
        'name': 'Updated Contact',
        'email': 'updated@example.com',
        'phone': '555-123-4567',
        'rating': '3'
    })

    with app.app_context():
        db = get_db()
        contact = db.execute('SELECT * FROM contact WHERE id = 1').fetchone()
        assert contact['name'] == 'Updated Contact'
        assert contact['email'] == 'updated@example.com'
        assert contact['phone'] == '555-123-4567'
        assert contact['rating'] == 3

def test_update_validate(client):
    response = client.post('/contact/1/update', data={'name': '', 'email': '', 'phone': '', 'rating': ''})
    assert b'Name is required.' in response.data

def test_update_exists_required(client):
    assert client.post('/contact/2/update').status_code == 404