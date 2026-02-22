import sys
import argparse
import json
import threading
import time
import dependencies
from dependencies import is_compiled

if not is_compiled():
    dependencies.checkifdepend()
    dependencies.fetch_assets()
dependencies.install_configs()
dependencies.load_global_icon_pil()

# Argument Parsing
parser = argparse.ArgumentParser(description="Skakavi Krompir Game")
parser.add_argument("--data-dir", type=str, help="Path to custom data directory")
args = parser.parse_args()

if args.data_dir:
    dependencies.set_custom_data_dir(args.data_dir)
    if not os.path.exists(args.data_dir):
        os.makedirs(args.data_dir)

# Helper for status dumping
def dump_status(status_text, score, state):
    try:
        data = {
            "status": status_text,
            "score": score,
            "state": state,
            "timestamp": time.time()
        }
        with open(os.path.join(dependencies.get_user_data_dir(), "status.json"), "w") as f:
            json.dump(data, f)
    except Exception:
        pass
import pygame
import scores
import achievements
import random
import namecheck
import modloader
import datetime
import os
import replays
import particles
import powerups
import options
import multiplayer
import customtkinter as ctk
from typing import Optional

paused = False  # initialize before use because of type checking
mp_server = None
mp_client = None
x = 100         # default x (restart() will overwrite)
y = 0           # default y (restart() will overwrite)
points = 0      # default points (restart() will overwrite)
velocity = 0    # etc.
scroll = 500
speed_increase = 3
difficulty = "Normal"
game_mode = "Classic"
time_left = 60.0
powerups_collected_this_run = 0
achievement_manager = None
rotated_image = None
rotated_rect = None
game_state_for_mods = {}
dying = False
replaying = False
current_replay_data = None
current_recording = []
frame_index = 0
current_seed = 0
replay_config = {}
powerup_manager = None
replay_speed = 1.0
replay_paused = False
replay_markers = []

###############################################
############ Flappy Bird-like Game ############
###############################################

################################################
################### Classes ####################
################################################
class pipe:
    def __init__(self, x, y, is_top):
        self.x = x
        self.y = y
        self.is_top = is_top

    def draw(self, screen):
        if self.is_top:
            pygame.draw.rect(screen, pipeColor, (self.x, 0, 50, self.y + 300))
        else:
            pygame.draw.rect(screen, pipeColor, (self.x, self.y, 50, HEIGHT - self.y))

class Button:
    def __init__(self, text, x, y, width, height, color, hover_color, action):
        self.text = text
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hover_color = hover_color
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect, border_radius=10)
        else:
            pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        
        btn_font = pygame.font.Font(dependencies.get_font_path(), 24)
        text_surf = btn_font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return self.action()
        return None

################################################
################### Functions ##################
################################################

class FloatingText:
    def __init__(self, text, x, y, color=(255, 255, 255)):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.timer = 60 # 1 second at 60fps
        self.font = pygame.font.Font(dependencies.get_font_path(), 24)
        
    def update(self):
        self.y -= 1 # Float up
        self.timer -= 1
        return self.timer > 0
        
    def draw(self, screen):
        # simple fade out could be added but let's stick to simple timer
        surf = self.font.render(self.text, True, self.color)
        screen.blit(surf, (self.x, self.y))

floating_texts = []



