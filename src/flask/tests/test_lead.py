import pytest
from flaskr.db import get_db

def test_index(client, auth):
    response = client.get('/lead/')
    assert response.status_code == 302 # Redirect to login
    assert 'http://localhost/auth/login' in response.headers['Location']

    auth.login()
    response = client.get('/lead/')
    assert response.status_code == 200
    assert b'Leads' in response.data
    assert b'Add Lead' in response.data
    # Check for a lead added by a fixture or previous test if applicable
    # For now, just check that the page loads and has expected static text

    # Add a lead to check if it's displayed
    with client.application.app_context():
        db = get_db()
        db.execute(
            "INSERT INTO lead (title, start_date, end_date, amount, probability) VALUES (?, ?, ?, ?, ?)",
            ('Test Lead for Index', '2024-01-01', '2024-01-31', 1000.0, 0.5),
        )
        db.commit()

    response = client.get('/lead/')
    assert b'Test Lead for Index' in response.data
    assert b'2024-01-01' in response.data # Date formatting might make this tricky, adjust if needed
    assert b'1000.0' in response.data 
    assert b'0.5' in response.data


@pytest.mark.parametrize(('path', 'expected_title'), (
    ('/lead/create', b'New Lead'),
    ('/lead/1/update', b'Edit Lead'), # Assumes lead with id 1 exists
))
def test_create_update_get_requires_login(client, path, expected_title):
    response = client.get(path)
    assert response.status_code == 302
    assert 'http://localhost/auth/login' in response.headers['Location']

# Need to ensure a lead with ID 1 exists for the update test case.
# This can be done by creating a lead before this parameterized test runs,
# or by ensuring 'test_update' specific tests handle creation.
# For simplicity, we'll handle lead creation within test_update and test_delete.

def test_create_get(client, auth):
    auth.login()
    response = client.get('/lead/create')
    assert response.status_code == 200
    assert b'New Lead' in response.data

def test_create_post(client, auth, app):
    auth.login()
    response = client.post('/lead/create', data={
        'title': 'New Test Lead',
        'start_date': '2024-02-01',
        'end_date': '2024-02-28',
        'amount': '1500.50',
        'probability': '0.75'
    }, follow_redirects=True)
    assert response.status_code == 200 # Should redirect to index
    assert b'Leads' in response.data # Check if we are on index page
    assert b'New Test Lead' in response.data # Check if new lead is listed

    with app.app_context():
        db = get_db()
        lead = db.execute("SELECT * FROM lead WHERE title = 'New Test Lead'").fetchone()
        assert lead is not None
        assert lead['start_date'] == '2024-02-01' # Stored as TEXT
        assert lead['amount'] == 1500.50
        assert lead['probability'] == 0.75

def test_create_post_title_required(client, auth, app):
    auth.login()
    response = client.post('/lead/create', data={
        'title': '', # Empty title
        'start_date': '2024-03-01',
        'amount': '200'
    })
    assert response.status_code == 200 # No redirect, show form with error
    assert b'Title is required.' in response.data

    with app.app_context():
        db = get_db()
        # Ensure no lead was created with an empty title by this post
        lead = db.execute("SELECT * FROM lead WHERE start_date = '2024-03-01'").fetchone()
        assert lead is None

def _create_test_lead(app, title="Update Me"):
    with app.app_context():
        db = get_db()
        cursor = db.execute(
            "INSERT INTO lead (title, start_date, end_date, amount, probability) VALUES (?, ?, ?, ?, ?)",
            (title, '2024-01-10', '2024-01-20', 500.0, 0.25),
        )
        db.commit()
        return cursor.lastrowid # Return the id of the created lead

def test_update_get(client, auth, app):
    lead_id = _create_test_lead(app)
    
    # Test get update page when not logged in
    response = client.get(f'/lead/{lead_id}/update')
    assert response.status_code == 302
    assert 'http://localhost/auth/login' in response.headers['Location']

    auth.login()
    response = client.get(f'/lead/{lead_id}/update')
    assert response.status_code == 200
    assert b'Edit Lead' in response.data
    assert b'Update Me' in response.data # Original title

