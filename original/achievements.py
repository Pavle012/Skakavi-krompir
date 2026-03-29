import os
import json
from shared import dependencies
from original import pygame_ui


class AchievementManager:
    def __init__(self):
        self.achievements_file = os.path.join(dependencies.get_user_data_dir(), "achievements.json")
        self.achievements = self.load_achievements()
        self.stats = self.load_stats()

        # Define achievements
        self.definitions = {
            "first_steps": {"title": "First Steps", "description": "Score 10 points", "target": 10, "stat": "high_score"},
            "master":      {"title": "Potato Master", "description": "Score 50 points", "target": 50, "stat": "high_score"},
            "legend":      {"title": "Potato Legend", "description": "Score 100 points", "target": 100, "stat": "high_score"},
            "collector":   {"title": "Powerup Collector", "description": "Collect 50 powerups", "target": 50, "stat": "total_powerups"},
            "survivor":    {"title": "Survivor", "description": "Collect 5 powerups in one run", "target": 5, "stat": "powerups_in_run"},
            "persistent":  {"title": "Persistent", "description": "Play 100 games", "target": 100, "stat": "total_games"},
            "zen_master":  {"title": "Zen Master", "description": "Score 100 points in Zen Mode", "target": 100, "stat": "zen_high_score"},
        }

    def load_achievements(self):
        if os.path.exists(self.achievements_file):
            try:
                with open(self.achievements_file, "r") as f:
                    return json.load(f).get("unlocked", [])
            except Exception:
                return []
        return []

    def load_stats(self):
        stats_file = os.path.join(dependencies.get_user_data_dir(), "stats.json")
        if os.path.exists(stats_file):
            try:
                with open(stats_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "high_score": 0,
            "total_powerups": 0,
            "total_games": 0,
            "zen_high_score": 0,
            "total_time_played": 0,
        }

    def save_achievements(self):
        with open(self.achievements_file, "w") as f:
            json.dump({"unlocked": self.achievements}, f)

    def save_stats(self):
        stats_file = os.path.join(dependencies.get_user_data_dir(), "stats.json")
        with open(stats_file, "w") as f:
            json.dump(self.stats, f)

    def update_stat(self, stat_name, value, incremental=True):
        if incremental:
            self.stats[stat_name] = self.stats.get(stat_name, 0) + value
        else:
            self.stats[stat_name] = max(self.stats.get(stat_name, 0), value)
        self.check_achievements()
        self.save_stats()

    def check_achievements(self):
        new_unlocked = []
        for ach_id, defn in self.definitions.items():
            if ach_id not in self.achievements:
                stat_val = self.stats.get(defn["stat"], 0)
                if stat_val >= defn["target"]:
                    self.achievements.append(ach_id)
                    new_unlocked.append(defn["title"])
        if new_unlocked:
            self.save_achievements()
        return new_unlocked

    def get_unlocked_count(self):
        return len(self.achievements)

    def get_total_count(self):
        return len(self.definitions)


def show_achievements_gui():
    """Display achievements as a pygame overlay. No arguments needed."""
    manager = AchievementManager()

    rows = []
    for ach_id, defn in manager.definitions.items():
        is_unlocked = ach_id in manager.achievements
        stat_val = manager.stats.get(defn["stat"], 0)
        status = "✓ Unlocked!" if is_unlocked else f"{stat_val}/{defn['target']}"
        rows.append((
            defn["title"],
            defn["description"],
            status,
        ))

    columns = [
        ("Achievement", 0.30),
        ("Description", 0.45),
        ("Progress",    0.25),
    ]

    unlocked = manager.get_unlocked_count()
    total = manager.get_total_count()
    extra_info = [f"Unlocked: {unlocked}/{total}"]

    pygame_ui.draw_scrollable_list(
        title="Achievements",
        rows=rows,
        columns=columns,
        extra_info=extra_info,
    )
