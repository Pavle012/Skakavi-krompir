import asyncio
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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


class MultiplayerSessionRegistration(BaseModel):
    owner: str
    host_name: str
    description: Optional[str] = "Skakavi Krompir host"


class MultiplayerSession:
    def __init__(self, session_id: str, owner: str):
        self.session_id = session_id
        self.owner = owner
        self.admin_name = owner
        self.current_seed = int(time.time() * 1000)
        self.connections = {}
        self.players = {}
        self.running = True

    async def broadcast_loop(self):
        while self.running:
            await self.broadcast({"type": "state_update", "players": list(self.players.values())})
            await asyncio.sleep(1 / 30)

    async def broadcast(self, packet):
        disconnected = []
        for websocket in list(self.connections):
            try:
                await websocket.send_json(packet)
            except Exception:
                disconnected.append(websocket)
        for websocket in disconnected:
            self.remove_player(websocket)

    async def send(self, websocket, packet):
        await websocket.send_json(packet)

    def add_player(self, websocket):
        player_id = str(uuid.uuid4())
        self.connections[websocket] = player_id
        self.players[player_id] = {
            "id": player_id,
            "name": "Unknown",
            "x": 100,
            "y": -1000,
            "rot": 0,
            "alive": True,
            "ready": False,
            "score": 0,
            "is_admin": False,
        }
        return player_id

    def remove_player(self, websocket):
        player_id = self.connections.pop(websocket, None)
        if player_id is not None:
            self.players.pop(player_id, None)

    async def process_packet(self, websocket, packet):
        player_id = self.connections.get(websocket)
        player = self.players.get(player_id)
        if not player:
            return

        packet_type = packet.get("type")
        if packet_type == "join":
            player["name"] = packet.get("name", "Player")
            player["is_admin"] = player["name"] == self.admin_name
        elif packet_type == "update":
            for key in ("x", "y", "rot", "alive", "score"):
                if key in packet:
                    player[key] = packet[key]
        elif packet_type == "ready":
            player["ready"] = packet.get("ready", True)
            if self.players and all(item["ready"] for item in self.players.values()):
                await self.start_game()
        elif packet_type == "admin_start" and player["is_admin"]:
            await self.start_game()
        elif packet_type == "admin_kick" and player["is_admin"]:
            target_id = packet.get("target_id")
            for target_socket, target_player_id in list(self.connections.items()):
                if target_player_id == target_id:
                    await self.send(target_socket, {"type": "kicked"})
                    self.remove_player(target_socket)
                    await target_socket.close()
                    break

    async def start_game(self):
        self.current_seed = int(time.time() * 1000)
        for player in self.players.values():
            player["ready"] = False
            player["alive"] = True
            player["score"] = 0
        await self.broadcast({"type": "start_game", "seed": self.current_seed})


multiplayer_sessions = {}


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
            updated_at INTEGER,
            session_id TEXT
        )
        """)
        try:
            conn.execute("ALTER TABLE hosts ADD COLUMN session_id TEXT")
        except sqlite3.OperationalError:
            pass


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


@app.post("/multiplayer/sessions")
async def create_multiplayer_session(session: MultiplayerSessionRegistration):
    add_user(session.owner)
    session_id = str(uuid.uuid4())
    multiplayer_sessions[session_id] = MultiplayerSession(session_id, session.owner)
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO hosts (owner, host_name, external_ip, port, description, updated_at, session_id) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session.owner, session.host_name, "server", 443, session.description, int(time.time()), session_id),
        )
    asyncio.create_task(multiplayer_sessions[session_id].broadcast_loop())
    return {"session_id": session_id}


@app.websocket("/multiplayer/ws/{session_id}")
async def multiplayer_websocket(websocket: WebSocket, session_id: str):
    session = multiplayer_sessions.get(session_id)
    if not session or not session.running:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    session.add_player(websocket)
    player_id = session.connections[websocket]
    await session.send(websocket, {
        "type": "welcome",
        "id": player_id,
        "seed": session.current_seed,
    })
    try:
        while True:
            await session.process_packet(websocket, await websocket.receive_json())
    except WebSocketDisconnect:
        session.remove_player(websocket)
    except Exception:
        session.remove_player(websocket)


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
    session_id = None
    with get_db_connection() as conn:
        row = conn.execute("SELECT session_id FROM hosts WHERE owner = ?", (host.owner,)).fetchone()
        if row:
            session_id = row[0]
        conn.execute(
            "DELETE FROM hosts WHERE owner = ?",
            (host.owner,)
        )
    if session_id in multiplayer_sessions:
        multiplayer_sessions[session_id].running = False
        multiplayer_sessions.pop(session_id, None)
    return {"status": "ok", "owner": host.owner}


@app.get("/hosts/list")
def list_hosts():
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT owner, host_name, external_ip, port, description, updated_at, session_id FROM hosts ORDER BY updated_at DESC"
        ).fetchall()
    return [
        {
            "owner": row[0],
            "host_name": row[1],
            "external_ip": row[2],
            "port": row[3],
            "description": row[4],
            "updated_at": row[5],
            "session_id": row[6],
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
            f"SELECT owner, host_name, external_ip, port, description, updated_at, session_id FROM hosts WHERE owner IN ({placeholders}) ORDER BY updated_at DESC",
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
            "session_id": row[6],
        }
        for row in rows
    ]
