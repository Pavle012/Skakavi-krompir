# --- EMERGENCY KIVY OVERRIDE (Must be very first lines) ---
import os
os.environ['KIVY_NO_ARGS'] = '1'
os.environ['KIVY_NO_CONFIG'] = '1'
os.environ['KIVY_NO_ENV_CONFIG'] = '1'
os.environ['KIVY_USE_DEFAULT_INPUT'] = '0'
os.environ['KIVY_AUDIO'] = 'none'

import sys
import traceback
from kivy.config import Config
# Completely wipe existing input sections
for section in ['input', 'mousetouch']:
    if Config.has_section(section):
        Config.remove_section(section)
Config.add_section('input')
Config.set('input', 'mouse', 'mouse')
Config.set('graphics', 'multisamples', '0')

# --- Standard Imports ---
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import random
from shared import dependencies
from shared.dependencies import is_compiled

print("[DEBUG] Running dependencies check...")
if not is_compiled():
    dependencies.checkifdepend()
    dependencies.fetch_assets()
dependencies.install_configs()
print("[DEBUG] Dependencies check finished.")

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, PushMatrix, PopMatrix, Rotate, RoundedRectangle, Line, InstructionGroup, Ellipse
from kivy.core.window import Window

# --- UI Overlay System ---

class GameButton(Button):
    def __init__(self, text, normal_color, hover_color, action_callback, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.normal_color = [c/255.0 for c in normal_color] + [1]
        self.hover_color = [c/255.0 for c in hover_color] + [1]
        self.action_callback = action_callback
        self.background_normal = ''
        self.background_color = self.normal_color
        self.size_hint_y = None
        self.height = 50
        self.font_size = 22

    def on_release(self):
        if self.action_callback:
            self.action_callback()

class UIOverlay(ModalView):
    def __init__(self, title, info_lines, button_defs, title_color=(255,255,255), **kwargs):
        super().__init__(**kwargs)
        self.background = ''
        self.background_color = [0, 0, 0, 0.5]
        self.size_hint = (None, None)
        self.width = 450
        self.auto_dismiss = False

        with self.canvas.before:
            Color(30/255, 30/255, 40/255, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            Color(1, 1, 1, 1)
            self.line = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, 20), width=2)
            
        self.bind(pos=self.update_graphics, size=self.update_graphics)

        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=10, size_hint_y=None)
        main_layout.bind(minimum_height=main_layout.setter('height'))
        
        t_color = [c/255.0 for c in title_color] + [1]
        main_layout.add_widget(Label(text=title, color=t_color, font_size=42, size_hint_y=None, height=60, bold=True))

        for line in info_lines:
            main_layout.add_widget(Label(text=line, font_size=20, size_hint_y=None, height=35))

        for b_text, norm_col, hov_col, action in button_defs:
            btn = GameButton(b_text, norm_col, hov_col, action)
            btn.size_hint_x = None
            btn.width = 320
            btn.pos_hint = {'center_x': 0.5}
            main_layout.add_widget(btn)

        # Cap height and enable scrolling
        self.height = min(100 + len(info_lines)*40 + len(button_defs)*60, Window.height * 0.85)
        
        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll.add_widget(main_layout)
        self.add_widget(scroll)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.line.rounded_rectangle = (self.x, self.y, self.width, self.height, 20)

# --- Game Logic ---

class Pipe:
    def __init__(self, x, y, is_top):
        self.x = x
        self.y = y
        self.is_top = is_top
        self.width = 50