def restart(replay_data=None):
    global scrollPixelsPerFrame, jumpVelocity, velocity, x, y, maxfps, clock, paused, points, text_str, text, pipeNumber, scroll, PIPE_SPACING, pipesPos, pipeColor, image, WIDTH, HEIGHT, dying
    global replaying, current_replay_data, current_recording, frame_index, current_seed, replay_config, speed_increase, powerup_manager
    global particle_manager, mp_client, replay_speed, replay_paused, replay_markers
    global difficulty, game_mode, time_left, powerups_collected_this_run, achievement_manager
    
    reloadSettings()
    
    replay_speed = 1.0
    replay_paused = False
    replay_markers = []
    
    if achievement_manager is None:
        achievement_manager = achievements.AchievementManager()
    
    achievement_manager.update_stat("total_games", 1)
    
    particle_manager = particles.ParticleManager()
    
    if replay_data:
        replaying = True
        current_replay_data = replay_data
        current_recording = []
        frame_index = 0
        current_seed = replay_data["seed"]
        replay_config = replay_data["config"]
        # Apply recorded config
        scrollPixelsPerFrame = replay_config.get("scrollPixelsPerFrame", scrollPixelsPerFrame)
        jumpVelocity = replay_config.get("jumpVelocity", jumpVelocity)
        speed_increase = replay_config.get("speed_increase", speed_increase)
        difficulty = replay_config.get("difficulty", "Normal")
        game_mode = replay_config.get("game_mode", "Classic")
        
        # Collect markers
        replay_markers = []
        for i, frame in enumerate(current_replay_data["frames"]):
            if frame.get("jump"):
                replay_markers.append({"frame": i, "type": "jump"})
            if frame.get("powerup"):
                replay_markers.append({"frame": i, "type": "powerup"})
    else:
        replaying = False
        current_replay_data = None
        current_recording = []
        frame_index = 0
        if mp_client and mp_client.current_seed is not None:
            current_seed = mp_client.current_seed
        else:
            current_seed = int(time.time() * 1000)
        
        replay_config = {
            "scrollPixelsPerFrame": scrollPixelsPerFrame,
            "jumpVelocity": jumpVelocity,
            "speed_increase": speed_increase,
            "difficulty": difficulty,
            "game_mode": game_mode
        }
    
    # Apply Difficulty Settings
    PIPE_SPACING = 300
    GAP_SIZE = 300
    if difficulty == "Easy":
        scrollPixelsPerFrame = max(1, scrollPixelsPerFrame - 1)
        GAP_SIZE = 400
        PIPE_SPACING = 400
    elif difficulty == "Hard":
        scrollPixelsPerFrame += 1
        GAP_SIZE = 200
        PIPE_SPACING = 250
        
    random.seed(current_seed)
    
    dying = False
    velocity = 0
    x = 100
    y = (HEIGHT // 2)
    maxfps = 60
    clock = pygame.time.Clock()
    paused = False
    points = 0
    time_left = 60.0
    powerups_collected_this_run = 0
    text_str = f"Points: {points}"
    text = font.render(text_str, True, (255, 255, 255))
    pipeNumber = 500
    scroll = 500
    pipesPos = []
    powerup_manager.reset()
    pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for i in range(pipeNumber):
        randomY = random.randint(-100, 100)
        pipesPos.append((100 + (i * PIPE_SPACING), (HEIGHT/2) + GAP_SIZE + -750 + randomY, True))
        pipesPos.append((100 + (i * PIPE_SPACING), (HEIGHT/2) + GAP_SIZE + -150 + randomY, False))
        
        gap_center_y = (HEIGHT/2) + GAP_SIZE + randomY - 300
        
        # 30% chance to spawn a powerup (Higher in Zen mode?)
        powerup_chance = 0.3
        if game_mode == "Zen": powerup_chance = 0.5
        
        if random.random() < powerup_chance:
            powerup_x = 100 + (i * PIPE_SPACING) + 10 
            powerup_manager.spawn_powerup(powerup_x, gap_center_y)
    
    # Reload the image in case it was changed
    image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
    image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
    modloader.trigger_on_restart()

def seek_to_frame(target_frame):
    global frame_index, current_replay_data, velocity, x, y, points, scroll, scrollPixelsPerFrame
    global rotated_image, rotated_rect, time_left, powerup_manager, floating_texts
    
    if not current_replay_data: return
    
    target_frame = max(0, min(target_frame, len(current_replay_data["frames"])))
    
    # Save replaying state
    was_replaying = True
    
    # Do a fresh restart
    restart(current_replay_data)
    
    # Run simulation up to target_frame (silent)
    for i in range(target_frame):
        frame = current_replay_data["frames"][i]
        sim_delta = frame["delta"]
        
        # Handle jump
        if frame["jump"]:
            velocity = -jumpVelocity
            particle_manager.create_jump_effect(x + 39, y + 58)
            
        # Physics update
        velocity += 0.5 * sim_delta * 60
        y += velocity * sim_delta * 60
        
        # Points and scroll
        # (Simplified, same as main loop)
        speed_multiplier = 1.0
        if powerup_manager.is_effect_active("speed"):
             speed_multiplier = powerup_manager.get_effect_value("speed", 1.0)
        
        scroll -= scrollPixelsPerFrame * sim_delta * 60 * speed_multiplier
        
        if (-scroll // PIPE_SPACING) < 0:
            points = 0
        else:
            points = int(-scroll // PIPE_SPACING + 1)
            
        if points % 10 == 0 and points != 0:
            scrollPixelsPerFrame += speed_increase * 0.01 * sim_delta * 60
            
        # Rotation for collisions
        angle = max(min(velocity * -2.5, 30), -90)
        sim_rotated_image = pygame.transform.rotate(image, angle)
        sim_rotated_rect = sim_rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)
        
        # Powerups
        powerup_manager.update(sim_delta, scroll, sim_rotated_rect)
        
        # Time Attack
        if game_mode == "Time Attack":
            time_left -= sim_delta
            
    # Set final frame index
    frame_index = target_frame
    
    # Update visual state
    angle = max(min(velocity * -2.5, 30), -90)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_rect = rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)
    floating_texts = [] # Clear floating texts when scrubbing



def isPotatoColliding(potato_surface, potato_rect):
    global pipesPos, scroll, powerup_manager
    
    # Invincibility check
    if powerup_manager.is_effect_active("invincibility"):
        return False
        
    # Create a mask from the rotated potato surface.
    potato_mask = pygame.mask.from_surface(potato_surface)

    # Iterate over each pipe.
    for px, py, is_top in pipesPos:
        realX = px + scroll
        
        # Optimization: Only check pipes that are roughly on screen
        if realX < -100 or realX > WIDTH + 100:
            continue

        if is_top:
            p_height = py + 300
            if p_height <= 0:
                continue
            pipe_rect = pygame.Rect(realX, 0, 50, p_height)
            # First, a simple and fast bounding box check.
            if not potato_rect.colliderect(pipe_rect):
                continue
            pipe_mask = pygame.mask.Mask((50, p_height), fill=True)
        else:
            p_height = HEIGHT - py
            if p_height <= 0:
                continue
            pipe_rect = pygame.Rect(realX, py, 50, p_height)
            # First, a simple and fast bounding box check.
            if not potato_rect.colliderect(pipe_rect):
                continue
            pipe_mask = pygame.mask.Mask((50, p_height), fill=True)

        # Calculate the offset between the potato and the pipe.
        offset = (pipe_rect.x - potato_rect.x, pipe_rect.y - potato_rect.y)

        # Check for overlap between the masks.
        if potato_mask.overlap(pipe_mask, offset):
            return True # Collision detected

    return False # No collision


def spawnPipe():
    global pipesPos, scroll, pipeColor, screen
    for px, py, is_top in pipesPos:
        realX = px + scroll
        # Optimization: Only draw pipes that are at least partially on screen
        if realX < -100 or realX > WIDTH + 100:
            continue
        pipe(realX, py, is_top).draw(screen)

def render_game():
    global screen, WIDTH, HEIGHT, rotated_image, rotated_rect, points, font, game_state_for_mods, mp_client
    screen.fill((66, 183, 237))
    spawnPipe()
    particle_manager.draw(screen)
    powerup_manager.draw(screen, scroll)
    
    # Draw ghost players
    if mp_client:
        mp_client.update_interpolation()
        for p_id, p in mp_client.remote_players.items():
            if not p["alive"]:
                 continue
            # Draw translucent potato
            ghost_angle = p["curr_rot"]
            ghost_img = pygame.transform.rotate(image, ghost_angle)
            ghost_img.set_alpha(150) # Translucent
            ghost_rect = ghost_img.get_rect(center=(p["curr_x"] + 39, p["curr_y"] + 29)) # Approx center
            screen.blit(ghost_img, ghost_rect.topleft)
            
            # Draw name tag
            name_font = pygame.font.Font(dependencies.get_font_path(), 18)
            name_surf = name_font.render(p["name"], True, (255, 255, 255))
            name_rect = name_surf.get_rect(center=(p["curr_x"] + 39, p["curr_y"] - 10))
            screen.blit(name_surf, name_rect)

    if rotated_image and rotated_rect:
        screen.blit(rotated_image, rotated_rect.topleft)
        
    # Draw invincibility shield
    if powerup_manager.is_effect_active("invincibility"):
        # Pulsing shield
        pulse = (pygame.time.get_ticks() // 100) % 5
        pygame.draw.circle(screen, (0, 255, 255), rotated_rect.center, 30 + pulse, 3)
        
    # Draw Floating Texts
    for ft in floating_texts:
        ft.draw(screen)

    points_text = font.render(f"Points: {points}", True, (255, 255, 255))
    screen.blit(points_text, (WIDTH - points_text.get_width() - 10, 10))
    
    # Show Mode and Difficulty
    mode_font = pygame.font.Font(dependencies.get_font_path(), 18)
    mode_text = mode_font.render(f"{game_mode} | {difficulty}", True, (255, 255, 255))
    screen.blit(mode_text, (10, 10))
    
    if game_mode == "Time Attack":
        timer_color = (255, 255, 255)
        if time_left < 10: timer_color = (255, 100, 100)
        timer_text = font.render(f"Time: {int(time_left)}s", True, timer_color)
        screen.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 10))
    
    if replaying:
        # Replay UI
        replay_font = pygame.font.Font(dependencies.get_font_path(), 18)
        status = "PAUSED" if replay_paused else "PLAYING"
        replay_text = replay_font.render(f"REPLAY: {status} ({replay_speed}x)", True, (255, 255, 0))
        screen.blit(replay_text, (10, HEIGHT - 30))
        
        # Progress bar
        bar_width = WIDTH - 40
        bar_height = 10
        pygame.draw.rect(screen, (100, 100, 100), (20, HEIGHT - 50, bar_width, bar_height), border_radius=5)
        if current_replay_data:
            total_frames = len(current_replay_data["frames"])
            progress = frame_index / total_frames
            pygame.draw.rect(screen, (255, 255, 0), (20, HEIGHT - 50, bar_width * progress, bar_height), border_radius=5)
            
            # Draw markers
            for marker in replay_markers:
                m_x = 20 + (marker["frame"] / total_frames) * bar_width
                m_color = (255, 255, 255) if marker["type"] == "jump" else (255, 215, 0)
                pygame.draw.circle(screen, m_color, (int(m_x), HEIGHT - 45), 3)
            
        # Help text
        help_text = replay_font.render("P: Pause | +/-: Speed | R: Restart | Esc: Exit", True, (255, 255, 255))
        screen.blit(help_text, (WIDTH - help_text.get_width() - 10, HEIGHT - 30))

    if game_state_for_mods:
        modloader.trigger_on_draw(screen, game_state_for_mods)