def test_update_post(client, auth, app):
    lead_id = _create_test_lead(app, title="Original Title for Update")
    auth.login()
    
    response = client.post(f'/lead/{lead_id}/update', data={
        'title': 'Updated Test Lead',
        'start_date': '2024-03-01',
        'end_date': '2024-03-31',
        'amount': '2500.75',
        'probability': '0.90'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Leads' in response.data # Redirected to index
    assert b'Updated Test Lead' in response.data

    with app.app_context():
        db = get_db()
        lead = db.execute("SELECT * FROM lead WHERE id = ?", (lead_id,)).fetchone()
        assert lead is not None
        assert lead['title'] == 'Updated Test Lead'
        assert lead['start_date'] == '2024-03-01'
        assert lead['amount'] == 2500.75
        assert lead['probability'] == 0.90

def test_update_post_title_required(client, auth, app):
    lead_id = _create_test_lead(app, title="Title Required Test")
    auth.login()

    response = client.post(f'/lead/{lead_id}/update', data={
        'title': '', # Empty title
        'start_date': '2024-04-01',
        'amount': '300'
    })
    assert response.status_code == 200 # No redirect
    assert b'Title is required.' in response.data

    with app.app_context():
        db = get_db()
        lead = db.execute("SELECT * FROM lead WHERE id = ?", (lead_id,)).fetchone()
        assert lead is not None
        assert lead['title'] == 'Title Required Test' # Title should not have changed

def test_update_non_existent(client, auth, app):
    auth.login()
    response = client.get('/lead/999/update')
    assert response.status_code == 404
    response = client.post('/lead/999/update', data={'title': 'ghost'})
    assert response.status_code == 404


def test_delete(client, auth, app):
    lead_id = _create_test_lead(app, title="To Be Deleted")
    
    # Test delete when not logged in
    response = client.post(f'/lead/{lead_id}/delete')
    assert response.status_code == 302 # Redirect to login
    assert 'http://localhost/auth/login' in response.headers['Location']

    auth.login()
    response = client.post(f'/lead/{lead_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Leads' in response.data # Redirected to index
    assert b'To Be Deleted' not in response.data # Lead should be gone

    with app.app_context():
        db = get_db()
        lead = db.execute("SELECT * FROM lead WHERE id = ?", (lead_id,)).fetchone()
        assert lead is None

def test_delete_non_existent(client, auth, app):
    auth.login()
    # Ensure lead 999 does not exist (or any other high number)
    with app.app_context():
        db = get_db()
        db.execute("DELETE FROM lead WHERE id = 999")
        db.commit()
        
    response = client.post('/lead/999/delete')
    assert response.status_code == 404

# Parameterized test for paths that require a lead to exist and user to be logged in for GET
@pytest.mark.parametrize('path_template', (
    '/lead/{id}/update',
))
def test_get_lead_specific_paths_auth_and_existence(client, auth, app, path_template):
    # Test access when not logged in
    response = client.get(path_template.format(id=1)) # Use arbitrary ID
    assert response.status_code == 302
    assert 'http://localhost/auth/login' in response.headers['Location']

    auth.login()
    # Test access to non-existent lead
    response = client.get(path_template.format(id=999)) # Use non-existent ID
    assert response.status_code == 404

    # Test access to existing lead
    lead_id = _create_test_lead(app, "Access Test Lead")
    response = client.get(path_template.format(id=lead_id))
    assert response.status_code == 200
    if "update" in path_template:
        assert b"Edit Lead" in response.data
        assert b"Access Test Lead" in response.data

# Parameterized test for POST actions on specific leads that require login and lead existence
@pytest.mark.parametrize('path_template', (
    '/lead/{id}/delete',
))
def test_post_lead_specific_paths_auth_and_existence(client, auth, app, path_template):
    # Test action when not logged in
    response = client.post(path_template.format(id=1)) # Use arbitrary ID
    assert response.status_code == 302
    assert 'http://localhost/auth/login' in response.headers['Location']

    auth.login()
    # Test action on non-existent lead
    response = client.post(path_template.format(id=999)) # Use non-existent ID
    assert response.status_code == 404

    # Test action on existing lead (delete will be tested more thoroughly in test_delete)
    # This is more of a general check for the decorator/get_lead logic
    if "delete" in path_template: # This is the only one for now
        lead_id = _create_test_lead(app, "Delete Action Test Lead")
        response = client.post(path_template.format(id=lead_id), follow_redirects=True)
        assert response.status_code == 200
        assert b'Leads' in response.data # Should redirect to index
        with app.app_context():
            db = get_db()
            lead = db.execute("SELECT * FROM lead WHERE id = ?", (lead_id,)).fetchone()
            assert lead is None
    # Add other POST actions like 'publish', 'archive' if they were part of lead module
    # For now, only delete fits this pattern of POSTing to /lead/<id>/action

@pytest.mark.parametrize(('amount_in', 'probability_in', 'expected_amount', 'expected_probability', 'error_expected'), (
    ('100.50', '0.5', 100.50, 0.5, None),
    ('', '', None, None, None), # Optional fields
    ('abc', '0.5', None, 0.5, b'Invalid amount.'),
    ('100', 'xyz', 100.0, None, b'Invalid probability.'),
    ('abc', 'xyz', None, None, b'Invalid amount. Invalid probability.'), # Check multiple errors
))
def test_create_optional_fields_validation(client, auth, app, amount_in, probability_in, expected_amount, expected_probability, error_expected):
    auth.login()
    response = client.post('/lead/create', data={
        'title': 'Validation Test',
        'start_date': '2024-05-01',
        'end_date': '2024-05-31',
        'amount': amount_in,
        'probability': probability_in
    }, follow_redirects=True)

    if error_expected:
        assert response.status_code == 200 # Should stay on create page
        assert error_expected in response.data
        with app.app_context():
            db = get_db()
            lead = db.execute("SELECT * FROM lead WHERE title = 'Validation Test'").fetchone()
            assert lead is None # Should not be created
    else:
        assert response.status_code == 200 # Successful creation redirects to index
        assert b'Leads' in response.data
        assert b'Validation Test' in response.data
        with app.app_context():
            db = get_db()
            lead = db.execute("SELECT * FROM lead WHERE title = 'Validation Test'").fetchone()
            assert lead is not None
            assert lead['amount'] == expected_amount
            assert lead['probability'] == expected_probability

def test_update_optional_fields_validation(client, auth, app):
    lead_id = _create_test_lead(app, title="Update Validation Test")
    auth.login()

    # First, check successful update with empty optional fields
    response = client.post(f'/lead/{lead_id}/update', data={
        'title': 'Updated Validation Test',
        'start_date': '',
        'end_date': '',
        'amount': '',
        'probability': ''
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Leads' in response.data
    assert b'Updated Validation Test' in response.data

    with app.app_context():
        db = get_db()
        lead = db.execute("SELECT * FROM lead WHERE id = ?", (lead_id,)).fetchone()
        assert lead is not None
        assert lead['title'] == 'Updated Validation Test'
        assert lead['start_date'] is None
        assert lead['end_date'] is None
        assert lead['amount'] is None
        assert lead['probability'] is None

    # Test invalid amount during update
    response = client.post(f'/lead/{lead_id}/update', data={
        'title': 'Updated Validation Test',
        'amount': 'invalid_amount',
        'probability': '0.5'
    })
    assert response.status_code == 200 # Stays on update page
    assert b'Invalid amount.' in response.data
    
    # Test invalid probability during update
    response = client.post(f'/lead/{lead_id}/update', data={
        'title': 'Updated Validation Test',
        'amount': '100.0',
        'probability': 'invalid_prob'
    })
    assert response.status_code == 200 # Stays on update page
    assert b'Invalid probability.' in response.data

    # Ensure original data (or last valid update) is still there
    with app.app_context():
        db = get_db()
        lead = db.execute("SELECT * FROM lead WHERE id = ?", (lead_id,)).fetchone()
        assert lead is not None
        assert lead['title'] == 'Updated Validation Test' # Title from successful update
        assert lead['amount'] is None # From successful update with empty fields
        assert lead['probability'] is None # From successful update with empty fields
