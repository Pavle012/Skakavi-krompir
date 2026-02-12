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
import gui
import scores
import random
import namecheck
import modloader
import datetime
import os
import replays
from typing import Optional

paused = False  # initialize before use because of type checking
x = 100         # default x (restart() will overwrite)
y = 0           # default y (restart() will overwrite)
points = 0      # default points (restart() will overwrite)
velocity = 0    # etc.
scroll = 500
speed_increase = 3
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


def restart(replay_data=None):
    global scrollPixelsPerFrame, jumpVelocity, velocity, x, y, maxfps, clock, paused, points, text_str, text, pipeNumber, scroll, PIPE_SPACING, pipesPos, pipeColor, image, WIDTH, HEIGHT, dying
    global replaying, current_replay_data, current_recording, frame_index, current_seed, replay_config, speed_increase
    
    reloadSettings()
    
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
    else:
        replaying = False
        current_replay_data = None
        current_recording = []
        frame_index = 0
        current_seed = int(time.time() * 1000)
        replay_config = {
            "scrollPixelsPerFrame": scrollPixelsPerFrame,
            "jumpVelocity": jumpVelocity,
            "speed_increase": speed_increase
        }
    
    random.seed(current_seed)
    
    dying = False
    velocity = 0
    x = 100
    y = (HEIGHT // 2)
    maxfps = 60
    clock = pygame.time.Clock()
    paused = False
    points = 0
    text_str = f"Points: {points}"
    text = font.render(text_str, True, (255, 255, 255))
    pipeNumber = 500
    scroll = 500
    PIPE_SPACING = 300
    GAP_SIZE = 300
    pipesPos = []
    pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for i in range(pipeNumber):
        randomY = random.randint(-100, 100)
        pipesPos.append((100 + (i * PIPE_SPACING), (HEIGHT/2) + GAP_SIZE + -750 + randomY, True))
        pipesPos.append((100 + (i * PIPE_SPACING), (HEIGHT/2) + GAP_SIZE + -150 + randomY, False))
    
    # Reload the image in case it was changed
    image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
    image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
    modloader.trigger_on_restart()


def isPotatoColliding(potato_surface, potato_rect):
    global pipesPos, scroll
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
    global screen, WIDTH, HEIGHT, rotated_image, rotated_rect, points, font, game_state_for_mods
    screen.fill((66, 183, 237))
    spawnPipe()
    if rotated_image and rotated_rect:
        screen.blit(rotated_image, rotated_rect.topleft)
    
    points_text = font.render(f"Points: {points}", True, (255, 255, 255))
    screen.blit(points_text, (WIDTH - points_text.get_width() - 10, 10))
    
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
    global scrollPixelsPerFrame, jumpVelocity, font, maxfps, speed_increase
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
    

def appendScore(score):
    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    with open(scores_path, "a") as f:
        f.write(f"{score}\n")

def show_lose_screen():
    global running, paused, points, name, WIDTH, HEIGHT, screen, rotated_image, rotated_rect
    
    lose_font = pygame.font.Font(dependencies.get_font_path(), 64)
    info_font = pygame.font.Font(dependencies.get_font_path(), 32)
    
    def on_restart():
        return "restart"
    
    def on_exit():
        return "exit"
    
    def on_leaderboard():
        scores.start_public(root)
        return None

    def on_save_replay():
        if not replaying:
            replays.save_replay(current_seed, current_recording, points, name, replay_config)
            return "restart" # Restart after saving? Or just stay? Restart for now.
        return None

    modloader.trigger_on_lose_screen(None)

    while True:
        # 1. Draw the game state as the background
        render_game()
        
        # 2. Draw a semi-transparent full-screen dim
        dim_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        dim_overlay.fill((0, 0, 0, 120))
        screen.blit(dim_overlay, (0, 0))
        
        # 3. Draw a centered box for the UI
        box_width = 450
        box_height = 400
        box_rect = pygame.Rect(WIDTH // 2 - box_width // 2, HEIGHT // 2 - box_height // 2, box_width, box_height)
        
        # Rounded box with border
        pygame.draw.rect(screen, (30, 30, 40), box_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 255, 255), box_rect, width=2, border_radius=20)
        
        lose_text = lose_font.render("YOU LOST!", True, (255, 80, 80))
        lose_rect = lose_text.get_rect(center=(WIDTH // 2, box_rect.top + 60))
        screen.blit(lose_text, lose_rect)
        
        score_info = info_font.render(f"Final Score: {points}", True, (255, 255, 255))
        score_rect = score_info.get_rect(center=(WIDTH // 2, box_rect.top + 130))
        screen.blit(score_info, score_rect)
        
        # Buttons shifted relative to the box
        btn_width = 300
        btn_height = 50
        start_y = box_rect.top + 180
        
        buttons = [
            Button("Restart", WIDTH // 2 - btn_width // 2, start_y, btn_width, btn_height, (46, 204, 113), (39, 174, 96), on_restart),
            Button("Leaderboard", WIDTH // 2 - btn_width // 2, start_y + 60, btn_width, btn_height, (52, 152, 219), (41, 128, 185), on_leaderboard),
            Button("Exit", WIDTH // 2 - btn_width // 2, start_y + 120, btn_width, btn_height, (231, 76, 60), (192, 57, 43), on_exit),
        ]
        
        if not replaying:
            buttons.append(Button("Save Replay", WIDTH // 2 - btn_width // 2, start_y + 180, btn_width, btn_height, (155, 89, 182), (142, 68, 173), on_save_replay))
            box_height = 460
            box_rect.height = box_height
            box_rect.y = HEIGHT // 2 - box_height // 2

        for btn in buttons:
            btn.draw(screen)
            
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
                if event.key == pygame.K_RETURN:
                    return "restart"
                if event.key == pygame.K_ESCAPE:
                    return "exit"
            
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

################################################
##################### Init #####################
################################################

import customtkinter as ctk

# Create a hidden root window
root = ctk.CTk()
root.withdraw()

rememberName = getSettings("rememberName") == "True"

if rememberName:
    name = getSettings("name")
else:
    name = namecheck.getname(root)

menu_res = gui.main_menu(root)
if menu_res == "exit":
    sys.exit()

initial_replay = None
if isinstance(menu_res, tuple) and menu_res[0] == "replay":
    initial_replay = menu_res[1]
    
HEIGHT = 400
WIDTH = 800
pygame.init()
modloader.load_mods()
font = pygame.font.Font(dependencies.get_font_path(), 36)
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
pygame.display.set_icon(image)

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
                afterpause = gui.pause_screen(root)
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
                            menu_res = gui.main_menu(root)
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
        if event.type == pygame.MOUSEBUTTONDOWN and not paused and not dying and not replaying:
            jump_this_frame = True

    if jump_this_frame:
         modloader.trigger_on_jump()
         velocity = -jumpVelocity

    if size_changed:
        current_w, current_h = pygame.display.get_surface().get_size()
        if WIDTH != current_w or HEIGHT != current_h:
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

    if not paused:
        if replaying:
            if frame_index < len(current_replay_data["frames"]):
                frame = current_replay_data["frames"][frame_index]
                delta = frame["delta"]
                if frame["jump"]:
                    modloader.trigger_on_jump()
                    velocity = -jumpVelocity
                frame_index += 1
            else:
                # Replay finished, just continue physics
                delta = clock.tick(maxfps) / 1000
        else:
            if just_resumed:
                delta = clock.tick(maxfps) / 1000
                just_resumed = False
            else:
                delta = clock.get_time() / 1000
            
            # Record this frame if not replaying and not dying
            if not dying:
                current_recording.append({
                    "delta": delta,
                    "jump": jump_this_frame
                })

        velocity += 0.5 * delta * 60
        if not dying:
            scroll -= scrollPixelsPerFrame * delta * 60
        y += velocity * delta * 60
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
            collision_detected = y > HEIGHT or y < 0 or isPotatoColliding(rotated_image, rotated_rect)
            if collision_detected:
                if not modloader.trigger_on_collision():
                     collision_detected = False
            
            if collision_detected:
                dying = True
                velocity = -8 # Small jump up on death
        else:
            # When dying, wait for potato to fall off screen
            if y > HEIGHT + 100:
                if replaying:
                    # Replay ended (either finished or crashed)
                    menu_res = gui.main_menu(root)
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
