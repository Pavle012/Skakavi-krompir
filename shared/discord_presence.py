import queue
import threading
import time
import uuid


DISCORD_APPLICATION_ID = "1573391238051266642"
RECONNECT_SECONDS = 15


class DiscordPresence:
    def __init__(self, enabled=True):
        self.enabled = enabled
        self._started_at = int(time.time())
        self._activity = {
            "details": "In the menus",
            "state": "Ready to play",
            "start": self._started_at,
        }
        self._join_requests = queue.SimpleQueue()
        self._lock = threading.Lock()
        self._wake = threading.Event()
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if not self.enabled or (self._thread and self._thread.is_alive()):
            return
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def update(self, details, state=None, join_secret=None):
        if not self.enabled:
            return
        activity = {"details": details, "start": self._started_at}
        if state:
            activity["state"] = state
        if join_secret:
            activity["join"] = join_secret
            activity["party_id"] = join_secret
        with self._lock:
            if activity != self._activity:
                self._activity = activity
                self._wake.set()

    def take_join_request(self):
        try:
            return self._join_requests.get_nowait()
        except queue.Empty:
            return None

    def stop(self):
        self._stop.set()
        self._wake.set()
        if self._thread and self._thread is not threading.current_thread():
            self._thread.join(timeout=12)
            if self._thread.is_alive():
                print("[Discord] Rich Presence did not shut down before timeout.")

    def _run(self):
        client = None
        next_connect = 0
        activity_published = False

        while not self._stop.is_set():
            now = time.monotonic()
            if client is None and now >= next_connect:
                try:
                    from pypresence import Client

                    client = Client(DISCORD_APPLICATION_ID)
                    client.start()
                    client.register_event("ACTIVITY_JOIN", self._on_join)
                    print("[Discord] Rich Presence connected.", flush=True)
                    activity_published = False
                    self._wake.set()
                except Exception as exc:
                    print(f"[Discord] Rich Presence unavailable: {exc}")
                    client = None
                    next_connect = now + RECONNECT_SECONDS

            if client is not None and self._wake.is_set():
                with self._lock:
                    activity = dict(self._activity)
                    self._wake.clear()
                try:
                    client.set_activity(**activity)
                    if not activity_published:
                        print("[Discord] Rich Presence activity published.", flush=True)
                        activity_published = True
                except Exception as exc:
                    print(f"[Discord] Rich Presence update failed: {exc}")
                    self._close_client(client)
                    client = None
                    next_connect = now + RECONNECT_SECONDS

            wait_time = 1
            if client is None:
                with self._lock:
                    self._wake.clear()
                wait_time = min(wait_time, max(0, next_connect - time.monotonic()))
            self._wake.wait(wait_time)

        if client is not None:
            self._close_client(client)

    def _on_join(self, data):
        session_id = data.get("secret") if isinstance(data, dict) else None
        if not isinstance(session_id, str):
            print("[Discord] Ignored a join request with an invalid session.")
            return
        try:
            session_id = str(uuid.UUID(session_id))
        except ValueError:
            print("[Discord] Ignored a join request with an invalid session.")
            return
        self._join_requests.put(session_id)

    @staticmethod
    def _close_client(client):
        try:
            client.clear_activity()
        except Exception as exc:
            print(f"[Discord] Could not clear Rich Presence: {exc}")
        try:
            client.close()
        except Exception as exc:
            print(f"[Discord] Could not close Rich Presence connection: {exc}")
