from modules import sqlwrap
import hashlib
import random
import string

def register_room(roomname):
    if sqlwrap.execute("SELECT room_name FROM rooms WHERE room_name = ?", (roomname,)):
        return False
    m = hashlib.sha256()
    m.update(roomname.encode('utf-8'))
    room_id = m.hexdigest()[:32]

    sqlwrap.execute("INSERT INTO rooms VALUES (?, ?)", (room_id, roomname))
    return room_id

def get_rooms(user_id):
    room_ids = sqlwrap.execute("SELECT room_id FROM members WHERE user_id = ?", (user_id,))
    if not room_ids:
        return None
    room_ids = [i[0] for i in room_ids]
    invite = list(filter(None, [sqlwrap.execute("SELECT invite FROM invites WHERE room_id = ?", (room_id,)) for room_id in room_ids]))
    room_name = list(filter(None, [sqlwrap.execute("SELECT room_name FROM rooms WHERE room_id = ?", (room_id,)) for room_id in room_ids]))
    return [(room_ids[i], room_name[i][0][0], invite[i][0][0]) for i in range(len(room_name))]


def join_room(user_id, room_id):
    sqlwrap.execute("INSERT INTO members VALUES (?, ?)", (user_id, room_id))

def leave_room(user_id, room_id):
    sqlwrap.execute("DELETE FROM members WHERE user_id = ? and room_id = ?", (user_id, room_id))
    if not sqlwrap.execute("SELECT * FROM members WHERE room_id = ?", (room_id,)):
        sqlwrap.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))

def in_room(user_id, room_id):
    members_not_admin = sqlwrap.execute("SELECT room_id FROM members WHERE room_id = ? AND user_id = ?", (room_id, user_id))
    return members_not_admin != None

def get_invite(room_id):
    invite = sqlwrap.execute("SELECT invite FROM invites WHERE room_id = ?", (room_id,))
    while invite == None:
        new_invite = ""
        for i in range(8): # invite string length
            new_invite += random.choice(string.ascii_letters)
        if not lookup_invite(new_invite):
            sqlwrap.execute("INSERT INTO invites VALUES (?, ?)", (room_id, new_invite))
            return new_invite
    return invite[0][0]

def lookup_invite(invite):
    r = sqlwrap.execute("SELECT room_id FROM invites WHERE invite = ?", (invite,))
    if r:
        return r[0][0]
