"""
namecheck.py  —  Pure-pygame name-entry screen.
No tkinter/customtkinter required.
"""

import pygame
import os
from shared import dependencies
from shared import friends_client

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
    Show a pygame name-entry screen with an optional online-mode username/password
    account flow used by the public records server.
    Returns the entered name (str).
    """
    global retun

    if not pygame.get_init():
        pygame.init()

    screen = pygame.display.get_surface()
    temp_display = False
    if screen is None:
        screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
        pygame.display.set_caption("Skakavi Krompir")
        temp_display = True

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
    password_text = ""
    remember = False
    online_mode = False
    active_field = "name"
    cursor_visible = True
    cursor_timer = 0
    error_msg = ""

    clock = pygame.time.Clock()
    MAX_NAME_LEN = 24
    MAX_PASS_LEN = 32

    while True:
        sw, sh = screen.get_size()

        box_w = min(560, sw - 40)
        box_h = 430 if online_mode else 380
        box_x = sw // 2 - box_w // 2
        box_y = sh // 2 - box_h // 2
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)

        screen.fill((20, 20, 35))
        _draw_rounded_rect(screen, (30, 30, 48), box_rect, radius=18,
                           border=2, border_color=(100, 100, 180))

        title_y = box_rect.y + 20
        t_surf = title_font.render("Enter Your Name", True, (255, 255, 255))
        screen.blit(t_surf, (box_rect.centerx - t_surf.get_width() // 2, title_y))

        label_y = box_rect.y + 84
        l_surf = label_font.render("Your name:", True, (190, 190, 215))
        screen.blit(l_surf, (box_rect.x + 24, label_y))

        input_y = box_rect.y + 116
        input_rect = pygame.Rect(box_rect.x + 24, input_y, box_w - 48, 44)
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

        password_rect = None
        if online_mode:
            pass_label_y = box_rect.y + 176
            pass_label = label_font.render("Password:", True, (190, 190, 215))
            screen.blit(pass_label, (box_rect.x + 24, pass_label_y))

            password_y = box_rect.y + 210
            password_rect = pygame.Rect(box_rect.x + 24, password_y, box_w - 48, 44)
            _draw_rounded_rect(screen, (50, 50, 72), password_rect, radius=8,
                               border=2, border_color=(130, 130, 210))
            pass_display = "*" * len(password_text)
            p_surf = input_font.render(pass_display, True, (255, 255, 255))
            screen.blit(p_surf, (password_rect.x + 10,
                                 password_rect.y + (password_rect.h - p_surf.get_height()) // 2))

        cursor_timer += clock.get_time()
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        if cursor_visible:
            if online_mode and active_field == "password" and password_rect:
                p_surf = input_font.render("*" * len(password_text), True, (255, 255, 255))
                cx = password_rect.x + 10 + p_surf.get_width() + 1
                pygame.draw.line(screen, (255, 255, 255),
                                 (cx, password_rect.y + 6), (cx, password_rect.bottom - 6), 2)
            else:
                cx = input_rect.x + 10 + t_surf2.get_width() + 1
                pygame.draw.line(screen, (255, 255, 255),
                                 (cx, input_rect.y + 6), (cx, input_rect.bottom - 6), 2)

        if online_mode:
            check_y = box_rect.y + 280
            online_rect = pygame.Rect(box_rect.x + 24, check_y, 22, 22)
            _draw_rounded_rect(screen, (55, 55, 80), online_rect, radius=5,
                               border=2, border_color=(180, 180, 200))
            inner = online_rect.inflate(-6, -6)
            pygame.draw.rect(screen, (100, 220, 130), inner, border_radius=3)
            online_label = hint_font.render("Online mode (sign in / sign up)", True, (210, 210, 220))
            screen.blit(online_label, (online_rect.right + 10,
                                       online_rect.y + (online_rect.h - online_label.get_height()) // 2))

            chk_y = check_y + 36
            chk_rect = pygame.Rect(box_rect.x + 24, chk_y, 22, 22)
            _draw_rounded_rect(screen, (55, 55, 80), chk_rect, radius=5,
                               border=2, border_color=(180, 180, 200))
            if remember:
                inner = chk_rect.inflate(-6, -6)
                pygame.draw.rect(screen, (100, 220, 130), inner, border_radius=3)
            chk_label = hint_font.render("Remember name", True, (210, 210, 220))
            screen.blit(chk_label, (chk_rect.right + 10,
                                     chk_rect.y + (chk_rect.h - chk_label.get_height()) // 2))
        else:
            check_y = box_rect.y + 220
            online_rect = pygame.Rect(box_rect.x + 24, check_y - 10, 22, 22)
            _draw_rounded_rect(screen, (55, 55, 80), online_rect, radius=5,
                               border=2, border_color=(180, 180, 200))
            online_label = hint_font.render("Online mode (sign in / sign up)", True, (210, 210, 220))
            screen.blit(online_label, (online_rect.right + 10,
                                       online_rect.y + (online_rect.h - online_label.get_height()) // 2))

            chk_y = check_y + 36
            chk_rect = pygame.Rect(box_rect.x + 24, chk_y, 22, 22)
            _draw_rounded_rect(screen, (55, 55, 80), chk_rect, radius=5,
                               border=2, border_color=(180, 180, 200))
            if remember:
                inner = chk_rect.inflate(-6, -6)
                pygame.draw.rect(screen, (100, 220, 130), inner, border_radius=3)
            chk_label = hint_font.render("Remember name", True, (210, 210, 220))
            screen.blit(chk_label, (chk_rect.right + 10,
                                     chk_rect.y + (chk_rect.h - chk_label.get_height()) // 2))

        if error_msg:
            err_surf = hint_font.render(error_msg, True, (255, 130, 130))
            screen.blit(err_surf, (box_rect.x + 24, box_rect.y + 330 if online_mode else box_rect.y + 320))

        button_y = box_rect.y + box_h - 92
        save_rect = pygame.Rect(box_rect.x + 24, button_y, (box_w - 56) // 2, 38)
        exit_rect = pygame.Rect(save_rect.right + 8, button_y,
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

        h_surf = hint_font.render("Enter to save  •  Esc to exit", True, (130, 130, 150))
        screen.blit(h_surf, (box_rect.centerx - h_surf.get_width() // 2, button_y + 55))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                import sys
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if online_mode and not password_text:
                        error_msg = "Password required"
                    else:
                        if online_mode:
                            if not friends_client.auth_login_or_register(text.strip(), password_text):
                                error_msg = "Login failed"
                                continue
                        _do_save(text if text.strip() else "Unnamed", remember)
                        retun = text if text.strip() else "Unnamed"
                        return retun
                elif event.key == pygame.K_ESCAPE:
                    import sys
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_TAB:
                    active_field = "password" if active_field == "name" and online_mode else "name"
                elif event.key == pygame.K_BACKSPACE:
                    if online_mode and active_field == "password":
                        password_text = password_text[:-1]
                    else:
                        text = text[:-1]
                else:
                    ch = event.unicode
                    if ch and ch.isprintable():
                        if online_mode and active_field == "password" and len(password_text) < MAX_PASS_LEN:
                            password_text += ch
                        elif len(text) < MAX_NAME_LEN:
                            text += ch
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if online_rect.collidepoint(event.pos):
                    online_mode = not online_mode
                    if not online_mode:
                        password_text = ""
                        active_field = "name"
                    else:
                        active_field = "password"
                elif chk_rect.collidepoint(event.pos):
                    remember = not remember
                elif password_rect and password_rect.collidepoint(event.pos):
                    active_field = "password"
                elif input_rect.collidepoint(event.pos):
                    active_field = "name"
                elif save_rect.collidepoint(event.pos):
                    if online_mode and not password_text:
                        error_msg = "Password required"
                    else:
                        if online_mode and not friends_client.auth_login_or_register(text.strip(), password_text):
                            error_msg = "Login failed"
                            continue
                        _do_save(text if text.strip() else "Unnamed", remember)
                        retun = text if text.strip() else "Unnamed"
                        return retun
                elif exit_rect.collidepoint(event.pos):
                    import sys
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.VIDEORESIZE:
                pass


def _do_save(name, remember):
    _set_settings("name", name)
    _set_settings("rememberName", str(remember))
