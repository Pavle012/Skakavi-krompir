import requests
from typing import List, Optional

DIRECTORY_URL = "https://dragon-honest-directly.ngrok-free.app"


def _url(path: str) -> str:
    return DIRECTORY_URL.rstrip("/") + path


def register_user(username: str) -> bool:
    try:
        r = requests.post(_url("/users/register"), json={"username": username}, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def send_friend_request(requester: str, target: str, message: Optional[str] = None) -> bool:
    try:
        payload = {"requester": requester, "target": target, "message": message or ""}
        r = requests.post(_url("/friends/request"), json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def accept_friend(requester: str, target: str) -> bool:
    try:
        payload = {"requester": requester, "target": target}
        r = requests.post(_url("/friends/accept"), json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def remove_friend(user: str, friend: str) -> bool:
    try:
        payload = {"user": user, "friend": friend}
        r = requests.post(_url("/friends/remove"), json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def list_friends(username: str) -> List[str]:
    try:
        r = requests.get(_url(f"/friends/{username}"), timeout=5)
        if r.status_code == 200:
            data = r.json()
            return [d.get("friend") for d in data]
    except Exception:
        pass
    return []


def list_friend_hosts(username: str) -> List[dict]:
    try:
        r = requests.get(_url(f"/hosts/friends/{username}"), timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def list_pending_requests(username: str) -> List[dict]:
    try:
        r = requests.get(_url(f"/friends/requests/{username}"), timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def reject_friend_request(requester: str, target: str) -> bool:
    try:
        payload = {"requester": requester, "target": target}
        r = requests.post(_url("/friends/reject"), json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def list_hosts() -> List[dict]:
    try:
        r = requests.get(_url("/hosts/list"), timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return []


def register_host(owner: str, host_name: str, external_ip: str, port: int, description: str = "Skakavi Krompir host") -> bool:
    try:
        payload = {"owner": owner, "host_name": host_name, "external_ip": external_ip, "port": port, "description": description}
        r = requests.post(_url("/hosts/register"), json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def unregister_host(owner: str) -> bool:
    try:
        payload = {"owner": owner}
        r = requests.post(_url("/hosts/unregister"), json=payload, timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def create_multiplayer_session(owner: str, host_name: str, description: str = "Skakavi Krompir host") -> Optional[dict]:
    try:
        payload = {"owner": owner, "host_name": host_name, "description": description}
        r = requests.post(_url("/multiplayer/sessions"), json=payload, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def multiplayer_websocket_url(session_id: str) -> str:
    base_url = DIRECTORY_URL.rstrip("/")
    if base_url.startswith("https://"):
        base_url = "wss://" + base_url[len("https://"):]
    elif base_url.startswith("http://"):
        base_url = "ws://" + base_url[len("http://"):]
    return f"{base_url}/multiplayer/ws/{session_id}"
