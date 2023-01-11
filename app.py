from flask import Flask, jsonify, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from datetime import date

from modules.auth import *
from modules.idwrap import *
from modules.rooms import *
from modules.sanity import *
from modules.message import *
from modules import sqlwrap

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

sqlwrap.init("chat.db")

@app.route("/")
@login_required
def index():
    rooms = get_rooms(session["user_id"])
    return render_template("index.html", rooms=rooms)

@app.route("/login", methods=["GET", "POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    if request.method == "POST":
        if sanity_check(username) and sanity_check(password):
            auth = auth_user(username, password)
            if auth:
                session.clear()
                session["user_id"] = auth
                return redirect("/")
            # Invalid username and/or password
            return render_template("login.html", invalid=True)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if sanity_check(username) and sanity_check(password):
            session.clear()
            if register_user(username, password):
                return redirect("/login")
            return render_template("login.html", register=True, error=True)
    else:
        return render_template("login.html", register=True)

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        roomname = request.form.get("roomname")
        if sanity_check(roomname):
            room_id = register_room(roomname)
            if room_id:
                join_room(session["user_id"], room_id)
                return redirect(f"/rooms/{room_id}")
            return render_template("new_room.html", roomname_already_exists=True)
        return render_template("new_room.html", error=True)
    else:
        return render_template("new_room.html")

@app.route('/join', methods=["GET", "POST"])
@app.route("/join/<invite>")
@login_required
def join(invite=None):
    if invite:
        room_id = lookup_invite(invite)
        if not room_id:
            return redirect("/")

        if not in_room(session["user_id"], room_id):
            join_room(session["user_id"], room_id)
        return redirect(f"/rooms/{room_id}")
    else:
        if request.method == "POST":
            room_id = lookup_invite(request.form.get("invite"))
            if not room_id:
                return render_template("join.html", error=True)

            if not in_room(session["user_id"], room_id):
                join_room(session["user_id"], room_id)
            return redirect(f"/rooms/{room_id}")
        else:
            return render_template("join.html")

@app.route("/leave/<room_id>")
@login_required
def leave(room_id):
    leave_room(session["user_id"], room_id)
    return redirect("/")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    if request.method == "POST":
        password = request.form.get("password")
        if sanity_check(password):
            auth = auth_user(get_username(session["user_id"]), password)
            if auth:
                delete_user(session["user_id"])
                session.clear()
                return redirect("/login")
            # Invalid username and/or password
            return render_template("delete.html", invalid=True)
    else:
        return render_template("delete.html")


@app.route("/rooms/<room_id>", methods=["GET", "POST"])
@login_required
def rooms(room_id):
    if in_room(session["user_id"], room_id):
        if request.method == "POST":
            return post_message(request.form.get("message"), session["user_id"], room_id)
        else:
            if request.args.get("last_message"):
                since = all_messages_since(request.args.get("last_message"), room_id)
                if since:
                    return since
                else:
                    return '', 204
            return render_template("room.html", roomname = get_roomname(room_id), invite = get_invite(room_id))
    return render_template("not_in_room.html")

@app.route('/msg.js')
def msg():
    return send_from_directory('.', 'msg.js')

@app.route('/static/<file>')
def styles(file):
    return send_from_directory('static', file)