class GameWidget(Widget):
    def __init__(self, app_ref, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref
        self.velocity = 0
        self.jump_velocity = 8
        self.scroll_pixels_per_frame = 8
        self.potato_x = 100
        self.potato_y = 300
        self.pipes = []
        self.pipe_spacing = 300
        self.gap_size = 300
        self.scroll = 500
        self.points = 0
        self.alive = False
        self.subsystems_ready = False
        self._keyboard = None
        
        # Managers
        self.particle_manager = None
        self.powerup_manager = None
        self.achievement_manager = None

        with self.canvas:
            self.bg_color = Color(66/255, 183/255, 237/255)
            self.bg_rect = Rectangle(pos=self.pos, size=self.size)
            self.pipe_instrs = InstructionGroup()
            self.canvas.add(self.pipe_instrs)
            self.powerup_instrs = InstructionGroup()
            self.canvas.add(self.powerup_instrs)
            self.particle_instrs = InstructionGroup()
            self.canvas.add(self.particle_instrs)
            self.potato_color = Color(1, 1, 1)
            self.potato_push = PushMatrix()
            self.potato_rotate = Rotate(angle=0)
            self.potato_rect = Rectangle(pos=(self.potato_x, self.potato_y), size=(50, 50))
            self.potato_pop = PopMatrix()
            self.invinc_instrs = InstructionGroup()
            self.canvas.add(self.invinc_instrs)

        self.bind(pos=self._update_bg, size=self._update_bg)
        Clock.schedule_once(self._late_init, 0.2)

    def _update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _late_init(self, dt):
        print("[DEBUG] Minimal Late Init...")
        try:
            # Physics
            settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
            if os.path.exists(settings_path):
                with open(settings_path) as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            if k == "jumpVelocity": self.jump_velocity = float(v)
                            if k == "scrollPixelsPerFrame": self.scroll_pixels_per_frame = float(v)

            # Potato Texture
            potato_path = dependencies.get_potato_path()
            if os.path.exists(potato_path):
                self.potato_rect.source = potato_path

            self.potato_y = self.height / 2
            
            from kivy_game.particles import ParticleManager
            self.particle_manager = ParticleManager()
            from kivy_game.powerups import PowerupManager
            self.powerup_manager = PowerupManager(dependencies.get_assets_dir())
            from kivy_game.achievements import AchievementManager
            self.achievement_manager = AchievementManager()

            self._keyboard = Window.request_keyboard(lambda: None, self)
            if self._keyboard:
                self._keyboard.bind(on_key_down=self._on_keyboard_down)

            self.subsystems_ready = True
            print("[DEBUG] Ready.")
        except Exception as e:
            print(f"[ERROR] Late init failed: {e}")
            traceback.print_exc()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        if keycode[1] in ('space', 'up'): self.jump()
        elif keycode[1] == 'escape': self.app.pause_game()
        return True

    def on_touch_down(self, touch):
        if self.alive: self.jump()
        return True
        
    def jump(self):
        if self.alive:
            self.velocity = -self.jump_velocity
            if self.particle_manager:
                self.particle_manager.create_jump_effect(self.potato_x + 25, self.potato_y)

    def restart(self):
        self.potato_x, self.potato_y, self.velocity = 100, self.height / 2, 0
        self.scroll, self.points, self.pipes = 500, 0, []
        for i in range(10):
            ry = random.randint(-100, 100)
            tx = 100 + (i * self.pipe_spacing)
            self.pipes.append(Pipe(tx, (self.height/2) + self.gap_size - 750 + ry, True))
            self.pipes.append(Pipe(tx, (self.height/2) + self.gap_size - 150 + ry, False))
            if self.powerup_manager and random.random() < 0.3:
                self.powerup_manager.spawn_powerup(tx + 10, (self.height/2) + self.gap_size - 300 + ry)
        if self.particle_manager: self.particle_manager.particles = []
        if self.powerup_manager: self.powerup_manager.reset()
        self.alive = True

    def update(self, dt):
        if not self.alive or not self.subsystems_ready:
            self.draw()
            return
        
        # Physics
        self.velocity += 0.5 * dt * 60
        self.potato_y -= self.velocity * dt * 60
        
        speed_mult = 1.0
        if self.powerup_manager and self.powerup_manager.is_effect_active("speed"):
            speed_mult = self.powerup_manager.get_effect_value("speed", 1.0)
            
        self.scroll -= self.scroll_pixels_per_frame * dt * 60 * speed_mult
        
        if self.particle_manager:
            self.particle_manager.update(dt)
        
        potato_rect = [self.potato_x, self.potato_y, 50, 50]
        if self.powerup_manager:
            collected, expired = self.powerup_manager.update(dt, self.scroll, potato_rect)
            if collected and self.particle_manager:
                self.particle_manager.create_pickup_effect(self.potato_x + 25, self.potato_y + 25)
        
        # Scoring
        new_points = int(-self.scroll // self.pipe_spacing + 1) if self.scroll < 0 else 0
        if new_points > self.points:
            self.points = new_points
            if self.achievement_manager:
                self.achievement_manager.update_stat("high_score", self.points, incremental=False)

        # Respawn Pipes
        while self.pipes and self.pipes[0].x + self.scroll < -100:
            self.pipes.pop(0)
        
        if len(self.pipes) < 20: # Keep 10 pairs
            last_x = self.pipes[-1].x if self.pipes else 100
            ry = random.randint(-100, 100)
            tx = last_x + self.pipe_spacing
            self.pipes.append(Pipe(tx, (self.height/2) + self.gap_size - 750 + ry, True))
            self.pipes.append(Pipe(tx, (self.height/2) + self.gap_size - 150 + ry, False))
            if self.powerup_manager and random.random() < 0.3:
                self.powerup_manager.spawn_powerup(tx + 10, (self.height/2) + self.gap_size - 300 + ry)

        if self.potato_y < 0 or self.potato_y > self.height:
            if not (self.powerup_manager and self.powerup_manager.is_effect_active("invincibility")):
                self.app.game_over()

        for p in self.pipes:
            rx = p.x + self.scroll
            if rx > self.potato_x + 50 or rx + p.width < self.potato_x: continue
            if p.is_top:
                if self.potato_y < p.y + 300:
                    if not (self.powerup_manager and self.powerup_manager.is_effect_active("invincibility")):
                        self.app.game_over()
            else:
                if self.potato_y + 50 > p.y:
                    if not (self.powerup_manager and self.powerup_manager.is_effect_active("invincibility")):
                        self.app.game_over()
        self.draw()

    def draw(self):
        # Pipes
        self.pipe_instrs.clear()
        self.pipe_instrs.add(Color(0.2, 0.8, 0.2))
        for p in self.pipes:
            rx = self.x + p.x + self.scroll
            if rx < -100 or rx > self.width + 100: continue
            if p.is_top: self.pipe_instrs.add(Rectangle(pos=(rx, self.y), size=(p.width, p.y + 300)))
            else: self.pipe_instrs.add(Rectangle(pos=(rx, self.y + p.y), size=(p.width, self.height - p.y)))
        
        # Powerups
        self.powerup_instrs.clear()
        if self.powerup_manager:
            for pu in self.powerup_manager.powerups:
                px = self.x + pu.rect[0]
                if -50 < px < self.width + 50:
                    self.powerup_instrs.add(Color(pu.color[0]/255, pu.color[1]/255, pu.color[2]/255, 1))
                    self.powerup_instrs.add(RoundedRectangle(pos=(px, self.y + pu.y), size=(30, 30), radius=[15]))
                    self.powerup_instrs.add(Color(1, 1, 1, 1))
                    self.powerup_instrs.add(Ellipse(pos=(px + 10, self.y + pu.y + 10), size=(10, 10)))

        # Particles
        self.particle_instrs.clear()
        if self.particle_manager:
            for pt in self.particle_manager.particles:
                if pt.life > 0:
                    self.particle_instrs.add(Color(pt.color[0]/255, pt.color[1]/255, pt.color[2]/255, pt.life))
                    self.particle_instrs.add(Ellipse(pos=(self.x + pt.x - pt.size, self.y + pt.y - pt.size), size=(pt.size*2, pt.size*2)))

        # Potato
        self.potato_rotate.angle = max(min(self.velocity * -2.5, 30), -90)
        self.potato_rotate.origin = (self.x + self.potato_x + 25, self.y + self.potato_y + 25)
        self.potato_rect.pos = (self.x + self.potato_x, self.y + self.potato_y)

        # Shield
        self.invinc_instrs.clear()
        if self.powerup_manager and self.powerup_manager.is_effect_active("invincibility"):
            self.invinc_instrs.add(Color(0, 1, 1, 1))
            self.invinc_instrs.add(Line(circle=(self.x + self.potato_x + 25, self.y + self.potato_y + 25, 30), width=3))

class SkakaviApp(App):
    def build(self):
        Window.bind(on_request_close=lambda *a: os._exit(0))
        Window.clearcolor = (66/255, 183/255, 237/255, 1)
        self.root_layout = FloatLayout()
        self.game = GameWidget(app_ref=self)
        self.root_layout.add_widget(self.game)
        self.score_label = Label(text="", font_size=32, size_hint=(None, None), size=(100, 50), pos_hint={'right': 0.95, 'top': 0.95})
        self.root_layout.add_widget(self.score_label)
        self.current_modal = None
        Clock.schedule_interval(self.game.update, 1.0/60.0)
        Clock.schedule_interval(self.update_score, 0.1)
        Clock.schedule_once(lambda dt: self.show_main_menu(), 0.5)
        return self.root_layout
        
    def update_score(self, dt):
        if self.game.alive: self.score_label.text = f"Points: {self.game.points}"

    def close_modal(self):
        if self.current_modal:
            self.current_modal.dismiss()
            self.current_modal = None

    def start_game(self):
        self.close_modal()
        self.game.restart()

    def pause_game(self):
        if not self.game.alive or self.current_modal: return
        self.game.alive = False
        self.show_pause_menu()

    def resume_game(self):
        self.close_modal()
        self.game.alive = True
        
    def game_over(self):
        self.game.alive = False
        self.show_lose_menu()

    def open_settings(self):
        self.close_modal()
        from kivy_game import options
        def on_close():
            if not self.game.alive: self.show_main_menu()
        options.start_settings(on_close=on_close)

    def open_scores(self):
        self.close_modal()
        from kivy_game import scores
        scores.start()

    def open_achievements(self):
        self.close_modal()
        from kivy_game import achievements
        achievements.show_achievements_gui()

    def open_leaderboard(self):
        self.close_modal()
        from kivy_game import scores
        scores.start_public()

    def open_replays(self):
        self.close_modal()
        from kivy_game import replays
        replays.start(on_select=lambda data: print(f"Selected Replay: {data}"))

    def exit_game(self):
        os._exit(0)

    def show_main_menu(self):
        self.close_modal()
        self.current_modal = UIOverlay("Skakavi Krompir", [], [
            ("Start Game", (46, 204, 113), (39, 174, 96), self.start_game),
            ("Multiplayer", (155, 89, 182), (142, 68, 173), lambda: print("Multiplayer Triggered")),
            ("Achievements", (255, 215, 0), (218, 165, 32), self.open_achievements),
            ("Settings", (155, 89, 182), (142, 68, 173), self.open_settings),
            ("Scores", (52, 152, 219), (41, 128, 185), self.open_scores),
            ("Leaderboard", (52, 152, 219), (41, 128, 185), self.open_leaderboard),
            ("Replays", (230, 126, 34), (211, 84, 0), self.open_replays),
            ("Exit", (231, 76, 60), (192, 57, 43), self.exit_game),
        ])
        self.current_modal.open()

    def show_pause_menu(self):
        self.close_modal()
        self.current_modal = UIOverlay("PAUSED", [], [
            ("Resume", (46, 204, 113), (39, 174, 96), self.resume_game),
            ("Leaderboard", (52, 152, 219), (41, 128, 185), self.open_leaderboard),
            ("Settings", (155, 89, 182), (142, 68, 173), self.open_settings),
            ("Exit", (231, 76, 60), (192, 57, 43), self.exit_game),
        ])
        self.current_modal.open()

    def show_lose_menu(self):
        self.close_modal()
        self.current_modal = UIOverlay("YOU LOST!", [f"Score: {self.game.points}"], [
            ("Restart", (46, 204, 113), (39, 174, 96), self.start_game),
            ("Leaderboard", (52, 152, 219), (41, 128, 185), self.open_leaderboard),
            ("Exit", (231, 76, 60), (192, 57, 43), self.exit_game),
        ], title_color=(255, 80, 80))
        self.current_modal.open()

if __name__ == '__main__':
    SkakaviApp().run()
