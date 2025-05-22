from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('contact', __name__, url_prefix='/contact')

@bp.route('/')
def index():
    db = get_db()
    contacts = db.execute(
        'SELECT id, name, email, phone, rating, created'
        ' FROM contact'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('contact/index.html', contacts=contacts)

@bp.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        rating = request.form['rating']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO contact (name, email, phone, rating)'
                ' VALUES (?, ?, ?, ?)',
                (name, email, phone, rating)
            )
            db.commit()
            return redirect(url_for('contact.index'))

    return render_template('contact/create.html')

def get_contact(id):
    contact = get_db().execute(
        'SELECT id, name, email, phone, rating, created'
        ' FROM contact'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if contact is None:
        abort(404, f"Contact id {id} doesn't exist.")

    return contact

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):
    contact = get_contact(id)

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        rating = request.form['rating']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE contact SET name = ?, email = ?, phone = ?, rating = ?'
                ' WHERE id = ?',
                (name, email, phone, rating, id)
            )
            db.commit()
            return redirect(url_for('contact.index'))

    return render_template('contact/update.html', contact=contact)

@bp.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    get_contact(id)
    db = get_db()
    db.execute('DELETE FROM contact WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('contact.index'))