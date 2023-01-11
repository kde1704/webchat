from modules import sqlwrap

def get_username(user_id):
    s = sqlwrap.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
    if s:
        return s[0][0]
    return None

def get_user_id(username):
    s = sqlwrap.execute("SELECT user_id FROM users WHERE username = ?", (username,))
    if s:
        return s[0][0]
    return None

def get_roomname(room_id):
    s = sqlwrap.execute("SELECT room_name FROM rooms WHERE room_id = ?", (room_id,))
    if s:
        return s[0][0]
    return None

def get_room_id(roomname):
    s = sqlwrap.execute("SELECT room_id FROM rooms WHERE room_name = ?", (roomname,))
    if s:
        return s[0][0]
    return None
