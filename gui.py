import pygame
import pygame_gui
from pygame_gui.elements import UIWindow, UIButton
import dependencies

# Global variables to hold the UI windows
pause_window = None
lose_window = None
name_input_window = None
remember_name_checkbox = None
main_menu_window = None
options_window = None
sliders = {}
value_labels = {}


def create_main_menu_window(manager):
    """
    Creates the main menu window.
    """
    global main_menu_window
    if main_menu_window is not None:
        return # Window already exists

    window_height = 320
    window_rect = pygame.Rect((0, 0), (300, window_height))
    window_rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)

    main_menu_window = UIWindow(
        rect=window_rect,
        manager=manager,
        window_display_title="Skakavi Krompir",
        object_id='#main_menu'
    )
    
    button_width = 150 # Wider buttons for main menu
    button_height = 40
    button_x = (window_rect.width - button_width) // 2 # Centered x

    # Buttons
    UIButton(
        relative_rect=pygame.Rect((button_x, 20), (button_width, button_height)),
        text='Start Game',
        manager=manager,
        container=main_menu_window,
        object_id='@main_menu_start_button'
    )
    UIButton(
        relative_rect=pygame.Rect((button_x, 80), (button_width, button_height)),
        text='Settings',
        manager=manager,
        container=main_menu_window,
        object_id='@main_menu_settings_button'
    )
    UIButton(
        relative_rect=pygame.Rect((button_x, 140), (button_width, button_height)),
        text='Scores',
        manager=manager,
        container=main_menu_window,
        object_id='@main_menu_scores_button'
    )
    UIButton(
        relative_rect=pygame.Rect((button_x, 200), (button_width, button_height)),
        text='Public Leaderboard',
        manager=manager,
        container=main_menu_window,
        object_id='@main_menu_public_leaderboard_button'
    )
    UIButton(
        relative_rect=pygame.Rect((button_x, 260), (button_width, button_height)),
        text='Exit',
        manager=manager,
        container=main_menu_window,
        object_id='@main_menu_exit_button'
    )

def close_main_menu_window():
    """
    Closes the main menu window.
    """
    global main_menu_window
    if main_menu_window is not None:
        main_menu_window.kill()
        main_menu_window = None
def create_name_input_window(manager):
    """
    Creates the name input window.
    """
    global name_input_window, name_entry_box, remember_name_checkbox
    if name_input_window is not None:
        return # Window already exists

    window_rect = pygame.Rect((0, 0), (350, 240))
    window_rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)

    name_input_window = UIWindow(
        rect=window_rect,
        manager=manager,
        window_display_title="Enter Your Name",
        object_id='#name_input_menu'
    )

    # Label
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((0, 10), (window_rect.width - 20, 30)),
        text="Please enter your name:",
        manager=manager,
        container=name_input_window
    )

    # Text Entry
    name_entry_box = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((50, 50), (250, 40)),
        manager=manager,
        container=name_input_window,
        object_id='@name_entry'
    )

    # Checkbox
    remember_name_checkbox = pygame_gui.elements.UICheckBox(
        relative_rect=pygame.Rect((50, 100), (200, 40)),
        text="Remember name",
        manager=manager,
        container=name_input_window,
        object_id='@remember_name_checkbox'
    )

    # Save Button
    UIButton(
        relative_rect=pygame.Rect((125, 150), (100, 40)),
        text='Save',
        manager=manager,
        container=name_input_window,
        object_id='@name_save_button'
    )

def close_name_input_window():
    """
    Closes the name input window.
    """
    global name_input_window, name_entry_box, remember_name_checkbox
    if name_input_window is not None:
        name_input_window.kill()
        name_input_window = None
        name_entry_box = None
        remember_name_checkbox = None

