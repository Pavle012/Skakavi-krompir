# Project Overview

This project is a "Flappy Bird-like" game called "Skakavi Krompir". It is written in Python and uses the following libraries:

*   **Pygame:** For the core game mechanics and rendering.
*   **CustomTkinter:** For the user interface elements, such as menus, settings, and score display.
*   **Pillow:** For image manipulation.

The game's architecture is modular, with different functionalities separated into different files:

*   `main.py`: The main entry point of the game, containing the game loop and core logic.
*   `gui.py`: Handles the creation of the pause and lose screens.
*   `options.py`: Provides a settings screen where the user can customize game parameters.
*   `scores.py`: Displays the high scores.
*   `dependencies.py`: A utility script that automatically installs missing dependencies and downloads game assets.
*   `namecheck.py`: A utility script that prompts the user to enter their name.
*   `settings.txt`: A text file that stores the game's settings.
*   `scores.txt`: A text file that stores the game's scores.

# Building and Running

This project does not require a separate build step. To run the game, simply execute the `main.py` script:

```bash
python3 main.py
```

The `dependencies.py` script will automatically install any missing dependencies (`pygame`, `customtkinter`, and `pillow`) on the first run.

# Development Conventions

*   **Code Style:** The code generally follows PEP 8 conventions, but there are some inconsistencies.
*   **Testing:** There are no automated tests in this project.
*   **Contribution:** There are no explicit contribution guidelines.
