import os
import sys
import dependencies
import inspect

# Shared game state that mods can access
game_state = {}

# Storage for hooks
_hooks = {
    "on_update": [],
    "on_draw": [],
    "on_event": [],
    "on_restart": [],
    "on_jump": [],
    "on_collision": [],
    "on_score": [],
    "on_quit": [],
    "on_main_menu": [],
    "on_pause_screen": [],
    "on_lose_screen": [],
    "on_settings": []
}

def update_game_state(new_state):
    """Allow the main game to update the shared game state."""
    global game_state
    game_state.update(new_state)

def get_game_state():
    """Return the current game state to the main game."""
    return game_state

# --- Registration functions for mods ---
def register_on_update(func):
    """Register a function to be called every game frame."""
    _hooks["on_update"].append(func)

def register_on_draw(func):
    """Register a function for custom drawing."""
    _hooks["on_draw"].append(func)

def register_on_event(func):
    """Register a function to handle Pygame events."""
    _hooks["on_event"].append(func)

def register_on_restart(func):
    """Register a function to be called when the game restarts."""
    _hooks["on_restart"].append(func)

def register_on_jump(func):
    """Register a function to be called when the player jumps."""
    _hooks["on_jump"].append(func)

def register_on_collision(func):
    """
    Register a function to be called when a collision is detected.
    The function should return False to cancel the collision (God Mode).
    """
    _hooks["on_collision"].append(func)

def register_on_score(func):
    """Register a function to be called when score increases."""
    _hooks["on_score"].append(func)

def register_on_quit(func):
    """Register a function to be called when the game is quitting."""
    _hooks["on_quit"].append(func)

# --- Trigger functions for the main game ---
def trigger_on_update(delta):
    """Execute all registered on_update hooks."""
    for func in _hooks["on_update"]:
        try:
            func(delta)
        except Exception as e:
            print(f"Error in on_update hook: {e}")

def trigger_on_draw(screen, game_state):
    """Execute all registered on_draw hooks."""
    for func in _hooks["on_draw"]:
        try:
            sig = inspect.signature(func)
            num_params = len(sig.parameters)
            if num_params == 1:
                func(screen)
            elif num_params == 2:
                func(screen, game_state)
            else:
                print(f"Warning: on_draw hook '{func.__name__}' has an unsupported number of parameters ({num_params}). Expected 1 or 2.", file=sys.stderr)
        except Exception as e:
            print(f"Error executing on_draw hook '{func.__name__}': {e}", file=sys.stderr)

def trigger_on_event(event):
    """Execute all registered on_event hooks."""
    for func in _hooks["on_event"]:
        try:
            func(event)
        except Exception as e:
            print(f"Error in on_event hook: {e}")
        
def trigger_on_restart():
    """Execute all registered on_restart hooks."""
    for func in _hooks["on_restart"]:
        try:
            func()
        except Exception as e:
            print(f"Error in on_restart hook: {e}")

def trigger_on_jump():
    """Execute on_jump hooks."""
    for func in _hooks["on_jump"]:
        try:
            func()
        except Exception as e:
            print(f"Error in on_jump hook: {e}")

def trigger_on_collision():
    """
    Execute on_collision hooks.
    If ANY hook returns False, the collision is considered cancelled (God Mode).
    Returns True if collision is valid, False if it was cancelled.
    """
    collision_valid = True
    for func in _hooks["on_collision"]:
        try:
            result = func()
            if result is False:
                collision_valid = False
        except Exception as e:
            print(f"Error in on_collision hook: {e}")
    return collision_valid

def trigger_on_score(new_score):
    """Execute on_score hooks."""
    for func in _hooks["on_score"]:
        try:
            func(new_score)
        except Exception as e:
            print(f"Error in on_score hook: {e}")

def trigger_on_quit():
    """Execute on_quit hooks."""
    for func in _hooks["on_quit"]:
        try:
            func()
        except Exception as e:
            print(f"Error in on_quit hook: {e}")

