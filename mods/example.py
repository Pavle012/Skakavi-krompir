# Example Mod for Skakavi Krompir

try:
    # mod_api is injected by the modloader
    api = mod_api
except NameError:
    print("This script is a mod and is not meant to be run directly.")
    api = None

def on_update_example(delta):
    """
    This function will be called every frame.
    `delta` is the time in seconds since the last frame.
    Access game_state via the api dictionary.
    """
    game_state = api.get("game_state", {})
    # Example of accessing game state:
    # if game_state:
    #     print(f"Current points: {game_state.get('points')}")
    pass

def on_draw_example(screen):
    """
    This function is for drawing custom graphics on the screen.
    `screen` is the main Pygame screen surface.
    """
    # Example: Draw a small red circle at position (20, 20)
    try:
        import pygame
        pygame.draw.circle(screen, (255, 0, 0), (20, 20), 10)
    except (ImportError, pygame.error):
        # Pygame might not be available in all contexts, or drawing might fail
        pass

def on_event_example(event):
    """
    This function is called for each Pygame event.
    """
    try:
        import pygame
        if event.type == pygame.KEYDOWN:
            # Example of using an event
            # print(f"Mod detected key press: {pygame.key.name(event.key)}")
            pass
    except (ImportError, pygame.error):
        pass
        
def on_restart_example():
    """
    This function is called every time the game restarts.
    """
    print("Mod 'example' detected game restart!")


# --- Registration ---
if api:
    print("Registering example_mod hooks...")
    api["register_on_update"](on_update_example)
    api["register_on_draw"](on_draw_example)
    api["register_on_event"](on_event_example)
    api["register_on_restart"](on_restart_example)
    print("example_mod hooks registered.")
