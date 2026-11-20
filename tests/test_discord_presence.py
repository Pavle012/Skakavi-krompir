import sys
import threading
import types
import unittest
from unittest.mock import patch

from shared.discord_presence import DiscordPresence


class FakePresence:
    def __init__(self, client_id):
        self.client_id = client_id
        self.connected = False
        self.updates = []
        self.updated = threading.Event()
        self.cleared = False
        self.closed = False
        self.events = {}

    def start(self):
        self.connected = True

    def register_event(self, event, callback):
        self.events[event.lower()] = callback

    def set_activity(self, **activity):
        self.updates.append(activity)
        self.updated.set()

    def clear_activity(self):
        self.cleared = True

    def close(self):
        self.closed = True


class DiscordPresenceTests(unittest.TestCase):
    def test_sends_current_activity_and_clears_on_stop(self):
        client = FakePresence("test-app-id")
        fake_module = types.SimpleNamespace(Client=lambda client_id: client)
        with patch.dict(sys.modules, {"pypresence": fake_module}):
            presence = DiscordPresence()
            presence.start()
            self.assertTrue(client.updated.wait(timeout=2))
            client.updated.clear()
            presence.update(
                "In a multiplayer lobby",
                "2 players",
                join_secret="session-123",
            )
            self.assertTrue(client.updated.wait(timeout=2))
            session_id = "d9428888-122b-11e1-b85c-61cd3cbb3210"
            client.events["activity_join"]({"secret": session_id})
            client.events["activity_join"]({"secret": "../../unexpected-path"})
            presence.stop()

        self.assertTrue(client.connected)
        self.assertIn("activity_join", client.events)
        self.assertEqual(
            client.updates[-1],
            {
                "details": "In a multiplayer lobby",
                "state": "2 players",
                "join": "session-123",
                "party_id": "session-123",
            },
        )
        self.assertEqual(presence.take_join_request(), session_id)
        self.assertIsNone(presence.take_join_request())
        self.assertTrue(client.cleared)
        self.assertTrue(client.closed)

    def test_disabled_presence_does_not_connect(self):
        client = FakePresence("test-app-id")
        fake_module = types.SimpleNamespace(Client=lambda client_id: client)
        with patch.dict(sys.modules, {"pypresence": fake_module}):
            presence = DiscordPresence(enabled=False)
            presence.start()
            presence.update("Playing Classic", "Score: 4")
            presence.stop()

        self.assertFalse(client.connected)
        self.assertEqual(client.updates, [])


if __name__ == "__main__":
    unittest.main()
