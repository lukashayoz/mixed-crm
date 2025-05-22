import pytest
from flaskr.db import get_db


def test_index(client, auth):
    response = client.get('/contact/')
    assert b'Contacts' in response.data
    assert b'John Doe' in response.data


@pytest.mark.parametrize('path', (
    '/contact/create',
    '/contact/1/update',
    '/contact/1/delete',
))
def test_login_required(client, path):
    response = client.post(path)
    assert response.headers["Location"] == "/auth/login"


def test_create(client, auth, app):
    auth.login()
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


def test_update(client, auth, app):
    auth.login()
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


@pytest.mark.parametrize('path', (
    '/contact/create',
    '/contact/1/update',
))
def test_create_update_validate(client, auth, path):
    auth.login()
    response = client.post(path, data={'name': '', 'email': '', 'phone': '', 'rating': ''})
    assert b'Name is required.' in response.data


@pytest.mark.parametrize('path', (
    '/contact/2/update',
    '/contact/2/delete',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.post(path).status_code == 404


def test_delete(client, auth, app):
    auth.login()
    response = client.post('/contact/1/delete')
    assert response.headers["Location"] == "/contact/"

    with app.app_context():
        db = get_db()
        contact = db.execute('SELECT * FROM contact WHERE id = 1').fetchone()
        assert contact is None