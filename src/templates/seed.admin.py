import bcrypt, json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
users_path = os.path.join(BASE_DIR, "data", "users.json")

admin_user = {
    "id": "u-admin",
    "username": "admin",
    "password_hash": bcrypt.hashpw("adminpass".encode("utf-8"), bcrypt.gensalt()).decode(),
    "role": "admin",
    "full_name": "Administrator",
    "email": "admin@example.com"
}

with open(users_path, "w", encoding="utf-8") as f:
    json.dump([admin_user], f, indent=2)

print("Seeded admin user -> username: admin, password: adminpass")