def create_pause_screen(manager):
    """
    Creates the pause menu window.
    """
    global pause_window
    if pause_window is not None:
        return  # Window already exists

    # Original CTK window was 340x300, but with more buttons now, it needs to be taller.
    # Resume (40px) + (20px pad) Scores (40px) + (20px pad) Public Leaderboard (40px) + (20px pad)
    # Settings (40px) + (20px pad) Update (40px) + (20px pad) Quit (40px) = 6*40 + 5*20 = 240 + 100 = 340px height needed for buttons + some extra
    # Adjusted for more buttons: 6*40 (buttons) + 5*20 (gaps) + 20 (top) + 20 (bottom) = 240 + 100 + 40 = 380px
    window_height = 400
    window_rect = pygame.Rect((0, 0), (300, window_height)) # Width 300
    window_rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)

    pause_window = UIWindow(
        rect=window_rect,
        manager=manager,
        window_display_title="Paused",
        object_id='#pause_menu'
    )
    
    button_width = 100
    button_height = 40
    button_x = (window_rect.width - button_width) // 2 # Centered x

    # Resume Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 20), (button_width, button_height)),
        text='Resume',
        manager=manager,
        container=pause_window,
        object_id='@pause_resume_button'
    )

    # Scores Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 80), (button_width, button_height)),
        text='Scores',
        manager=manager,
        container=pause_window,
        object_id='@pause_scores_button'
    )

    # Public Leaderboard Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 140), (button_width, button_height)),
        text='Public Leaderboard',
        manager=manager,
        container=pause_window,
        object_id='@pause_public_leaderboard_button'
    )

    # Settings Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 200), (button_width, button_height)),
        text='Settings',
        manager=manager,
        container=pause_window,
        object_id='@pause_settings_button'
    )

    # Update Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 260), (button_width, button_height)),
        text='Update',
        manager=manager,
        container=pause_window,
        object_id='@pause_update_button'
    )

    # Quit Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 320), (button_width, button_height)),
        text='Quit',
        manager=manager,
        container=pause_window,
        object_id='@pause_quit_button'
    )

def close_pause_screen():
    """
    Closes the pause menu window.
    """
    global pause_window
    if pause_window is not None:
        pause_window.kill()
        pause_window = None

def create_lose_screen(manager):
    """
    Creates the lose screen window.
    """
    global lose_window
    if lose_window is not None:
        return # Window already exists

    # Original CTK window was 300x200, but with more buttons now, it needs to be taller.
    # Restart (40px) + (20px pad) Public Leaderboard (40px) + (20px pad) Quit (40px) = 3*40 + 2*20 = 120 + 40 = 160px height needed
    # Adjusted for more buttons: 3*40 (buttons) + 2*20 (gaps) + 20 (top) + 20 (bottom) = 120 + 40 + 40 = 200px
    window_height = 220
    window_rect = pygame.Rect((0, 0), (300, window_height)) # Width 300
    window_rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)

    lose_window = UIWindow(
        rect=window_rect,
        manager=manager,
        window_display_title="You Lost!",
        object_id='#lose_menu'
    )

    button_width = 100
    button_height = 40
    button_x = (window_rect.width - button_width) // 2 # Centered x

    # Restart Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 20), (button_width, button_height)),
        text='Restart',
        manager=manager,
        container=lose_window,
        object_id='@lose_restart_button'
    )

    # Public Leaderboard Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 80), (button_width, button_height)),
        text='Public Leaderboard',
        manager=manager,
        container=lose_window,
        object_id='@lose_public_leaderboard_button'
    )

    # Quit Button
    UIButton(
        relative_rect=pygame.Rect((button_x, 140), (button_width, button_height)),
        text='Quit',
        manager=manager,
        container=lose_window,
        object_id='@lose_quit_button'
    )


def close_lose_screen():


    """


    Closes the lose screen window.


    """


    global lose_window


    if lose_window is not None:


        lose_window.kill()


        lose_window = None





# --- Options Window (moved here as a workaround) ---


options_window = None





