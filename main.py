
# ... Imports are at the top ...
# Move imports here to ensure they are available
import pygame_gui
import sys
import asyncio
import dependencies
from dependencies import is_compiled
import pygame
import gui
import scores
import random
import namecheck
import datetime
import os
from typing import Optional

# Global variables (declared here for potential external access, but initialized in main)
paused = False
x = 100
y = 0
points = 0
velocity = 0
scroll = 500
speed_increase = 3
pipeNumber = 500
PIPE_SPACING = 300
pipesPos = []
pipeColor = (0, 0, 0)
image = None
screen = None
manager = None
clock = None
font = None

async def main():
    global paused, x, y, points, velocity, scroll, speed_increase, pipeNumber, PIPE_SPACING
    global pipesPos, pipeColor, image, screen, manager, clock, font, running, game_state
    global previous_game_state, name, just_resumed, angle, scrollPixelsPerFrame, jumpVelocity
    global maxfps, text, text_str

    print("Starting main function...", flush=True)

    try:
        if not is_compiled():
            dependencies.checkifdepend()
            dependencies.fetch_assets()
        dependencies.install_configs()
        # dependencies.load_global_icon_pil() # Skipping PIL icon load to be safe, or retry inside try block

        print("Configs installed.", flush=True)

        # --- Init ---
        HEIGHT = 800
        WIDTH = 1200
        pygame.init()
        print("Pygame initialized.", flush=True)
        
        font_path = dependencies.get_font_path()
        print(f"Loading font from {font_path}", flush=True)
        font = pygame.font.Font(font_path, 36)
        
        pygame.display.set_caption("skakavi krompir")
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        print("Display set.", flush=True)

        potato_path = dependencies.get_potato_path()
        print(f"Loading potato from {potato_path}", flush=True)
        try:
             image = pygame.image.load(potato_path).convert_alpha()
             image = pygame.transform.scale(image, (2360 // 30, 1745 // 30))
             pygame.display.set_icon(image)
        except Exception as e:
            print(f"Failed to load potato image: {e}", flush=True)
            # Create a placeholder surface if image fails
            image = pygame.Surface((50, 50))
            image.fill((255, 255, 0))

        # Pygame GUI Manager
        manager = pygame_gui.UIManager((WIDTH, HEIGHT))
        print("GUI Manager initialized.", flush=True)

        # --- Game State Setup ---
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
        
        print(f"Initial game state: {game_state}", flush=True)

        restart()
        running = True
        just_resumed = False
        angle = 0
        
        # Initialize settings (globals)
        scrollPixelsPerFrame = 2
        jumpVelocity = 12
        maxfps = 60
        reloadSettings() # This will update them from file

        print("Entering main loop...", flush=True)

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
            await asyncio.sleep(0)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"CRITICAL ERROR: {e}", flush=True)

    print("Main loop finished or crashed.")
    pygame.quit()

asyncio.run(main())