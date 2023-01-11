from modules import sqlwrap
from modules.idwrap import get_username
import hashlib
import json
import time

def post_message(message, user_id, room_id):
    hash_message_length = 50
    m = hashlib.sha256()
    m.update((message[:min(hash_message_length, len(message))] + str(user_id) + room_id + str(time.time())).encode('utf-8'))
    message_id = m.hexdigest()[:32]
    sqlwrap.execute("INSERT INTO messages VALUES (?, ?)", (message_id, message))
    sqlwrap.execute("INSERT INTO message_meta (message_id, room_id, sender_id) VALUES (?, ?, ?)", (message_id, room_id, user_id))
    send_time = sqlwrap.execute("SELECT strftime('%H:%M', timestamp) FROM message_meta WHERE message_id = ?", (message_id,))
    return json.dumps({"id": message_id, "message": message, "sender": get_username(user_id), "time": send_time})

def all_messages_since(message_id, room_id):
    if message_id == "0":
        messages = sqlwrap.execute("SELECT message_id, sender_id, strftime('%H:%M', timestamp) FROM message_meta WHERE room_id = ?", (room_id,))
    else:
        messages = sqlwrap.execute("SELECT message_id, sender_id, strftime('%H:%M', timestamp) FROM message_meta WHERE room_id = ? AND \
            (timestamp BETWEEN (SELECT timestamp FROM message_meta WHERE message_id = ?) AND strftime ('%Y-%m-%d %H:%M:%f', 'NOW')) AND \
            message_id != ?", (room_id, message_id, message_id))
    result = {}

    if not messages:
        return False

    for message in messages:
        message_id, sender, timestamp = message
        message_content = sqlwrap.execute("SELECT message FROM messages WHERE message_id = ?", (message_id,))
        timestamp += " UTC"
        result[message_id] = {"message": message_content, "sender": get_username(sender), "time": timestamp}
    return json.dumps(result)