def create_options_window(manager):


    """


    Creates a test options window.


    """


    global options_window


    if options_window is not None:


        return





    options_window = pygame_gui.elements.UIWindow(


        rect=pygame.Rect((0, 0), (300, 220)),


        manager=manager,


        window_display_title="Settings (Test)"


    )


    options_window.rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)





    container = options_window.get_container()


    button_width = 100


    button_x = (container.get_rect().width - button_width) / 2





    # Test Button 1


    pygame_gui.elements.UIButton(


        relative_rect=pygame.Rect((button_x, 20), (button_width, 40)),


        text='Test Button',


        manager=manager,


        container=container,


        object_id='@options_test_button'


    )





    # Close Button


    pygame_gui.elements.UIButton(


        relative_rect=pygame.Rect((button_x, 80), (button_width, 40)),


        text='Close',


        manager=manager,


        container=container,


        object_id='@options_close_button'


    )





def close_options_window():





    """Closes the options window."""





    global options_window





    if options_window is not None:





        options_window.kill()





        options_window = None











def create_options_window(manager):





    """Creates the options/settings window."""





    global options_window, sliders, value_labels





    if options_window is not None:





        options_window.focus()





        return











    options_window = pygame_gui.elements.UIWindow(





        rect=pygame.Rect((0, 0), (400, 420)),





        manager=manager,





        window_display_title="Settings"





    )





    options_window.rect.center = (manager.window_resolution[0] // 2, manager.window_resolution[1] // 2)











    container = options_window.get_container()





    y_pos = 10











    # --- Sliders for settings ---





    settings_to_add = [





        {"key": "scrollPixelsPerFrame", "name": "Speed", "range": (1, 20), "default": 8},





        {"key": "jumpVelocity", "name": "Jump Height", "range": (1, 20), "default": 8},





        {"key": "maxFps", "name": "Max FPS", "range": (30, 240), "default": 60},





        {"key": "speed_increase", "name": "Speed Increase", "range": (0, 10), "default": 3},





    ]











    for setting in settings_to_add:





        pygame_gui.elements.UILabel(





            relative_rect=pygame.Rect((10, y_pos), (150, 30)),





            text=setting["name"], manager=manager, container=container





        )





        current_value = dependencies.getSettings(setting["key"])





        if current_value is None: current_value = setting["default"]





        try:





            current_value = int(current_value)





        except (ValueError, TypeError):





            current_value = setting["default"]











        value_labels[setting["key"]] = pygame_gui.elements.UILabel(





            relative_rect=pygame.Rect((170, y_pos), (50, 30)),





            text=str(current_value), manager=manager, container=container





        )





        





        sliders[setting["key"]] = pygame_gui.elements.UIHorizontalSlider(





            relative_rect=pygame.Rect((230, y_pos), (150, 30)),





            start_value=current_value, value_range=setting["range"],





            manager=manager, container=container, object_id=f"@options_slider_{setting['key']}"





        )





        y_pos += 40











    y_pos += 20





    button_width = 150





    button_x = (container.get_rect().width - button_width) / 2











    pygame_gui.elements.UIButton(





        relative_rect=pygame.Rect((button_x, y_pos), (button_width, 40)),





        text="Upload Font", manager=manager, container=container, object_id="@options_upload_font"





    )





    y_pos += 50





    pygame_gui.elements.UIButton(





        relative_rect=pygame.Rect((button_x, y_pos), (button_width, 40)),





        text="Upload Image", manager=manager, container=container, object_id="@options_upload_image"





    )





    y_pos += 50





    pygame_gui.elements.UIButton(





        relative_rect=pygame.Rect((button_x, y_pos), (button_width, 40)),





        text="Reset Settings", manager=manager, container=container, object_id="@options_reset_settings"





    )





    y_pos += 60





    pygame_gui.elements.UIButton(





        relative_rect=pygame.Rect((button_x, y_pos), (100, 40)),





        text="Close", manager=manager, container=container, object_id="@options_close_button"





    )







