import pygame_gui
import sys
import dependencies
from dependencies import is_compiled

if not is_compiled():
    dependencies.checkifdepend()
    dependencies.fetch_assets()
dependencies.install_configs()
dependencies.load_global_icon_pil()

import pygame
import gui
import scores
import random
import namecheck
import datetime
import os
from typing import Optional

paused = False  # initialize before use because of type checking
x = 100         # default x (restart() will overwrite)
y = 0           # default y (restart() will overwrite)
points = 0      # default points (restart() will overwrite)
velocity = 0    # etc.
scroll = 500
speed_increase = 3

###############################################
############ Flappy Bird-like Game ############
###############################################

################################################
################### Classes ####################
################################################
class pipe:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self, screen):
        pygame.draw.rect(screen, pipeColor, (self.x, self.y, 50, 300))

################################################
################### Functions ##################
################################################


def restart():
    global scrollPixelsPerFrame, jumpVelocity, velocity, x, y, maxfps, clock, paused, points, text_str, text, pipeNumber, scroll, PIPE_SPACING, pipesPos, pipeColor, image
    reloadSettings()
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
    pipesPos = []
    pipeColor = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    for i in range(pipeNumber):
        randomY = random.randint(-100, 100)
        pipesPos.append((100 + (i * PIPE_SPACING), 0 + randomY))
        pipesPos.append((100 + (i * PIPE_SPACING), 600 + randomY))
    
    # Reload the image in case it was changed
    image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
    image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))


def isPotatoColliding(potato_surface, potato_rect):
    global pipesPos, scroll
    # Create a mask from the rotated potato surface.
    potato_mask = pygame.mask.from_surface(potato_surface)

    # Iterate over each pipe.
    for px, py in pipesPos:
        realX = px + scroll
        pipe_rect = pygame.Rect(realX, py, 50, 300)

        # First, a simple and fast bounding box check to see if they are even close.
        if not potato_rect.colliderect(pipe_rect):
            continue

        # If the bounding boxes overlap, perform a more accurate (and slower) pixel-perfect collision check.
        # Create a mask for the pipe (a simple filled rectangle).
        pipe_mask = pygame.mask.Mask((50, 300), fill=True)
        
        # Calculate the offset between the potato and the pipe. This is the relative position
        # of the pipe's top-left corner from the potato's top-left corner.
        offset = (pipe_rect.x - potato_rect.x, pipe_rect.y - potato_rect.y)

        # Check for overlap between the masks.
        if potato_mask.overlap(pipe_mask, offset):
            return True # Collision detected

    return False # No collision


def spawnPipe():
    global pipesPos, scroll, pipeColor, screen
    for px, py in pipesPos:
        realX = px + scroll
        pipe(realX, py).draw(screen)

def reloadSettings():
    global scrollPixelsPerFrame, jumpVelocity, font, maxfps, speed_increase
    def _get_int_setting(key: str, default: int) -> int:
        val = dependencies.getSettings(key)
        if val is None:
            return default
        try:
            return int(val)
        except ValueError:
            print(f"Invalid integer for {key}: {val}. Using default {default}.", flush=True)
            return default

    scrollPixelsPerFrame = _get_int_setting("scrollPixelsPerFrame", 2)
    jumpVelocity = _get_int_setting("jumpVelocity", 12)
    maxfps = _get_int_setting("maxFps", 60)
    font = pygame.font.Font(dependencies.get_font_path(), 36)
    rememberName = dependencies.getSettings("rememberName") == "True"
    speed_increase = _get_int_setting("speed_increase", 3)
    

def appendScore(score):
    scores_path = os.path.join(dependencies.get_user_data_dir(), "scores.txt")
    with open(scores_path, "a") as f:
        f.write(f"{score}\n")

################################################
##################### Init #####################
################################################

# --- Game State Setup ---
# We use a simple string-based state machine
game_state = "STARTUP"
previous_game_state = "STARTUP"
name = ""

rememberName = dependencies.getSettings("rememberName") == "True"
if rememberName:
    name = dependencies.getSettings("name")
    if name:
        game_state = "MAIN_MENU"
    else:
        game_state = "NAME_CHECK"
else:
    game_state = "NAME_CHECK"
    
HEIGHT = 800
WIDTH = 1200
pygame.init()
font = pygame.font.Font(dependencies.get_font_path(), 36)
pygame.display.set_caption("skakavi krompir")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
image = pygame.image.load(dependencies.get_potato_path()).convert_alpha()
image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
pygame.display.set_icon(image)

# Pygame GUI Manager
manager = pygame_gui.UIManager((WIDTH, HEIGHT))


################################################
################### Main Loop ##################
################################################

restart()
running = True
just_resumed = False

# Keep track of the last angle for smooth pause/unpause visuals
angle = 0

