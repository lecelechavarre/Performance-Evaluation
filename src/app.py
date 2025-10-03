from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import os, datetime
from file_store import load_json, save_json
from utils import next_id
from auth import verify_password, get_user_by_username
from exports import export_evaluations_to_excel

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'data'))
USERS_PATH = os.path.join(DATA_DIR, 'users.json')
CRITERIA_PATH = os.path.join(DATA_DIR, 'criteria.json')
EVAL_PATH = os.path.join(DATA_DIR, 'evaluations.json')

def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

@app.route('/login', methods=['GET','POST'])
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user_by_username(username)
        if user and verify_password(password, user['password_hash']):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['full_name'] = user.get('full_name','')
            flash('Welcome back, ' + session['full_name'], 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    users = load_json(USERS_PATH)
    criteria = load_json(CRITERIA_PATH)
    evals = load_json(EVAL_PATH)
    stats = {'users': len(users), 'criteria': len(criteria), 'evaluations': len(evals)}
    user = {'id': session.get('user_id'), 'username': session.get('username'), 'full_name': session.get('full_name'), 'role': session.get('role')}
    return render_template('dashboard.html', user=user, stats=stats)

@app.route('/criteria', methods=['GET','POST'])
@login_required
def criteria_list():
    if request.method == 'POST':
        if session.get('role') != 'admin':
            flash('Only admin can add criteria', 'danger')
            return redirect(url_for('criteria_list'))
        criteria = load_json(CRITERIA_PATH)
        criteria.append({'id': next_id('c'), 'name': request.form.get('name'), 'weight': float(request.form.get('weight',1))})
        save_json(CRITERIA_PATH, criteria)
        flash('Criteria added', 'success')
        return redirect(url_for('criteria_list'))
    criteria = load_json(CRITERIA_PATH)
    return render_template('criteria.html', criteria=criteria)

@app.route('/evaluations', methods=['GET','POST'])
@login_required
def evaluations_list():
    if request.method == 'POST':
        data = load_json(EVAL_PATH)
        criteria = load_json(CRITERIA_PATH)
        scores = {}
        for c in criteria:
            key = f"score_{c['id']}"
            val = request.form.get(key)
            if val:
                try:
                    scores[c['id']] = int(val)
                except ValueError:
                    pass
        ev = {
            'id': next_id('ev'),
            'employee_id': request.form.get('employee_id'),
            'evaluator_id': session.get('user_id'),
            'date': request.form.get('date') or datetime.date.today().isoformat(),
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

@app.route('/export/evaluations')
@login_required
def export_evals():
    evaluations = load_json(EVAL_PATH)
    criteria = load_json(CRITERIA_PATH)
    criteria_map = {c['id']: c['name'] for c in criteria}
    out_path = os.path.abspath(os.path.join(DATA_DIR, 'evaluations_export.xlsx'))
    export_evaluations_to_excel(evaluations, criteria_map, out_path)
    return send_file(out_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
