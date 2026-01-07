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

### Modifying Game State

Unlike before, the `game_state` is now **two-way synchronized**. This means you can modify values in the `game_state` dictionary, and the game will potentially adopt them in the next frame.

You can modify:
- `player_pos`: Tuple `(x, y)`. Teleport the player!
- `player_velocity`: Float. Change jump height or gravity effects.
- `points`: Int. Give the player free points.
- `scroll`: Float. Fast forward or rewind time (visually).
- `pipe_color`: Tuple `(r, g, b)`. Disco pipes?

**Example: Super Jump**
```python
def super_jump():
    state = api.get("game_state", {})
    # Set negative velocity to jump up
    state['player_velocity'] = -20 
    
api["register_on_jump"](super_jump)
```

### New Hooks

**`register_on_jump(function)`**
Called when the player presses the jump button (Space or Click).
- **Parameter:** None.

**`register_on_collision(function)`**
Called when the player hits a pipe or the ground.
- **Parameter:** None.
- **Return Value:** If your function returns `False`, the collision is **cancelled**. This effectively gives you God Mode.

```python
def god_mode():
    return False # I refuse to die

api["register_on_collision"](god_mode)
```

**`register_on_score(function)`**
Called when the player's score increases.
- **Parameter:** `new_score` (int).

**`register_on_quit(function)`**
Called when the game is closing.
- **Parameter:** None.

## Example Mod: God Mode & Super Jump

```python
try:
    api = mod_api
except NameError:
    api = None

if api:
    def on_jump_hook():
        print("Super Jump Activated!")
        state = api["game_state"]
        # Make the jump twice as strong
        state["player_velocity"] = -15 

    def on_collision_hook():
        print("Collision avoided! God Mode active.")
        return False # Cancel collision

    api["register_on_jump"](on_jump_hook)
    api["register_on_collision"](on_collision_hook)
```

Happy modding!
