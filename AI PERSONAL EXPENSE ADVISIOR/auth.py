# auth.py
import json
import os
import hashlib
import uuid

USERS_FILE = "users_db.json"

def _load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def _hash_password(password, salt=None):
    if salt is None:
        salt = uuid.uuid4().hex
    hash_obj = hashlib.sha256()
    hash_obj.update((salt + password).encode("utf-8"))
    return salt + "$" + hash_obj.hexdigest()

def _check_password(stored, plain):
    try:
        salt, h = stored.split("$", 1)
    except Exception:
        return False
    hash_obj = hashlib.sha256()
    hash_obj.update((salt + plain).encode("utf-8"))
    return hash_obj.hexdigest() == h

def signup(fullname: str, username: str, password: str, sq: str, sa: str) -> str:
    if not username or not password:
        return "Please provide username and password."
    users = _load_users()
    if username in users:
        return "Username already exists."

    users[username] = {
        "fullname": fullname or username,
        "password": _hash_password(password),
        "security_question": sq,
        "security_answer": sa.lower().strip()
    }
    _save_users(users)
    return f"User '{username}' created successfully. You can now login."



def login(username: str, password: str):
    users = _load_users()
    if username not in users:
        return None
    user = users[username]
    if _check_password(user.get("password",""), password):
        # return minimal user object
        return {"username": username, "fullname": user.get("fullname", username)}
    return None

def logout():
    # no-op here; main app should pop session key
    return True

def reset_password(username: str, answer: str, newpass: str) -> str:
    users = _load_users()
    if username not in users:
        return "User not found."

    if users[username]["security_answer"] != answer.lower().strip():
        return "Incorrect answer ❌"

    users[username]["password"] = _hash_password(newpass)
    _save_users(users)
    return "Password reset successfully ✔"


