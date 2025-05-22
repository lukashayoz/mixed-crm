import pytest

def test_index(client):
    response = client.get('/contact/')
    assert b'Contacts' in response.data
    assert b'John Doe' in response.data