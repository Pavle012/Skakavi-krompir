"""
namecheck.py  —  Pure-pygame name-entry screen.
No tkinter/customtkinter required.
"""

import pygame
import os
import dependencies

retun = "Unnamed"


def _set_settings(key, new_value):
    settings = {}
    settings_path = os.path.join(dependencies.get_user_data_dir(), "settings.txt")
    if os.path.exists(settings_path):
        with open(settings_path) as f:
            for line in f:
                if "=" in line:
                    k, value = line.strip().split("=", 1)
                    settings[k] = value
    settings[key] = new_value
    with open(settings_path, "w") as f:
        for k, value in settings.items():
            f.write(f"{k}={value}\n")


def _font(size):
    return pygame.font.Font(dependencies.get_font_path(), size)


def _draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)


def getname():
    """
    Show a pygame name-entry screen.
    Returns the entered name (str).
    """
    global retun

    # Initialise pygame display if it isn't up yet.
    # (main.py calls us before pygame.init() on first launch, so we do a minimal init here)
    if not pygame.get_init():
        pygame.init()

    # Create a temporary window if none exists yet
    screen = pygame.display.get_surface()
    temp_display = False
    if screen is None:
        screen = pygame.display.set_mode((600, 400), pygame.RESIZABLE)
        pygame.display.set_caption("Skakavi Krompir")
        temp_display = True

    # Try to set window icon
    icon_pil = dependencies.get_global_icon_pil()
    if icon_pil:
        try:
            import io
            buf = io.BytesIO()
            icon_pil.save(buf, format="PNG")
            buf.seek(0)
            icon_surf = pygame.image.load(buf)
            pygame.display.set_icon(icon_surf)
        except Exception:
            pass

    title_font = _font(36)
    label_font = _font(22)
    input_font = _font(26)
    hint_font = _font(16)

    text = ""
    remember = False
    cursor_visible = True
    cursor_timer = 0

    clock = pygame.time.Clock()
    MAX_NAME_LEN = 24

    while True:
        sw, sh = screen.get_size()

        box_w = min(480, sw - 60)
        box_h = 300
        box_x = sw // 2 - box_w // 2
        box_y = sh // 2 - box_h // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        screen.fill((20, 20, 35))
        _draw_rounded_rect(screen, (30, 30, 48), box_rect, radius=18,
                           border=2, border_color=(100, 100, 180))

        # Title
        t_surf = title_font.render("Enter Your Name", True, (255, 255, 255))
        screen.blit(t_surf, (box_rect.centerx - t_surf.get_width() // 2, box_rect.y + 18))

        # Label
        l_surf = label_font.render("Your name:", True, (190, 190, 215))
        screen.blit(l_surf, (box_rect.x + 24, box_rect.y + 78))

        # Input box
        input_rect = pygame.Rect(box_rect.x + 24, box_rect.y + 108, box_w - 48, 44)
        _draw_rounded_rect(screen, (50, 50, 72), input_rect, radius=8,
                           border=2, border_color=(130, 130, 210))

        display_text = text
        t_surf2 = input_font.render(display_text, True, (255, 255, 255))
        if t_surf2.get_width() > input_rect.w - 20:
            for i in range(len(display_text)):
                t_surf2 = input_font.render(display_text[i:], True, (255, 255, 255))
                if t_surf2.get_width() <= input_rect.w - 20:
                    break
        screen.blit(t_surf2, (input_rect.x + 10,
                               input_rect.y + (input_rect.h - t_surf2.get_height()) // 2))

        # Cursor
        cursor_timer += clock.get_time()
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        if cursor_visible:
            cx = input_rect.x + 10 + t_surf2.get_width() + 1
            pygame.draw.line(screen, (255, 255, 255),
                             (cx, input_rect.y + 6), (cx, input_rect.bottom - 6), 2)

        # Remember checkbox
        chk_rect = pygame.Rect(box_rect.x + 24, box_rect.y + 166, 22, 22)
        _draw_rounded_rect(screen, (55, 55, 80), chk_rect, radius=5,
                           border=2, border_color=(180, 180, 200))
        if remember:
            inner = chk_rect.inflate(-6, -6)
            pygame.draw.rect(screen, (100, 220, 130), inner, border_radius=3)
        chk_label = hint_font.render("Remember name", True, (210, 210, 220))
        screen.blit(chk_label, (chk_rect.right + 10,
                                 chk_rect.y + (chk_rect.h - chk_label.get_height()) // 2))

        # Buttons
        save_rect = pygame.Rect(box_rect.x + 24, box_rect.y + 206, (box_w - 56) // 2, 38)
        exit_rect = pygame.Rect(save_rect.right + 8, box_rect.y + 206,
                                (box_w - 56) // 2, 38)

        mouse_pos = pygame.mouse.get_pos()
        save_hover = save_rect.collidepoint(mouse_pos)
        exit_hover = exit_rect.collidepoint(mouse_pos)

        _draw_rounded_rect(screen,
                           (46, 180, 100) if save_hover else (36, 140, 70),
                           save_rect, radius=8)
        _draw_rounded_rect(screen,
                           (200, 60, 50) if exit_hover else (160, 40, 40),
                           exit_rect, radius=8)

        save_lbl = label_font.render("Save", True, (255, 255, 255))
        exit_lbl = label_font.render("Exit", True, (255, 255, 255))
        screen.blit(save_lbl, (save_rect.centerx - save_lbl.get_width() // 2,
                                save_rect.centery - save_lbl.get_height() // 2))
        screen.blit(exit_lbl, (exit_rect.centerx - exit_lbl.get_width() // 2,
                                exit_rect.centery - exit_lbl.get_height() // 2))

        # Hint
        h_surf = hint_font.render("Enter to save  •  Esc to exit", True, (130, 130, 150))
        screen.blit(h_surf, (box_rect.centerx - h_surf.get_width() // 2, box_rect.bottom - 22))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    _do_save(text if text.strip() else "Unnamed", remember)
                    retun = text if text.strip() else "Unnamed"
                    return retun
                elif event.key == pygame.K_ESCAPE:
                    import sys
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable() and len(text) < MAX_NAME_LEN:
                        text += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if chk_rect.collidepoint(event.pos):
                    remember = not remember
                elif save_rect.collidepoint(event.pos):
                    _do_save(text if text.strip() else "Unnamed", remember)
                    retun = text if text.strip() else "Unnamed"
                    return retun
                elif exit_rect.collidepoint(event.pos):
                    import sys
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.VIDEORESIZE:
                pass  # screen reference stays valid


def _do_save(name, remember):
    _set_settings("name", name)
    _set_settings("rememberName", str(remember))