def getSettings(key: str) -> Optional[str]:
    settings = {}
    settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
    with open(settings_path) as f:
        for line in f:
            if "=" in line:
                k, value = line.strip().split("=", 1)
                settings[k] = value
    return settings.get(key)

def reloadSettings():
    global scrollPixelsPerFrame, jumpVelocity, font, maxfps, speed_increase, difficulty, game_mode
    def _get_int_setting(key: str, default: int) -> int:
        val = getSettings(key)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            print(f"Invalid integer for {key}: {val}. Using default {default}.", flush=True)
            return default

    def _get_float_setting(key: str, default: float) -> float:
        val = getSettings(key)
        if val is None:
            return default
        try:
            return float(val)
        except ValueError:
            print(f"Invalid float for {key}: {val}. Using default {default}.", flush=True)
            return default

    scrollPixelsPerFrame = _get_int_setting("scrollPixelsPerFrame", 2)
    jumpVelocity = _get_int_setting("jumpVelocity", 12)
    maxfps = _get_int_setting("maxFps", 60)
    font = pygame.font.Font(dependencies.get_font_path(), 36)
    rememberName = getSettings("rememberName") == "True"
    speed_increase = _get_float_setting("speed_increase", 3.0)
    difficulty = getSettings("difficulty") or "Normal"
    game_mode = getSettings("game_mode") or "Classic"
    