while running:
    time_delta = clock.get_time() / 1000.0

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        manager.process_events(event)

        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # --- Name Check Events ---
            if game_state == "NAME_CHECK" and '@name_save_button' in event.ui_object_id:
                name = gui.name_entry_box.get_text()
                remember = gui.remember_name_checkbox.is_selected
                
                dependencies.setSettings("name", name)
                dependencies.setSettings("rememberName", remember)

                gui.close_name_input_window()
                game_state = "MAIN_MENU" # Transition to main menu

            # --- Main Menu Events ---
            if game_state == "MAIN_MENU":
                if '@main_menu_start_button' in event.ui_object_id:
                    gui.close_main_menu_window()
                    game_state = "PLAYING"
                    restart() # Restart game before playing
                elif '@main_menu_exit_button' in event.ui_object_id:
                    running = False
                elif '@main_menu_settings_button' in event.ui_object_id:
                    previous_game_state = game_state
                    game_state = "OPTIONS"
                    gui.create_options_window(manager)
                elif '@main_menu_scores_button' in event.ui_object_id:
                    scores.create_scores_window(manager)
                elif '@main_menu_public_leaderboard_button' in event.ui_object_id:
                    scores.create_public_leaderboard_window(manager)


            # --- Pause Menu Events ---
            elif game_state == "PAUSED":
                if '@pause_resume_button' in event.ui_object_id:
                    game_state = "PLAYING"
                    gui.close_pause_screen()
                    velocity = 0
                    clock.tick(maxfps)
                    just_resumed = True
                elif '@pause_quit_button' in event.ui_object_id:
                    running = False
                elif '@pause_scores_button' in event.ui_object_id:
                    scores.create_scores_window(manager)
                elif '@pause_public_leaderboard_button' in event.ui_object_id:
                    scores.create_public_leaderboard_window(manager)
                elif '@pause_settings_button' in event.ui_object_id:
                    previous_game_state = game_state
                    game_state = "OPTIONS"
                    gui.create_options_window(manager)
                elif '@pause_update_button' in event.ui_object_id:
                    print("Update button pressed")

            # --- Game Over Events ---
            elif game_state == "GAME_OVER":
                if '@lose_restart_button' in event.ui_object_id:
                    gui.close_lose_screen()
                    restart()
                    game_state = "PLAYING"
                elif '@lose_quit_button' in event.ui_object_id:
                    running = False
                elif '@lose_public_leaderboard_button' in event.ui_object_id:
                    scores.create_public_leaderboard_window(manager)
            
            # --- Options Window Events ---
            elif game_state == "OPTIONS":
                if '@options_close_button' in event.ui_object_id:
                    gui.close_options_window()
                    game_state = previous_game_state
                elif '@options_test_button' in event.ui_object_id:
                    print("Test button pressed!")
                elif '@options_upload_font' in event.ui_object_id:
                    print("Upload Font button pressed") # Placeholder
                elif '@options_upload_image' in event.ui_object_id:
                    print("Upload Image button pressed") # Placeholder
                elif '@options_reset_settings' in event.ui_object_id:
                    print("Reset Settings button pressed") # Placeholder

        if event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED and game_state == "OPTIONS":
            slider_id = event.ui_object_id
            for key, slider in gui.sliders.items():
                if slider_id.endswith(key): # Check if the key is in the full object ID
                    value = int(event.value)
                    gui.value_labels[key].set_text(str(value))
                    dependencies.setSettings(key, value)
                    # Also update game values in real-time if needed
                    reloadSettings()

        # --- Keyboard/Mouse Events for Gameplay ---
        if game_state == "PLAYING":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    velocity = -jumpVelocity
                if event.key == pygame.K_ESCAPE:
                    game_state = "PAUSED"
                    gui.create_pause_screen(manager)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not manager.get_focus_set():
                    velocity = -jumpVelocity

    # --- Update and Draw ---
    manager.update(time_delta)

    screen.fill((66, 183, 237))

    if game_state == "NAME_CHECK":
        gui.create_name_input_window(manager)
        
    elif game_state == "MAIN_MENU":
        gui.create_main_menu_window(manager)
    
    elif game_state == "OPTIONS":
        # When in options, we might want to see the underlying screen
        if previous_game_state == "PAUSED":
            # Redraw the last game state
            rotated_image = pygame.transform.rotate(image, angle)
            rotated_rect = rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)
            spawnPipe()
            screen.blit(rotated_image, rotated_rect.topleft)
        # No need to explicitly call create_options_window here, 
        # it is created on button press and will be drawn by the manager

    elif game_state == "PLAYING":
        spawnPipe()
        if (-scroll // PIPE_SPACING) < 0:
            points = 0
        else:
            points = int(-scroll // PIPE_SPACING + 1)
        text_str = f"Points: {points}"
        text = font.render(text_str, True, (255, 255, 255))

        if just_resumed:
            just_resumed = False
        else:
            velocity += 0.5 * time_delta * 60
            scroll -= scrollPixelsPerFrame * time_delta * 60
            y += velocity * time_delta * 60

        if points % 10 == 0 and points != 0:
            scrollPixelsPerFrame += speed_increase * 0.01 * time_delta * 60
        
        angle = max(min(velocity * -2.5, 30), -90)
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)
        screen.blit(rotated_image, rotated_rect.topleft)
        
        if y > HEIGHT or y < 0 or isPotatoColliding(rotated_image, rotated_rect):
            game_state = "GAME_OVER"
            appendScore([points, name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")])
            scores.submit_score(name, points)
            reloadSettings()
            gui.create_lose_screen(manager)

    elif game_state == "PAUSED" or game_state == "GAME_OVER":
        # Redraw the last game state to keep it on screen under the menu
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rect = rotated_image.get_rect(center=image.get_rect(topleft=(x, y)).center)
        spawnPipe()
        screen.blit(rotated_image, rotated_rect.topleft)

    # UI and score text should always be on top (if not in a menu state)
    if game_state == "PLAYING":
        screen.blit(text, (WIDTH - text.get_width() - 10, 10))
    
    manager.draw_ui(screen)
    
    pygame.display.update()
    clock.tick(maxfps)

pygame.quit()
sys.exit()