# --- GUI Hooks ---
def register_on_main_menu(func):
    """Register a function to be called when the main menu is shown."""
    _hooks["on_main_menu"].append(func)

def register_on_pause_screen(func):
    """Register a function to be called when the pause screen is shown."""
    _hooks["on_pause_screen"].append(func)

def register_on_lose_screen(func):
    """Register a function to be called when the lose screen is shown."""
    _hooks["on_lose_screen"].append(func)

def register_on_settings(func):
    """Register a function to be called when the settings menu is shown."""
    _hooks["on_settings"].append(func)

def trigger_on_main_menu(window):
    """Execute on_main_menu hooks, passing the window object."""
    for func in _hooks["on_main_menu"]:
        try:
            func(window)
        except Exception as e:
            print(f"Error in on_main_menu hook: {e}")

def trigger_on_pause_screen(window):
    """Execute on_pause_screen hooks, passing the window object."""
    for func in _hooks["on_pause_screen"]:
        try:
            func(window)
        except Exception as e:
            print(f"Error in on_pause_screen hook: {e}")

def trigger_on_lose_screen(window):
    """Execute on_lose_screen hooks, passing the window object."""
    for func in _hooks["on_lose_screen"]:
        try:
            func(window)
        except Exception as e:
            print(f"Error in on_lose_screen hook: {e}")

def trigger_on_settings(window):
    """Execute on_settings hooks, passing the window object."""
    for func in _hooks["on_settings"]:
        try:
            func(window)
        except Exception as e:
            print(f"Error in on_settings hook: {e}")

def load_mods():
    """Discover and load all mods from the project and user data directories."""
    
    # Define both directories
    local_mods_dir = "mods"
    user_mods_dir = os.path.join(dependencies.get_user_data_dir(), "mods")

    # Ensure directories exist
    if not os.path.exists(local_mods_dir):
        os.makedirs(local_mods_dir)
    if not os.path.exists(user_mods_dir):
        os.makedirs(user_mods_dir)
        print(f"Created user mods directory at: {user_mods_dir}")
        
    all_mod_files = {} # Use a dictionary to avoid duplicates, mapping filename to full path

    # Discover mods in local directory
    for f in os.listdir(local_mods_dir):
        if f.endswith(".py"):
            all_mod_files[f] = os.path.join(local_mods_dir, f)
            
    # Discover mods in user directory (will overwrite if names conflict, which is intended)
    for f in os.listdir(user_mods_dir):
        if f.endswith(".py"):
            all_mod_files[f] = os.path.join(user_mods_dir, f)

    if not all_mod_files:
        print("No mods found in local or user directory.")
        return
        
    print(f"Loading {len(all_mod_files)} mod(s):", ", ".join(m.replace('.py', '') for m in all_mod_files.keys()))

    # API that will be exposed to the mods
    mod_api = {
        "register_on_update": register_on_update,
        "register_on_draw": register_on_draw,
        "register_on_event": register_on_event,
        "register_on_restart": register_on_restart,
        "register_on_jump": register_on_jump,
        "register_on_collision": register_on_collision,
        "register_on_score": register_on_score,
        "register_on_quit": register_on_quit,
        "register_on_main_menu": register_on_main_menu,
        "register_on_pause_screen": register_on_pause_screen,
        "register_on_lose_screen": register_on_lose_screen,
        "register_on_settings": register_on_settings,
        "game_state": game_state,
    }

    for mod_name, mod_path in all_mod_files.items():
        try:
            with open(mod_path, 'r') as f:
                mod_code = f.read()
                # Execute the mod's code in a context that has access to the mod_api
                exec(mod_code, {"mod_api": mod_api})
        except Exception as e:
            print(f"Error loading mod '{mod_name}' from '{mod_path}': {e}", file=sys.stderr)

    print("Mods loaded.")