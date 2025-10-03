import bcrypt
import os
from file_store import load_json
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
USERS_PATH = os.path.join(DATA_DIR, 'users.json')

def verify_password(plain, hashed):
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def get_user_by_username(username):
    users = load_json(USERS_PATH)
    return next((u for u in users if u['username'] == username), None)
