from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os
from auth import verify_password, hash_password
from file_store import load_json, save_json
from utils import next_id
import datetime
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
USERS_PATH = os.path.abspath(os.path.join(DATA_DIR, 'users.json'))
CRITERIA_PATH = os.path.abspath(os.path.join(DATA_DIR, 'criteria.json'))
EVAL_PATH = os.path.abspath(os.path.join(DATA_DIR, 'evaluations.json'))

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret')


def login_required(fn):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


def role_required(role):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            users = load_json(USERS_PATH)
            user = next((u for u in users if u['id'] == session.get('user_id')), None)
            if not user or user.get('role') != role:
                flash('Unauthorized', 'danger')
                return redirect(url_for('dashboard'))
            return fn(*args, **kwargs)
        wrapper.__name__ = fn.__name__
        return wrapper
    return decorator


@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_json(USERS_PATH)
        user = next((u for u in users if u['username'] == username), None)
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash('Logged in', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    users = load_json(USERS_PATH)
    criteria = load_json(CRITERIA_PATH)
    evaluations = load_json(EVAL_PATH)
    # Simple summary
    return render_template('dashboard.html', users=users, criteria=criteria, evaluations=evaluations)


# Users management (Admin)
@app.route('/users')
@login_required
def users_list():
    users = load_json(USERS_PATH)
    return render_template('users.html', users=users)


@app.route('/users/create', methods=['POST'])
@login_required
def users_create():
    # only admin
    if session.get('role') != 'admin':
        flash('Unauthorized', 'danger')
        return redirect(url_for('users_list'))
    users = load_json(USERS_PATH)
    username = request.form['username']
    full_name = request.form.get('full_name','')
    role = request.form.get('role','employee')
    pw = request.form.get('password','password')
    new = {
        'id': next_id('u'),
        'username': username,
        'password_hash': hash_password(pw),
        'role': role,
        'full_name': full_name,
        'email': request.form.get('email','')
    }
    users.append(new)
    save_json(USERS_PATH, users)
    flash('User created', 'success')
    return redirect(url_for('users_list'))


# Criteria CRUD (Admin)
@app.route('/criteria', methods=['GET','POST'])
@login_required
def criteria_list():
    if request.method == 'POST':
        if session.get('role') != 'admin':
            flash('Unauthorized', 'danger')
            return redirect(url_for('criteria_list'))
        criteria = load_json(CRITERIA_PATH)
        criteria.append({'id': next_id('c'), 'name': request.form['name'], 'weight': float(request.form.get('weight',1.0))})
        save_json(CRITERIA_PATH, criteria)
        flash('Criteria added', 'success')
        return redirect(url_for('criteria_list'))
    criteria = load_json(CRITERIA_PATH)
    return render_template('criteria.html', criteria=criteria)


# Evaluations CRUD (Evaluator/Admin)
@app.route('/evaluations', methods=['GET','POST'])
@login_required
def evaluations_list():
    if request.method == 'POST':
        # create evaluation
        data = load_json(EVAL_PATH)
        scores = {}
        criteria = load_json(CRITERIA_PATH)
        for c in criteria:
            key = f"score_{c['id']}"
            if key in request.form and request.form[key].strip() != '':
                scores[c['id']] = int(request.form[key])
        ev = {
            'id': next_id('ev'),
            'employee_id': request.form['employee_id'],
            'evaluator_id': session.get('user_id'),
            'date': request.form.get('date', datetime.date.today().isoformat()),
            'scores': scores,
            'comments': request.form.get('comments',''),
            'status': 'final'
        }
        data.append(ev)
        save_json(EVAL_PATH, data)
        flash('Evaluation saved', 'success')
        return redirect(url_for('evaluations_list'))

    evaluations = load_json(EVAL_PATH)
    users = load_json(USERS_PATH)
    criteria = load_json(CRITERIA_PATH)
    return render_template('evaluations.html', evaluations=evaluations, users=users, criteria=criteria)


# Export evaluations to Excel
@app.route('/export/evaluations')
@login_required
def export_evals():
    evaluations = load_json(EVAL_PATH)
    criteria = load_json(CRITERIA_PATH)
    rows = []
    for ev in evaluations:
        row = {'eval_id': ev['id'], 'employee_id': ev['employee_id'], 'evaluator_id': ev['evaluator_id'], 'date': ev['date'], 'comments': ev.get('comments','')}
        for cid, score in ev.get('scores',{}).items():
            row[cid] = score
        rows.append(row)
    df = pd.DataFrame(rows)
    out_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'evaluations_export.xlsx')
    df.to_excel(out_path, index=False)
    return send_file(out_path, as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
