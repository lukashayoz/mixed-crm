import pytest
from flaskr.db import get_db

def test_delete(client, app):
    response = client.post('/contact/1/delete')
    assert response.headers["Location"] == "/contact/"

    with app.app_context():
        db = get_db()
        contact = db.execute('SELECT * FROM contact WHERE id = 1').fetchone()
        assert contact is None

def test_delete_exists_required(client):
    assert client.post('/contact/2/delete').status_code == 404