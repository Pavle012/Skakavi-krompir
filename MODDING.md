# Modding Guide for Skakavi Krompir

This guide will walk you through creating your own mods for Skakavi Krompir.

## Getting Started

Creating a mod is as simple as creating a Python script (`.py` file) and placing it in the correct directory. The game's mod loader will automatically discover and load it.

### Mod Locations

Mods can be placed in two locations:

1.  **Project `mods/` directory:** A folder named `mods` right next to the game's main files. This is useful for developers or for mods that are bundled with the game.
2.  **User data `mods/` directory:** A `mods` folder located in your user-specific data directory. This is the recommended place for personal mods, as they won't be affected by game updates.

The user data directory path depends on your operating system:
*   **Windows:** `%APPDATA%\SkakaviKrompir` (e.g., `C:\Users\YourUser\AppData\Roaming\SkakaviKrompir`)
*   **Linux/macOS:** `~/.local/share/SkakaviKrompir` (e.g., `/home/YourUser/.local/share/SkakaviKrompir`)

The game will create this directory for you on the first run. You will need to create the `mods` subfolder inside it yourself.

> **Note:** If a mod in the user data directory has the same filename as a mod in the project directory, the one in the user data directory will be loaded, overriding the project one.

## The Modding API (`mod_api`)

When the game loads your mod, it injects a global dictionary called `mod_api` into your script's scope. This API is your gateway to interacting with the game.

### Accessing the API

To use the API, you can get it at the top of your script. It's a good practice to wrap it in a `try...except` block to prevent errors if the script is run directly.

```python
try:
    api = mod_api
except NameError:
    print("This script is a mod and is not meant to be run directly.")
    api = None
```

### Hooks (Registration Functions)

Hooks are functions that let you "hook into" the game's loop at specific points. You register your own functions to be called by the game.

To register a hook, you call the corresponding registration function from the `api` and pass your function as an argument.

**`register_on_update(function)`**

This hook is called on every single game frame. It's ideal for logic that needs to run continuously.

-   **Parameter:** Your function will receive one argument: `delta` (the time in seconds since the last frame).

```python
def my_update_logic(delta):
    # Do something every frame
    pass

api["register_on_update"](my_update_logic)
```

**`register_on_draw(function)`**

This hook is called after the game has drawn all its elements, allowing you to draw your own graphics on top.

-   **Parameters:** Your function can accept one or two arguments:
    1.  `screen`: The main Pygame screen surface to draw on.
    2.  `game_state` (optional): The shared game state dictionary (see below).

```python
def my_drawing(screen, game_state):
    # Draw a circle on the screen
    import pygame
    pygame.draw.circle(screen, (255, 0, 0), (100, 100), 20)

api["register_on_draw"](my_drawing)
```

**`register_on_event(function)`**

This hook is called for every Pygame event (like key presses, mouse clicks, etc.).

-   **Parameter:** Your function will receive one argument: `event` (the Pygame event object).

```python
def my_event_handler(event):
    import pygame
    if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
        print("P key was pressed!")

api["register_on_event"](my_event_handler)
```

**`register_on_restart(function)`**

This hook is called every time the player restarts the game. It's useful for resetting any state your mod might have.

-   **Parameters:** Your function receives no arguments.

```python
def on_game_restart():
    print("The game has restarted!")

api["register_on_restart"](on_game_restart)
```

### Shared Game State (`game_state`)

The `mod_api` provides access to a `game_state` dictionary that contains read-only information about the current game session.

You can access it via `api["game_state"]` or, more safely, `api.get("game_state", {})`. It is also passed as the second argument to `on_draw` hooks.

The dictionary contains the following keys:

| Key               | Type               | Description                                           |
| ----------------- | ------------------ | ----------------------------------------------------- |
| `player_pos`      | `tuple` (x, y)     | The logical top-left coordinates of the player.       |
| `player_velocity` | `float`            | The current vertical velocity of the player.          |
| `player_rect`     | `pygame.Rect`      | The bounding rectangle of the rotated player sprite.  |
| `player_surface`  | `pygame.Surface`   | The rotated player image surface.                     |
| `pipes`           | `list` of `tuples` | A list of all pipes. Each is `(x, y, is_top)`.        |
| `scroll`          | `float`            | The current horizontal scroll position of the world.  |
| `width`           | `int`              | The current width of the game window.                 |
| `height`          | `int`              | The current height of the game window.                |
| `points`          | `int`              | The current score.                                    |
| `pipe_spacing`    | `int`              | The horizontal distance between pipes.                |
| `pipe_color`      | `tuple` (r, g, b)  | The current color of the pipes.                       |


## Example Mod

This example mod demonstrates how to use the different hooks. You can find this file in `mods/example.py`.

```python
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
    if game_state and game_state.get('points', 0) > 5:
        print(f"Wow, you have more than 5 points!")


def on_draw_example(screen, game_state):
    """
    This function is for drawing custom graphics on the screen.
    `screen` is the main Pygame screen surface.
    `game_state` has the current game data.
    """
    try:
        import pygame
        # Draw a semi-transparent circle around the potato
        player_rect = game_state.get('player_rect')
        if player_rect:
            # Create a separate surface for the circle to handle transparency
            radius = player_rect.width / 2 + 10
            circle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surface, (255, 255, 0, 100), (radius, radius), radius)
            screen.blit(circle_surface, (player_rect.centerx - radius, player_rect.centery - radius))

    except ImportError:
        pass # Pygame not available

def on_event_example(event):
    """
    This function is called for each Pygame event.
    """
    try:
        import pygame
        if event.type == pygame.KEYDOWN:
            # Example of using an event
            if event.key == pygame.K_h:
                print("Mod detected 'h' key press!")
    except (ImportError, pygame.error):
        pass

def on_restart_example():
    """
    This function is called every time the game restarts.
    """
    print("Mod 'example' detected game restart!")


# --- Registration ---
# Make sure the api is available before registering hooks
if api:
    print("Registering example_mod hooks...")
    api["register_on_update"](on_update_example)
    api["register_on_draw"](on_draw_example)
    api["register_on_event"](on_event_example)
    api["register_on_restart"](on_restart_example)
    print("example_mod hooks registered.")
```

Happy modding!
