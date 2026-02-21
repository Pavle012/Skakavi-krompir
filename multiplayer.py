import socket
import threading
import json
import time
import uuid

DEFAULT_PORT = 15565

class GameServer:
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT, admin_name="Admin"):
        self.host = host
        self.port = port
        self.admin_name = admin_name
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}  # conn -> addr
        self.players = {}  # conn -> dict of player info
        self.running = False
        self.current_seed = int(time.time() * 1000)
    
    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.running = True
            print(f"[Server] Started on {self.host}:{self.port}")
            
            accept_thread = threading.Thread(target=self.accept_clients, daemon=True)
            accept_thread.start()
            
            broadcast_thread = threading.Thread(target=self.broadcast_loop, daemon=True)
            broadcast_thread.start()
            
        except Exception as e:
            print(f"[Server] Failed to start: {e}")
            self.running = False
            
    def stop(self):
        self.running = False
        try:
            self.server_socket.close()
        except:
            pass
        for conn in list(self.clients.keys()):
            try:
                conn.close()
            except:
                pass
        self.clients.clear()
        self.players.clear()
        print("[Server] Stopped.")

    def accept_clients(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                client_id = str(uuid.uuid4())
                self.clients[conn] = addr
                self.players[conn] = {
                    "id": client_id,
                    "name": "Unknown",
                    "x": 100,
                    "y": -1000,
                    "rot": 0,
                    "alive": True,
                    "ready": False,
                    "score": 0,
                    "is_admin": False
                }
                print(f"[Server] Client connected from {addr}")
                
                # Send the welcome packet with ID and current seed
                welcome_packet = {
                    "type": "welcome",
                    "id": client_id,
                    "seed": self.current_seed
                }
                self.send_to_client(conn, welcome_packet)
                
                threading.Thread(target=self.handle_client, args=(conn,), daemon=True).start()
            except Exception as e:
                if self.running:
                    print(f"[Server] Accept error: {e}")

    def handle_client(self, conn):
        buffer = ""
        while self.running:
            try:
                data = conn.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.process_packet(conn, json.loads(line))
            except Exception as e:
                break
                
        self.disconnect_client(conn)

    def process_packet(self, conn, packet):
        p_type = packet.get("type")
        player = self.players.get(conn)
        if not player:
            return
            
        if p_type == "join":
            name = packet.get("name", "Player")
            player["name"] = name
            if name == self.admin_name:
                 player["is_admin"] = True
            print(f"[Server] {name} joined the game.")
            
        elif p_type == "update":
            player["x"] = packet.get("x", player["x"])
            player["y"] = packet.get("y", player["y"])
            player["rot"] = packet.get("rot", player["rot"])
            player["alive"] = packet.get("alive", player["alive"])
            player["score"] = packet.get("score", player["score"])
            
        elif p_type == "ready":
            player["ready"] = packet.get("ready", True)
            self.check_all_ready()
            
        elif p_type == "admin_start":
            if player["is_admin"]:
                self.start_game()
                
        elif p_type == "admin_kick":
             if player["is_admin"]:
                 target_id = packet.get("target_id")
                 self.kick_player(target_id)

    def check_all_ready(self):
        # If all connected players are ready, start!
        all_ready = True
        has_players = False
        for p in self.players.values():
            has_players = True
            if not p["ready"]:
                all_ready = False
                break
        if has_players and all_ready:
            self.start_game()

    def start_game(self):
        self.current_seed = int(time.time() * 1000)
        start_packet = {"type": "start_game", "seed": self.current_seed}
        for conn in self.players:
            self.players[conn]["ready"] = False
            self.players[conn]["alive"] = True
            self.players[conn]["score"] = 0
            # Don't reset X and Y here, client will do it
        self.broadcast(start_packet)
        print("[Server] Game started! Seed sent to all.")

    def kick_player(self, target_id):
        target_conn = None
        for conn, p in self.players.items():
            if p["id"] == target_id:
                target_conn = conn
                break
        if target_conn:
            self.send_to_client(target_conn, {"type": "kicked"})
            print(f"[Server] Kicked {self.players[target_conn]['name']}")
            self.disconnect_client(target_conn)

    def disconnect_client(self, conn):
        if conn in self.players:
            print(f"[Server] {self.players[conn]['name']} disconnected.")
            del self.players[conn]
        if conn in self.clients:
            del self.clients[conn]
        try:
            conn.close()
        except:
            pass

    def broadcast_loop(self):
        # 30 ticks per second state broadcast
        while self.running:
            state_packet = {
                "type": "state_update",
                "players": list(self.players.values())
            }
            self.broadcast(state_packet)
            time.sleep(1/30)

    def broadcast(self, data):
        msg = json.dumps(data) + "\n"
        encoded = msg.encode('utf-8')
        invalid = []
        for conn in list(self.clients.keys()):
            try:
                conn.sendall(encoded)
            except:
                invalid.append(conn)
        for c in invalid:
            self.disconnect_client(c)

    def send_to_client(self, conn, data):
        try:
            msg = json.dumps(data) + "\n"
            conn.sendall(msg.encode('utf-8'))
        except:
            self.disconnect_client(conn)


class GameClient:
    def __init__(self, host, port, name):
        self.host = host
        self.port = port
        self.name = name
        self.socket = None
        self.running = False
        
        self.client_id = None
        self.current_seed = None
        
        self.remote_players = {} # id -> player_dict
        
        # Event flags for main thread to check
        self.should_start_game = False
        self.was_kicked = False
        self.connection_error = False

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None)
            self.running = True
            
            # Start listener thread
            threading.Thread(target=self.listen_loop, daemon=True).start()
            
            # Send join packet
            self.send({"type": "join", "name": self.name})
            return True
        except Exception as e:
            print(f"[Client] Connection failed: {e}")
            self.connection_error = True
            return False

    def listen_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.socket.recv(1024).decode('utf-8')
                if not data:
                    break
                buffer += data
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        self.process_packet(json.loads(line))
            except Exception as e:
                print(f"[Client] Listen error: {e}")
                self.connection_error = True
                break
        self.disconnect()

    def process_packet(self, packet):
        p_type = packet.get("type")
        
        if p_type == "welcome":
            self.client_id = packet["id"]
            self.current_seed = packet["seed"]
            
        elif p_type == "state_update":
            players_list = packet.get("players", [])
            
            # Keep track of active IDs to remove disconnected ones
            active_ids = []
            
            for p in players_list:
                p_id = p["id"]
                active_ids.append(p_id)
                
                # Don't update ourself in the remote_players list
                if p_id == self.client_id:
                    continue
                    
                if p_id not in self.remote_players:
                    # New player joined
                    self.remote_players[p_id] = {
                        "name": p["name"],
                        "alive": p["alive"],
                        "score": p["score"],
                        "ready": p["ready"],
                        "target_x": p["x"],
                        "target_y": p["y"],
                        "target_rot": p["rot"],
                        "curr_x": p["x"],
                        "curr_y": p["y"],
                        "curr_rot": p["rot"]
                    }
                else:
                    # Update targets for lerping
                    rp = self.remote_players[p_id]
                    rp["name"] = p["name"]
                    rp["alive"] = p["alive"]
                    rp["score"] = p["score"]
                    rp["ready"] = p["ready"]
                    
                    rp["target_x"] = p["x"]
                    rp["target_y"] = p["y"]
                    rp["target_rot"] = p["rot"]
                    
            # Remove disconnected
            to_remove = [pid for pid in self.remote_players if pid not in active_ids]
            for pid in to_remove:
                del self.remote_players[pid]
                
        elif p_type == "start_game":
            self.current_seed = packet["seed"]
            self.should_start_game = True
            
        elif p_type == "kicked":
            self.was_kicked = True
            self.disconnect()

    def update_interpolation(self, lerp_factor=0.3):
        # Called by main game loop every frame to smooth out positions
        for p in self.remote_players.values():
            p["curr_x"] += (p["target_x"] - p["curr_x"]) * lerp_factor
            p["curr_y"] += (p["target_y"] - p["curr_y"]) * lerp_factor
            p["curr_rot"] += (p["target_rot"] - p["curr_rot"]) * lerp_factor

    def send_update(self, x, y, rot, alive, score):
        self.send({
            "type": "update",
            "x": x,
            "y": y,
            "rot": rot,
            "alive": alive,
            "score": score
        })

    def send_ready(self, ready_state):
        self.send({"type": "ready", "ready": ready_state})
        
    def admin_start(self):
        self.send({"type": "admin_start"})
        
    def admin_kick(self, target_id):
        self.send({"type": "admin_kick", "target_id": target_id})

    def send(self, data):
        if not self.running or not self.socket:
            return
        try:
            msg = json.dumps(data) + "\n"
            self.socket.sendall(msg.encode('utf-8'))
        except:
            self.connection_error = True
            self.disconnect()

    def disconnect(self):
        self.running = False
        try:
            self.socket.close()
        except:
            pass

# Standalone Server runner
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("-a", "--admin", type=str, default="Admin")
    args = parser.parse_args()
    
    server = GameServer(port=args.port, admin_name=args.admin)
    server.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
