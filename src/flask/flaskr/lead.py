from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('lead', __name__, url_prefix='/lead')

@bp.route('/')
def index():
    db = get_db()
    leads = db.execute(
        'SELECT id, title, start_date, end_date, amount, probability'
        ' FROM lead'
        ' ORDER BY id DESC'
    ).fetchall()
    return render_template('lead/index.html', leads=leads)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        amount_str = request.form.get('amount')
        probability_str = request.form.get('probability')

        error = None

        if not title:
            error = 'Title is required.'

        start_date = start_date_str if start_date_str else None
        end_date = end_date_str if end_date_str else None
        
        amount = None
        if amount_str:
            try:
                amount = float(amount_str)
            except ValueError:
                error = 'Invalid amount.'
                # If there's already an error, append to it or handle appropriately
                if error and error != 'Invalid amount.':
                     error += ' Invalid amount.'
                else:
                    error = 'Invalid amount.'
        
        probability = None
        if probability_str:
            try:
                probability = float(probability_str)
            except ValueError:
                 # If there's already an error, append to it or handle appropriately
                if error and error != 'Invalid probability.':
                     error += ' Invalid probability.'
                else:
                    error = 'Invalid probability.'


        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO lead (title, start_date, end_date, amount, probability)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, start_date, end_date, amount, probability)
            )
            db.commit()
            return redirect(url_for('lead.index'))

    return render_template('lead/create.html')

def get_lead(id):
    lead = get_db().execute(
        'SELECT id, title, start_date, end_date, amount, probability'
        ' FROM lead'
        ' WHERE id = ?',
        (id,)
    ).fetchone()

    if lead is None:
        abort(404, f"Lead id {id} doesn't exist.")

    return lead

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    lead = get_lead(id)

    if request.method == 'POST':
        title = request.form['title']
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        amount_str = request.form.get('amount')
        probability_str = request.form.get('probability')
        error = None

        if not title:
            error = 'Title is required.'

        start_date = start_date_str if start_date_str else None
        end_date = end_date_str if end_date_str else None

        amount = None
        if amount_str:
            try:
                amount = float(amount_str)
            except ValueError:
                if error:
                    error += ' Invalid amount.'
                else:
                    error = 'Invalid amount.'
        
        probability = None
        if probability_str:
            try:
                probability = float(probability_str)
            except ValueError:
                if error:
                    error += ' Invalid probability.'
                else:
                    error = 'Invalid probability.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE lead SET title = ?, start_date = ?, end_date = ?, amount = ?, probability = ?'
                ' WHERE id = ?',
                (title, start_date, end_date, amount, probability, id)
            )
            db.commit()
            return redirect(url_for('lead.index'))

    return render_template('lead/update.html', lead=lead)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_lead(id) # Check if lead exists
    db = get_db()
    db.execute('DELETE FROM lead WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('lead.index'))
