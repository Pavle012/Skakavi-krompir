from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import time
from typing import Optional

app = FastAPI()
DB = "scores.db"

SECRET_KEY = "GhrMYxwtogB8"
MAX_SCORE = 999

class Score(BaseModel):
    player: str
    score: int
    secret: str  # simple anti-cheat

class UserRegistration(BaseModel):
    username: str

class FriendRequestPayload(BaseModel):
    requester: str
    target: str
    message: Optional[str] = None

class FriendActionPayload(BaseModel):
    user: str
    friend: str

class HostRegistration(BaseModel):
    owner: str
    host_name: str
    external_ip: str
    port: int
    description: Optional[str] = "Skakavi Krompir host"


def get_db_connection():
    return sqlite3.connect(DB, check_same_thread=False)


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player TEXT,
            score INTEGER
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            created_at INTEGER
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS friend_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            requester TEXT,
            target TEXT,
            message TEXT,
            status TEXT,
            created_at INTEGER,
            UNIQUE(requester, target)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_a TEXT,
            user_b TEXT,
            created_at INTEGER,
            UNIQUE(user_a, user_b)
        )
        """)
        conn.execute("""
        CREATE TABLE IF NOT EXISTS hosts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT UNIQUE,
            host_name TEXT,
            external_ip TEXT,
            port INTEGER,
            description TEXT,
            updated_at INTEGER
        )
        """)


def add_user(username: str):
    now = int(time.time())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO users (username, created_at) VALUES (?, ?)",
            (username, now)
        )


def friend_exists(user_a: str, user_b: str) -> bool:
    if user_a == user_b:
        return False
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT 1 FROM friendships WHERE (user_a = ? AND user_b = ?) OR (user_a = ? AND user_b = ?)",
            (user_a, user_b, user_b, user_a)
        ).fetchone()
    return row is not None


def create_friendship(user_a: str, user_b: str):
    if user_a == user_b:
        return
    if friend_exists(user_a, user_b):
        return
    now = int(time.time())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO friendships (user_a, user_b, created_at) VALUES (?, ?, ?)",
            (user_a, user_b, now)
        )
        conn.execute(
            "INSERT OR IGNORE INTO friendships (user_a, user_b, created_at) VALUES (?, ?, ?)",
            (user_b, user_a, now)
        )


def remove_friendship(user_a: str, user_b: str):
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM friendships WHERE (user_a = ? AND user_b = ?) OR (user_a = ? AND user_b = ?)",
            (user_a, user_b, user_b, user_a)
        )


@app.on_event("startup")
def startup_event():
    init_db()


@app.post("/submit")
def submit(score: Score):
    if score.secret != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid secret")

    if score.score < 0 or score.score > MAX_SCORE:
        raise HTTPException(status_code=400, detail="Invalid score")

    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO scores (player, score) VALUES (?, ?)",
            (score.player, score.score)
        )

    return {"status": "ok"}


@app.get("/leaderboard")
def leaderboard(limit: int = 10):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT player, score FROM scores ORDER BY score DESC LIMIT ?",
            (limit,)
        ).fetchall()

    return [{"player": r[0], "score": r[1]} for r in rows]


@app.post("/users/register")
def register_user(user: UserRegistration):
    add_user(user.username)
    return {"status": "ok", "username": user.username}


@app.post("/friends/request")
def request_friend(request: FriendRequestPayload):
    add_user(request.requester)
    add_user(request.target)
    if request.requester == request.target:
        raise HTTPException(status_code=400, detail="Cannot friend yourself")
    if friend_exists(request.requester, request.target):
        raise HTTPException(status_code=400, detail="Already friends")

    now = int(time.time())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO friend_requests (requester, target, message, status, created_at) VALUES (?, ?, ?, ?, ?)",
            (request.requester, request.target, request.message or "", "pending", now)
        )

    return {"status": "pending"}


@app.post("/friends/accept")
def accept_friend(request: FriendRequestPayload):
    add_user(request.requester)
    add_user(request.target)
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT status FROM friend_requests WHERE requester = ? AND target = ?",
            (request.requester, request.target)
        ).fetchone()
        if not row or row[0] != "pending":
            raise HTTPException(status_code=404, detail="Friend request not found")
        conn.execute(
            "UPDATE friend_requests SET status = ? WHERE requester = ? AND target = ?",
            ("accepted", request.requester, request.target)
        )

    create_friendship(request.requester, request.target)
    return {"status": "accepted"}


@app.post("/friends/reject")
def reject_friend(request: FriendRequestPayload):
    # Mark friend request as rejected or remove it
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT status FROM friend_requests WHERE requester = ? AND target = ?",
            (request.requester, request.target)
        ).fetchone()
        if not row or row[0] != "pending":
            raise HTTPException(status_code=404, detail="Friend request not found")
        conn.execute(
            "UPDATE friend_requests SET status = ? WHERE requester = ? AND target = ?",
            ("rejected", request.requester, request.target)
        )
    return {"status": "rejected"}


@app.get("/friends/requests/{username}")
def list_pending_requests(username: str):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT requester, message, created_at FROM friend_requests WHERE target = ? AND status = 'pending' ORDER BY created_at DESC",
            (username,)
        ).fetchall()
    return [{"requester": r[0], "message": r[1], "created_at": r[2]} for r in rows]


@app.post("/friends/remove")
def remove_friend(request: FriendActionPayload):
    if request.user == request.friend:
        raise HTTPException(status_code=400, detail="Cannot remove yourself")
    remove_friendship(request.user, request.friend)
    return {"status": "removed"}


@app.get("/friends/{username}")
def list_friends(username: str):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT user_b FROM friendships WHERE user_a = ?",
            (username,)
        ).fetchall()
    return [{"friend": row[0]} for row in rows]


@app.post("/hosts/register")
def register_host(host: HostRegistration):
    add_user(host.owner)
    now = int(time.time())
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO hosts (owner, host_name, external_ip, port, description, updated_at) VALUES (?, ?, ?, ?, ?, ?) "
            "ON CONFLICT(owner) DO UPDATE SET host_name = excluded.host_name, external_ip = excluded.external_ip, port = excluded.port, description = excluded.description, updated_at = excluded.updated_at",
            (host.owner, host.host_name, host.external_ip, host.port, host.description, now)
        )

    return {"status": "ok", "owner": host.owner, "host_name": host.host_name}


class HostUnregisterPayload(BaseModel):
    owner: str


@app.post("/hosts/unregister")
def unregister_host(host: HostUnregisterPayload):
    with get_db_connection() as conn:
        conn.execute(
            "DELETE FROM hosts WHERE owner = ?",
            (host.owner,)
        )
    return {"status": "ok", "owner": host.owner}


@app.get("/hosts/list")
def list_hosts():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT owner, host_name, external_ip, port, description, updated_at FROM hosts ORDER BY updated_at DESC"
        ).fetchall()
    return [
        {
            "owner": row[0],
            "host_name": row[1],
            "external_ip": row[2],
            "port": row[3],
            "description": row[4],
            "updated_at": row[5],
        }
        for row in rows
    ]


@app.get("/hosts/friends/{username}")
def list_friend_hosts(username: str):
    with get_db_connection() as conn:
        friend_rows = conn.execute(
            "SELECT user_b FROM friendships WHERE user_a = ?",
            (username,)
        ).fetchall()
        friends = [row[0] for row in friend_rows]
        if not friends:
            return []
        placeholders = ",".join(["?"] * len(friends))
        rows = conn.execute(
            f"SELECT owner, host_name, external_ip, port, description, updated_at FROM hosts WHERE owner IN ({placeholders}) ORDER BY updated_at DESC",
            friends
        ).fetchall()
    return [
        {
            "owner": row[0],
            "host_name": row[1],
            "external_ip": row[2],
            "port": row[3],
            "description": row[4],
            "updated_at": row[5],
        }
        for row in rows
    ]