def appendScore(score):
    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    with open(scores_path, "a") as f:
        f.write(f"{score}\n")

def run_ui_overlay(title, info_lines, button_defs, title_color=(255, 255, 255), hook_func=None, on_esc=None, on_enter=None, per_frame_callback=None):
    global WIDTH, HEIGHT, screen, clock, root
    
    if hook_func:
        hook_func(None)
        
    title_font = pygame.font.Font(dependencies.get_font_path(), 64)
    info_font = pygame.font.Font(dependencies.get_font_path(), 32)

    while True:
        if per_frame_callback:
            res = per_frame_callback()
            if res: return res
            
        render_game()
        
        dim_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_overlay.fill((0, 0, 0, 150))
        screen.blit(dim_overlay, (0, 0))
        
        box_width = 450
        box_height = 120 + len(info_lines) * 40 + len(button_defs) * 55 + 20
        box_rect = pygame.Rect(WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2, box_width, box_height)
        
        pygame.draw.rect(screen, (30, 30, 40), box_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, width=2, border_radius=20)
        
        title_surf = title_font.render(title, True, title_color)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, box_rect.top + 60))
        screen.blit(title_surf, title_rect)
        
        curr_y = box_rect.top + 120
        for line in info_lines:
            info_surf = info_font.render(line, True, (255, 255, 255))
            info_rect = info_surf.get_rect(center=(WIDTH // 2, curr_y))
            screen.blit(info_surf, info_rect)
            curr_y += 40
            
        btn_width = 320
        btn_height = 45
        if info_lines: curr_y += 10
        
        buttons = []
        for b_def in button_defs:
            btn = Button(b_def[0], WIDTH // 2 - btn_width // 2, curr_y, btn_width, btn_height, b_def[1], b_def[2], b_def[3])
            btn.draw(screen)
            buttons.append(btn)
            curr_y += 55
            
        pygame.display.update()
        
        size_changed = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            if event.type == pygame.VIDEORESIZE:
                WIDTH, HEIGHT = event.w, event.h
                size_changed = True
            elif event.type == pygame.WINDOWRESIZED:
                WIDTH, HEIGHT = event.x, event.y
                size_changed = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and on_esc:
                    res = on_esc()
                    if res: return res
                if event.key == pygame.K_RETURN and on_enter:
                    res = on_enter()
                    if res: return res
            
            for btn in buttons:
                res = btn.is_clicked(event)
                if res:
                    return res
        
        if size_changed:
            current_w, current_h = pygame.display.get_surface().get_size()
            if WIDTH != current_w or HEIGHT != current_h:
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        
        try:
            root.update()
        except:
            pass
        clock.tick(60)

def show_lose_screen():
    global points, name, replaying, current_seed, current_recording, replay_config, mp_client, mp_server
    
    def on_restart(): return "restart"
    def on_exit(): return "exit"
    def on_leaderboard():
        scores.start_public(root)
        return None
    def on_save_replay():
        replays.save_replay(current_seed, current_recording, points, name, replay_config)
        return "restart"
    def on_ready():
        if mp_client:
            mp_client.send_ready(True)
        return None
    def on_stop_server():
        global mp_client, mp_server
        if mp_server:
            mp_server.stop()
            mp_server = None
        if mp_client:
            mp_client.disconnect()
            mp_client = None
        return "exit"

    button_defs = [
        ("Restart", (46, 204, 113), (39, 174, 96), on_restart),
        ("Leaderboard", (52, 152, 219), (41, 128, 185), on_leaderboard),
        ("Exit", (231, 76, 60), (192, 57, 43), on_exit),
    ]
    
    if mp_client:
        button_defs.insert(0, ("Ready Up", (46, 204, 113), (39, 174, 96), on_ready))
        
    if mp_server:
        button_defs.append(("Stop Server", (231, 76, 60), (192, 57, 43), on_stop_server))
    
    if not replaying:
        button_defs.append(("Save Replay", (155, 89, 182), (142, 68, 173), on_save_replay))

    def lose_callback():
        if mp_client and mp_client.should_start_game:
            mp_client.should_start_game = False
            return "restart"
        return None

    return run_ui_overlay(
        title="YOU LOST!",
        info_lines=[f"Final Score: {points}"],
        button_defs=button_defs,
        title_color=(255, 80, 80),
        hook_func=modloader.trigger_on_lose_screen,
        on_esc=on_exit,
        on_enter=on_restart,
        per_frame_callback=lose_callback
    )

def show_pause_screen():
    global mp_server, mp_client
    def on_resume(): return "resume"
    def on_exit(): return "exit"
    def on_scores():
        scores.start(root)
        return None
    def on_leaderboard():
        scores.start_public(root)
        return None
    def on_settings():
        import options
        options.start(root)
        return None
    def on_update():
        import updater
        import sys
        game_executable_path = sys.argv[0]
        updater.start_update(game_executable_path)
        return "exit"
    def on_stop_server():
        global mp_client, mp_server
        if mp_server:
            mp_server.stop()
            mp_server = None
        if mp_client:
            mp_client.disconnect()
            mp_client = None
        return "exit"

    button_defs = [
        ("Resume", (46, 204, 113), (39, 174, 96), on_resume),
        ("Scores", (52, 152, 219), (41, 128, 185), on_scores),
        ("Leaderboard", (52, 152, 219), (41, 128, 185), on_leaderboard),
        ("Settings", (155, 89, 182), (142, 68, 173), on_settings),
        ("Update", (230, 126, 34), (211, 84, 0), on_update),
        ("Exit", (231, 76, 60), (192, 57, 43), on_exit),
    ]
    
    if mp_server:
        button_defs.append(("Stop Server", (231, 76, 60), (192, 57, 43), on_stop_server))

    return run_ui_overlay(
        title="PAUSED",
        info_lines=[],
        button_defs=button_defs,
        title_color=(255, 255, 255),
        hook_func=modloader.trigger_on_pause_screen,
        on_esc=on_resume,
        on_enter=on_resume
    )

def show_multiplayer_menu():
    def on_add(): return "add"
    def on_create(): return "create"
    def on_back(): return "back"

    button_defs = [
        ("Add Server", (46, 204, 113), (39, 174, 96), on_add),
        ("Create Server", (52, 152, 219), (41, 128, 185), on_create),
        ("Back", (231, 76, 60), (192, 57, 43), on_back),
    ]

    return run_ui_overlay(
        title="Multiplayer",
        info_lines=["Connect to a server or host one!"],
        button_defs=button_defs,
        on_esc=on_back
    )

def show_lobby_screen(client, is_admin):
    global mp_server, mp_client
    
    def on_start():
        if is_admin:
            client.admin_start()
        return None
        
    def on_back():
        global mp_client, mp_server
        client.disconnect()
        if mp_server:
            mp_server.stop()
            mp_server = None
        mp_client = None
        return "back"

    def lobby_callback():
        global mp_client, mp_server
        if client.should_start_game:
            client.should_start_game = False
            return "start"
            
        if client.connection_error or client.was_kicked:
            client.disconnect()
            mp_client = None
            if mp_server:
                mp_server.stop()
                mp_server = None
            return "kicked"
        return None

    while True:
        player_names = [p["name"] for p in client.remote_players.values()]
        player_names.insert(0, client.name + " (You)")
        info_lines = [f"Players connected: {len(player_names)}"] + player_names[:5]

        button_defs = []
        if is_admin:
            button_defs.append(("Start Game", (46, 204, 113), (39, 174, 96), on_start))
        button_defs.append(("Disconnect", (231, 76, 60), (192, 57, 43), on_back))

        res = run_ui_overlay(
            title="Lobby",
            info_lines=info_lines,
            button_defs=button_defs,
            on_esc=on_back,
            per_frame_callback=lobby_callback
        )
        if res: return res

def get_text_input(title, text):
    global root
    # Create a small modal-like window without the strict 'grab_set' that fails on some Linux distros
    input_window = ctk.CTkToplevel(root)
    input_window.title(title)
    input_window.geometry("300x150")
    input_window.attributes("-topmost", True)
    
    # Position it near the center of the screen
    input_window.update_idletasks()
    
    result = {"value": None}
    
    label = ctk.CTkLabel(input_window, text=text)
    label.pack(pady=10)
    
    entry = ctk.CTkEntry(input_window)
    entry.pack(pady=5)
    entry.focus_set()
    
    def on_submit():
        result["value"] = entry.get()
        input_window.destroy()

    btn = ctk.CTkButton(input_window, text="OK", command=on_submit)
    btn.pack(pady=10)
    
    input_window.bind("<Return>", lambda e: on_submit())
    input_window.bind("<Escape>", lambda e: input_window.destroy())
    
    input_window.wait_window()
    return result["value"]

def handle_multiplayer():
    global name, root, mp_client, mp_server
    
    while True:
        choice = show_multiplayer_menu()
        if choice == "back" or choice == "kicked":
            return None
            
        if choice == "add":
            server_addr = get_text_input("Join Server", "Enter server address (IP:Port):")
            if server_addr:
                if ":" in server_addr:
                    try:
                        host, port = server_addr.split(":")
                        port = int(port)
                    except:
                        host, port = server_addr, multiplayer.DEFAULT_PORT
                else:
                    host, port = server_addr, multiplayer.DEFAULT_PORT
                
                client = multiplayer.GameClient(host, port, name)
                if client.connect():
                    mp_client = client
                    res = show_lobby_screen(client, False)
                    if res == "start":
                         return "start"
                else:
                    pass
                    
        elif choice == "create":
            port_str = get_text_input("Create Server", f"Enter port (default {multiplayer.DEFAULT_PORT}):")
            port = int(port_str) if port_str and port_str.isdigit() else multiplayer.DEFAULT_PORT
            
            srv = multiplayer.GameServer(port=port, admin_name=name)
            srv.start()
            mp_server = srv
            
            client = multiplayer.GameClient("127.0.0.1", port, name)
            if client.connect():
                mp_client = client
                res = show_lobby_screen(client, True)
                if res == "start":
                    return "start"
            else:
                srv.stop()
                mp_server = None

def show_main_menu():
    def on_start(): return "start"
    def on_exit(): return "exit"
    def on_settings():
        options.start(root)
        return None
    def on_scores():
        scores.start(root)
        return None
    def on_public_leaderboard():
        scores.start_public(root)
        return None
    def on_replays():
        replay_data = replays.start(root)
        if replay_data:
            return ("replay", replay_data)
        return None
    def on_multiplayer():
        return "multiplayer"
    def on_achievements():
        achievements.show_achievements_gui(root)
        return None

    button_defs = [
        ("Start Game", (46, 204, 113), (39, 174, 96), on_start),
        ("Multiplayer", (155, 89, 182), (142, 68, 173), on_multiplayer),
        ("Achievements", (255, 215, 0), (218, 165, 32), on_achievements),
        ("Settings", (155, 89, 182), (142, 68, 173), on_settings),
        ("Scores", (52, 152, 219), (41, 128, 185), on_scores),
        ("Leaderboard", (52, 152, 219), (41, 128, 185), on_public_leaderboard),
        ("Replays", (230, 126, 34), (211, 84, 0), on_replays),
        ("Exit", (231, 76, 60), (192, 57, 43), on_exit),
    ]

    return run_ui_overlay(
        title="Skakavi Krompir",
        info_lines=[],
        button_defs=button_defs,
        hook_func=modloader.trigger_on_main_menu,
        on_esc=on_exit,
        on_enter=on_start
    )


################################################
##################### Init #####################
################################################

import customtkinter as ctk

# Create a hidden root window
root = ctk.CTk()
root.withdraw()

HEIGHT = 600
WIDTH = 800
pygame.init()
modloader.load_mods()
font = pygame.font.Font(dependencies.get_font_path(), 36)
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
pygame.display.set_icon(image)

powerup_manager = powerups.PowerupManager(dependencies.get_assets_dir())

# Basic setup needed for background rendering in main menu
# restart() will do a full reset later, but we need it once here.
restart()

rememberName = getSettings("rememberName") == "True"

if rememberName:
    name = getSettings("name")
else:
    name = namecheck.getname(root)

initial_replay = None
while True:
    menu_res = show_main_menu()
    if menu_res == "exit":
        sys.exit()
    elif menu_res == "multiplayer":
        res = handle_multiplayer()
        if res == "start":
            break
    elif menu_res == "start":
        break
    elif isinstance(menu_res, tuple) and menu_res[0] == "replay":
        initial_replay = menu_res[1]
        break

################################################
################### Main Loop ##################
################################################

restart(initial_replay)
running = True
just_resumed = False

dump_status("Playing", points, "playing")

while running:
    try:
        root.update()
        root.update_idletasks()
    except:
        pass
    jump_this_frame = False
    size_changed = False
    for event in pygame.event.get():
        modloader.trigger_on_event(event)
        if event.type == pygame.QUIT:
            modloader.trigger_on_quit()
            running = False
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            size_changed = True
        elif event.type == pygame.WINDOWRESIZED:
            WIDTH, HEIGHT = event.x, event.y
            size_changed = True
        if event.type == pygame.KEYDOWN and not paused and not dying:
            if event.key == pygame.K_ESCAPE:
                paused = True
                dump_status("Paused", points, "paused")
                afterpause = show_pause_screen()
                if afterpause == "exit":
                    running = False
                elif afterpause == "resume":
                    # If potato is in a losing state, show lose screen immediately
                    angle = max(min(velocity * -2.5, 30), -90)
                    rotated_image_on_resume = pygame.transform.rotate(image, angle)
                    rotated_rect_on_resume = rotated_image_on_resume.get_rect(center=image.get_rect(topleft=(x, y)).center)
                    if y > HEIGHT or y < 0 or isPotatoColliding(rotated_image_on_resume, rotated_rect_on_resume):
                        if replaying:
                            # Replay ended prematurely via pause-resume? Just go back to menu
                            menu_res = show_main_menu()
                            if menu_res == "exit":
                                running = False
                            else:
                                rep = None
                                if isinstance(menu_res, tuple) and menu_res[0] == "replay":
                                    rep = menu_res[1]
                                restart(rep)
                                paused = False
                        else:
                            rotated_image, rotated_rect = rotated_image_on_resume, rotated_rect_on_resume
                            appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
                            scores.submit_score(name, points)
                            reloadSettings()
                            afterpause2 = show_lose_screen()
                            if afterpause2 == "exit":
                                running = False
                            elif afterpause2 == "restart":
                                restart()
                                paused = False
                    else:
                        velocity = 0
                        clock.tick(maxfps)  # Reset clock to avoid large delta
                        just_resumed = True
                        paused = False
            elif event.key == pygame.K_SPACE and not replaying:
                jump_this_frame = True
            elif replaying:
                if event.key == pygame.K_p:
                    replay_paused = not replay_paused
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    replay_speed = min(4.0, replay_speed + 0.5)
                elif event.key == pygame.K_MINUS:
                    replay_speed = max(0.1, replay_speed - 0.5)
                elif event.key == pygame.K_r:
                    restart(current_replay_data)
        if event.type == pygame.MOUSEBUTTONDOWN and not paused and not dying:
            if replaying:
                # Scrubbing logic
                mx, my = event.pos
                if HEIGHT - 55 <= my <= HEIGHT - 35:
                    bar_width = WIDTH - 40
                    if 20 <= mx <= WIDTH - 20:
                        rel_x = (mx - 20) / bar_width
                        target_f = int(rel_x * len(current_replay_data["frames"]))
                        seek_to_frame(target_f)
            elif not replaying:
                jump_this_frame = True

    if jump_this_frame:
         modloader.trigger_on_jump()
         velocity = -jumpVelocity
         # Create jump particles at the bottom center of the player
         # Player size is approx 78x58. Center is x + 39. Bottom is y + 58.
         particle_manager.create_jump_effect(x + 39, y + 58)

    if size_changed:
        current_w, current_h = pygame.display.get_surface().get_size()
        if WIDTH != current_w or HEIGHT != current_h:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    if not paused:
        if mp_client:
            # Sync our position to others
            # 'angle' is calculated later in the frame, let's use the current one or calculate it here
            calc_angle = max(min(velocity * -2.5, 30), -90)
            if dying:
                 calc_angle = (pygame.time.get_ticks() // 5) % 360
            mp_client.send_update(x, y, calc_angle, not dying, points)
            
            # If server sent a forced restart (e.g. game started while we were in a game)
            if mp_client.should_start_game:
                mp_client.should_start_game = False
                restart()
                
            if mp_client.connection_error or mp_client.was_kicked:
                 # Local disconnect handling
                 mp_client.disconnect()
                 mp_client = None
                 if mp_server:
                      mp_server.stop()
                      mp_server = None

        if replaying:
            if replay_paused:
                delta = 0
            else:
                if frame_index < len(current_replay_data["frames"]):
                    frame = current_replay_data["frames"][frame_index]
                    delta = frame["delta"] * replay_speed
                    # We want to skip frames if speed > 1, but for simplicity we'll just scale delta
                    # Wait, if I scale delta, the potato moves faster but we only consume 1 frame per tick.
                    # This means we spend the same number of ticks to play the replay, but it looks faster.
                    # This is actually fine for simple playback!
                    
                    if frame["jump"]:
                        modloader.trigger_on_jump()
                        velocity = -jumpVelocity
                        particle_manager.create_jump_effect(x + 39, y + 58)
                    
                    if frame.get("powerup"):
                        # Just a marker for now, powerup logic still runs based on position
                        pass
                        
                    frame_index += 1
                else:
                    # Replay finished, just continue physics or end?
                    # For now keep it as is
                    delta = clock.tick(maxfps) / 1000
        else:
            if just_resumed:
                delta = clock.tick(maxfps) / 1000
                just_resumed = False
            else:
                delta = clock.get_time() / 1000
            
            # Recording moved to end of loop to capture all events
            pass

        velocity += 0.5 * delta * 60
        if not dying:
            pass # Powerup logic moved to after rotation to ensure rotated_rect is available
            
        y += velocity * delta * 60
        particle_manager.update(delta)
        clock.tick(maxfps)

        if not dying:
            if (-scroll // PIPE_SPACING) < 0:
                new_points = 0
            else:
                new_points = int(-scroll // PIPE_SPACING + 1)
            
            if new_points > points:
                modloader.trigger_on_score(new_points)
            points = new_points
                
            # make the speed go faster over time
            if points % 10 == 0 and points != 0:
                scrollPixelsPerFrame += speed_increase * 0.01 * delta * 60
        
        # --- Rotation and Drawing ---
        if dying:
            # Spinner rotation on death
            angle = (pygame.time.get_ticks() // 5) % 360
        else:
            angle = max(min(velocity * -2.5, 30), -90)
            
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)

        if not dying:
            # Powerup updates and effects
            # Now rotated_rect is valid for this frame
            collected_effect, expired_effects = powerup_manager.update(delta, scroll, rotated_rect)
            
            if collected_effect:
                powerups_collected_this_run += 1
                achievement_manager.update_stat("total_powerups", 1)
                achievement_manager.update_stat("powerups_in_run", powerups_collected_this_run, incremental=False)
                # Handle instant effects
                p_text = ""
                p_color = (255, 255, 255)
                
                if collected_effect["type"] == "score":
                    val = collected_effect["value"]
                    points += val
                    modloader.trigger_on_score(points)
                    p_text = f"+{val}"
                    p_color = (255, 215, 0)
                elif collected_effect["type"] == "invincibility":
                    p_text = "SHIELD!"
                    p_color = (0, 255, 255)
                elif collected_effect["type"] == "speed":
                    val = collected_effect["value"]
                    if val > 1:
                        p_text = "SPEED UP!"
                        p_color = (255, 50, 50)
                    else:
                        p_text = "SLOW MO!"
                        p_color = (100, 100, 255)
                        
                if p_text:
                    floating_texts.append(FloatingText(p_text, rotated_rect.centerx, rotated_rect.top - 20, p_color))
            
            # Record powerup collection for replay
            if collected_effect and not replaying:
                if current_recording:
                    current_recording[-1]["powerup"] = True
            
            # Remove expired floating texts
            floating_texts = [ft for ft in floating_texts if ft.update()]
            
            # Speed boost / Slow motion
            speed_multiplier = 1.0
            if powerup_manager.is_effect_active("speed"):
                 speed_multiplier = powerup_manager.get_effect_value("speed", 1.0)

            # Apply speed effects
            base_scroll_change = scrollPixelsPerFrame * delta * 60 * speed_multiplier
            
            scroll -= base_scroll_change

        # Update mod-accessible game state if not dying
        if not dying:
            game_state_for_mods = {
                "player_pos": (x, y),
                "player_velocity": velocity,
                "player_rect": rotated_rect,
                "player_surface": rotated_image,
                "pipes": pipesPos,
                "scroll": scroll,
                "width": WIDTH,
                "height": HEIGHT,
                "points": points,
                "pipe_spacing": PIPE_SPACING,
                "pipe_color": pipeColor
            }
            modloader.update_game_state(game_state_for_mods)

            # Trigger mod hooks
            modloader.trigger_on_update(delta)
            
            # Record this frame if not replaying and not dying
            if not replaying and not dying:
                current_recording.append({
                    "delta": delta,
                    "jump": jump_this_frame,
                    "powerup": bool(collected_effect) if 'collected_effect' in locals() else False
                })

            # Pull state back from mods
            new_state = modloader.get_game_state()
            if new_state:
                if "player_pos" in new_state and isinstance(new_state["player_pos"], (tuple, list)) and len(new_state["player_pos"]) == 2:
                    x, y = new_state["player_pos"]
                if "player_velocity" in new_state:
                    velocity = new_state["player_velocity"]
                if "scroll" in new_state:
                    scroll = new_state["scroll"]
                if "points" in new_state:
                    points = new_state["points"]
                if "pipe_color" in new_state:
                    pipeColor = new_state["pipe_color"]

        render_game()

        # --- Collision and State Transitions ---
        if not dying:
            if game_mode == "Zen":
                collision_detected = False
            else:
                collision_detected = y > HEIGHT or y < 0 or isPotatoColliding(rotated_image, rotated_rect)
                
            if game_mode == "Time Attack":
                time_left -= delta
                if time_left <= 0:
                    collision_detected = True
                    time_left = 0
            
            if collision_detected:
                if not modloader.trigger_on_collision():
                     collision_detected = False
            
            if collision_detected:
                dying = True
                achievement_manager.update_stat("high_score", points, incremental=False)
                if game_mode == "Zen":
                    achievement_manager.update_stat("zen_high_score", points, incremental=False)
                velocity = -8 # Small jump up on death
                particle_manager.create_collision_effect(x + 39, y + 29) # Center of player
        else:
            # When dying, wait for potato to fall off screen
            if y > HEIGHT + 100:
                if replaying:
                    # Replay ended (either finished or crashed)
                    menu_res = show_main_menu()
                    if menu_res == "exit":
                        running = False
                    else:
                        rep = None
                        if isinstance(menu_res, tuple) and menu_res[0] == "replay":
                            rep = menu_res[1]
                        restart(rep)
                        paused = False
                else:
                    paused = True
                    appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
                    scores.submit_score(name, points)
                    reloadSettings()
                    afterpause = show_lose_screen()
                    if afterpause == "exit":
                        running = False
                    elif afterpause == "restart":
                        restart()
                        paused = False
                    
        pygame.display.update()

pygame.quit()
dump_status("Stopped", points, "stopped")
