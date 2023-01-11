from modules import sqlwrap
import hashlib

from flask import redirect, session

from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

from modules.rooms import *

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def auth_user(username, password):
    logins = sqlwrap.execute("SELECT user_id, hash FROM users WHERE username = ?", (username,))
    if logins and check_password_hash(logins[0][1], password):
        return logins[0][0] # return user_id
    return False

def register_user(username, password):
    password_hash = generate_password_hash(password)
    if sqlwrap.execute("SELECT user_id FROM users WHERE username = ?", (username,)):
        return False
    sqlwrap.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, password_hash))
    return True

def delete_user(user_id):
    rooms = get_rooms(user_id)
    if rooms:
        for room in rooms:
            leave_room(user_id, room[0])
    sqlwrap.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
