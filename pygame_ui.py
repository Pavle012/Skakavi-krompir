"""
pygame_ui.py  —  Pure-pygame UI helpers for Skakavi Krompir
Provides blocking screen loops for common dialogs (text input, scrollable
lists, info screens) that overlay on whatever pygame surface is current.
"""

import pygame
import dependencies

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_screen():
    return pygame.display.get_surface()

def _font(size):
    return pygame.font.Font(dependencies.get_font_path(), size)

def _draw_rounded_rect(surface, color, rect, radius=12, border=0, border_color=None):
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surface, border_color, rect, width=border, border_radius=radius)

def _dim_overlay(surface):
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    surface.blit(overlay, (0, 0))

def _center_box(surface, w, h):
    sw, sh = surface.get_size()
    return pygame.Rect(sw // 2 - w // 2, sh // 2 - h // 2, w, h)


# ---------------------------------------------------------------------------
# Native file dialog (tkinter, hidden window — no customtkinter needed)
# ---------------------------------------------------------------------------

def pick_file(title="Select File", filetypes=(("All files", "*.*"),)):
    """Open a native OS file-picker dialog. Returns path string or ''."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(title=title, filetypes=filetypes)
        root.destroy()
        return path or ""
    except Exception as e:
        print(f"File dialog error: {e}")
        return ""


# ---------------------------------------------------------------------------
# Checkbox widget
# ---------------------------------------------------------------------------

class Checkbox:
    def __init__(self, x, y, label, checked=False, font_size=20):
        self.x = x
        self.y = y
        self.label = label
        self.checked = checked
        self.size = 22
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self._font = _font(font_size)

    def draw(self, surface):
        _draw_rounded_rect(surface, (60, 60, 80), self.rect, radius=5, border=2, border_color=(200, 200, 200))
        if self.checked:
            inner = self.rect.inflate(-6, -6)
            pygame.draw.rect(surface, (100, 220, 130), inner, border_radius=3)
        text_surf = self._font.render(self.label, True, (230, 230, 230))
        surface.blit(text_surf, (self.x + self.size + 10, self.y + (self.size - text_surf.get_height()) // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.checked = not self.checked
                return True
        return False


# ---------------------------------------------------------------------------
# draw_text_input  — blocking text-entry overlay
# ---------------------------------------------------------------------------

def draw_text_input(title, prompt, default=""):
    """
    Show a full-screen-dim text-input dialog.
    Returns the entered string, or None if cancelled (Escape / window close).
    """
    screen = _get_screen()
    sw, sh = screen.get_size()

    title_font = _font(40)
    prompt_font = _font(22)
    input_font = _font(26)
    hint_font = _font(16)

    box_w, box_h = min(560, sw - 60), 240
    box_rect = _center_box(screen, box_w, box_h)

    text = default
    cursor_visible = True
    cursor_timer = 0

    # Capture a snapshot of the current screen as background
    background = screen.copy()

    clock = pygame.time.Clock()
    while True:
        # Blit frozen background
        screen.blit(background, (0, 0))
        _dim_overlay(screen)

        _draw_rounded_rect(screen, (30, 30, 45), box_rect, radius=16,
                           border=2, border_color=(100, 100, 160))

        # Title
        t_surf = title_font.render(title, True, (255, 255, 255))
        screen.blit(t_surf, (box_rect.centerx - t_surf.get_width() // 2, box_rect.y + 18))

        # Prompt
        p_surf = prompt_font.render(prompt, True, (190, 190, 210))
        screen.blit(p_surf, (box_rect.x + 20, box_rect.y + 70))

        # Input area
        input_rect = pygame.Rect(box_rect.x + 20, box_rect.y + 100, box_rect.w - 40, 44)
        _draw_rounded_rect(screen, (50, 50, 70), input_rect, radius=8,
                           border=2, border_color=(130, 130, 200))

        display_text = text
        t_surf2 = input_font.render(display_text, True, (255, 255, 255))
        # Scroll text if too wide
        if t_surf2.get_width() > input_rect.w - 20:
            # Show the tail
            for i in range(len(display_text)):
                t_surf2 = input_font.render(display_text[i:], True, (255, 255, 255))
                if t_surf2.get_width() <= input_rect.w - 20:
                    break
        screen.blit(t_surf2, (input_rect.x + 10, input_rect.y + (input_rect.h - t_surf2.get_height()) // 2))

        # Cursor
        cursor_timer += clock.get_time()
        if cursor_timer >= 500:
            cursor_visible = not cursor_visible
            cursor_timer = 0
        if cursor_visible:
            cx = input_rect.x + 10 + t_surf2.get_width() + 1
            cy1 = input_rect.y + 6
            cy2 = input_rect.y + input_rect.h - 6
            pygame.draw.line(screen, (255, 255, 255), (cx, cy1), (cx, cy2), 2)

        # Hint
        hint = hint_font.render("Enter to confirm  •  Escape to cancel", True, (140, 140, 160))
        screen.blit(hint, (box_rect.centerx - hint.get_width() // 2, box_rect.bottom - 28))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return text
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                else:
                    if event.unicode and event.unicode.isprintable():
                        text += event.unicode
            if event.type == pygame.VIDEORESIZE:
                background = screen.copy()
                sw, sh = screen.get_size()
                box_rect = _center_box(screen, box_w, box_h)


# ---------------------------------------------------------------------------
# draw_scrollable_list  — generic scrollable list overlay
# ---------------------------------------------------------------------------

def draw_scrollable_list(title, rows, columns, action_buttons_per_row=None,
                         close_label="Close", extra_info=None):
    """
    Show a scrollable list dialog.

    Parameters
    ----------
    title : str
    rows  : list of tuples  —  one tuple per row, values match `columns`
    columns : list of (header_str, weight_float)  — controls column layout
    action_buttons_per_row : list[dict] optionally per row, each dict:
        {"label": str, "color": tuple, "hover": tuple, "value": any}
        The callback returns (row_index, button_value).
    close_label : str
    extra_info : list[str]  — lines shown above the list

    Returns
    -------
    None always (caller decides what to do with selected item separately)
    The function calls `on_select(row_idx, btn_value)` when a row action is clicked.
    Actually returns (row_idx, btn_value) or None on close.
    """
    screen = _get_screen()
    sw, sh = screen.get_size()
    background = screen.copy()

    title_font = _font(36)
    header_font = _font(18)
    row_font = _font(16)
    btn_font = _font(14)
    info_font = _font(18)

    PADDING = 30
    box_w = min(700, sw - 40)
    box_h = min(sh - 60, 560)
    box_rect = _center_box(screen, box_w, box_h)

    ROW_H = 44
    HEADER_H = 36
    BTN_W = 80
    BTN_H = 30
    BTN_GAP = 6

    content_x = box_rect.x + PADDING
    content_w = box_rect.w - PADDING * 2

    # Scrolling
    scroll_offset = 0
    num_rows = len(rows)
    btn_defs = action_buttons_per_row or []

    # Compute column widths from weights
    btn_area_w = len(btn_defs) * (BTN_W + BTN_GAP) if btn_defs else 0
    text_area_w = content_w - btn_area_w
    total_weight = sum(w for _, w in columns) or 1
    col_widths = [int(text_area_w * w / total_weight) for _, w in columns]

    # Extra info lines height
    info_h = len(extra_info) * 28 if extra_info else 0

    # Scrollable area
    TITLE_SECTION_H = 60 + info_h + HEADER_H
    CLOSE_BTN_H = 54
    list_area_h = box_h - TITLE_SECTION_H - CLOSE_BTN_H

    # Pre-render buttons
    def make_btn_rect(row_screen_y, btn_idx):
        bx = box_rect.right - PADDING - btn_area_w + btn_idx * (BTN_W + BTN_GAP)
        by = row_screen_y + (ROW_H - BTN_H) // 2
        return pygame.Rect(bx, by, BTN_W, BTN_H)

    clock = pygame.time.Clock()
    hovered_row = -1

    while True:
        screen.blit(background, (0, 0))
        _dim_overlay(screen)
        _draw_rounded_rect(screen, (28, 28, 42), box_rect, radius=16,
                           border=2, border_color=(100, 100, 160))

        # Title
        t_surf = title_font.render(title, True, (255, 255, 255))
        screen.blit(t_surf, (box_rect.centerx - t_surf.get_width() // 2, box_rect.y + 14))

        y_cursor = box_rect.y + 60

        # Extra info
        if extra_info:
            for line in extra_info:
                l_surf = info_font.render(line, True, (220, 220, 100))
                screen.blit(l_surf, (content_x, y_cursor))
                y_cursor += 28

        # Column headers
        hx = content_x
        for (hdr, _), cw in zip(columns, col_widths):
            h_surf = header_font.render(hdr, True, (160, 160, 200))
            screen.blit(h_surf, (hx, y_cursor + 8))
            hx += cw
        pygame.draw.line(screen, (80, 80, 120),
                         (content_x, y_cursor + HEADER_H - 2),
                         (content_x + content_w, y_cursor + HEADER_H - 2), 1)
        y_cursor += HEADER_H

        # Clip list area
        list_rect = pygame.Rect(box_rect.x, y_cursor, box_rect.w, list_area_h)
        clip_region = list_rect.clip(screen.get_rect())
        screen.set_clip(clip_region)

        mouse_pos = pygame.mouse.get_pos()
        hovered_row = -1

        for i, row in enumerate(rows):
            ry = y_cursor + i * ROW_H - scroll_offset
            if ry + ROW_H < clip_region.top or ry > clip_region.bottom:
                continue
            row_rect = pygame.Rect(content_x, ry, content_w, ROW_H - 2)
            if row_rect.collidepoint(mouse_pos):
                hovered_row = i
                pygame.draw.rect(screen, (50, 50, 75), row_rect, border_radius=6)
            elif i % 2 == 0:
                pygame.draw.rect(screen, (35, 35, 52), row_rect, border_radius=6)

            # Row text columns
            rx = content_x
            for col_val, cw in zip(row, col_widths):
                cell_surf = row_font.render(str(col_val), True, (220, 220, 220))
                # Clip to column width
                screen.blit(cell_surf, (rx + 4, ry + (ROW_H - cell_surf.get_height()) // 2))
                rx += cw

            # Action buttons
            for j, bdef in enumerate(btn_defs):
                br = make_btn_rect(ry, j)
                if br.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, bdef.get("hover", (80, 80, 80)), br, border_radius=6)
                else:
                    pygame.draw.rect(screen, bdef.get("color", (60, 60, 60)), br, border_radius=6)
                bs = btn_font.render(bdef["label"], True, (255, 255, 255))
                screen.blit(bs, (br.centerx - bs.get_width() // 2,
                                 br.centery - bs.get_height() // 2))

        screen.set_clip(None)

        # Scrollbar
        total_list_h = num_rows * ROW_H
        if total_list_h > list_area_h:
            sb_h = max(30, int(list_area_h * list_area_h / total_list_h))
            sb_y = y_cursor + int(scroll_offset / total_list_h * list_area_h)
            sb_rect = pygame.Rect(box_rect.right - 10, sb_y, 6, sb_h)
            pygame.draw.rect(screen, (100, 100, 140), sb_rect, border_radius=3)

        # Close button
        close_y = box_rect.bottom - CLOSE_BTN_H + 8
        close_rect = pygame.Rect(box_rect.centerx - 80, close_y, 160, 36)
        close_hover = close_rect.collidepoint(mouse_pos)
        _draw_rounded_rect(screen, (70, 30, 30) if close_hover else (50, 20, 20),
                           close_rect, radius=8)
        cs = btn_font.render(close_label, True, (255, 255, 255))
        screen.blit(cs, (close_rect.centerx - cs.get_width() // 2,
                         close_rect.centery - cs.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if close_rect.collidepoint(event.pos):
                        return None
                    # Check row action buttons
                    for i, row in enumerate(rows):
                        ry = y_cursor + i * ROW_H - scroll_offset
                        for j, bdef in enumerate(btn_defs):
                            br = make_btn_rect(ry, j)
                            if br.collidepoint(event.pos):
                                return (i, bdef["value"])
                elif event.button == 4:  # scroll up
                    scroll_offset = max(0, scroll_offset - ROW_H * 3)
                elif event.button == 5:  # scroll down
                    max_scroll = max(0, num_rows * ROW_H - list_area_h)
                    scroll_offset = min(max_scroll, scroll_offset + ROW_H * 3)
            if event.type == pygame.VIDEORESIZE:
                background = screen.copy()
                sw, sh = screen.get_size()
                box_rect = _center_box(screen, box_w, box_h)


# ---------------------------------------------------------------------------
# draw_settings_screen  — rich settings screen
# ---------------------------------------------------------------------------

def draw_settings_screen(settings_defs, current_values):
    """
    Show a settings screen with various control types.

    settings_defs: list of dicts, each with:
      - type: "int" | "float" | "select" | "bool" | "action" | "slider" | "section"
      - key: settings key (str)
      - label: display label (str)
      - options: list of str (for "select")
      - min/max: for "int"/"float"/"slider"
      - action: callable (for "action" type)
      - label_only: str (for "section" type — just a divider label)

    current_values: dict key->value (will be modified in-place)

    Returns the updated current_values dict when closed.
    """
    screen = _get_screen()
    sw, sh = screen.get_size()
    background = screen.copy()

    title_font = _font(38)
    label_font = _font(20)
    val_font = _font(20)
    btn_font = _font(16)
    section_font = _font(16)

    PADDING = 30
    BOX_W = min(520, sw - 40)
    BOX_H = min(sh - 40, 620)
    box_rect = _center_box(screen, BOX_W, BOX_H)

    ITEM_H = 50
    SECTION_H = 32
    TITLE_H = 60
    CLOSE_BTN_H = 52

    list_area_top = box_rect.y + TITLE_H
    list_area_bottom = box_rect.bottom - CLOSE_BTN_H
    list_area_h = list_area_bottom - list_area_top
    list_rect = pygame.Rect(box_rect.x, list_area_top, BOX_W, list_area_h)

    scroll_offset = 0
    dragging_slider = None  # key of slider being dragged

    def item_heights():
        heights = []
        for d in settings_defs:
            if d["type"] == "section":
                heights.append(SECTION_H)
            else:
                heights.append(ITEM_H)
        return heights

    heights = item_heights()
    total_content_h = sum(heights)

    clock = pygame.time.Clock()

    while True:
        screen.blit(background, (0, 0))
        _dim_overlay(screen)
        _draw_rounded_rect(screen, (28, 28, 42), box_rect, radius=16,
                           border=2, border_color=(100, 100, 160))

        # Title
        t_surf = title_font.render("Settings", True, (255, 255, 255))
        screen.blit(t_surf, (box_rect.centerx - t_surf.get_width() // 2, box_rect.y + 14))

        # Clip to list area
        screen.set_clip(list_rect.clip(screen.get_rect()))

        mouse_pos = pygame.mouse.get_pos()
        y_cursor = list_area_top - scroll_offset
        item_rects = []  # (def_idx, screen_rect)

        for idx, (d, h) in enumerate(zip(settings_defs, heights)):
            iy = y_cursor
            item_rect = pygame.Rect(box_rect.x + PADDING, iy, BOX_W - PADDING * 2, h)
            item_rects.append((idx, item_rect))

            t = d["type"]

            if t == "section":
                label_surf = section_font.render(d.get("label", ""), True, (150, 150, 200))
                screen.blit(label_surf, (item_rect.x, iy + (SECTION_H - label_surf.get_height()) // 2))
                pygame.draw.line(screen, (70, 70, 110),
                                 (item_rect.x, iy + SECTION_H - 4),
                                 (item_rect.right, iy + SECTION_H - 4), 1)
            else:
                # Row highlight
                row_rect = pygame.Rect(box_rect.x + 8, iy + 3, BOX_W - 16, h - 6)
                if t != "slider" and row_rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (45, 45, 65), row_rect, border_radius=6)

                # Label
                lbl = label_font.render(d["label"], True, (210, 210, 210))
                screen.blit(lbl, (item_rect.x, iy + (ITEM_H - lbl.get_height()) // 2))

                right_x = item_rect.right
                key = d.get("key")
                val = current_values.get(key) if key else None

                if t == "bool":
                    # Toggle checkbox style button
                    tog_rect = pygame.Rect(right_x - 70, iy + (ITEM_H - 28) // 2, 70, 28)
                    is_on = str(val).lower() in ("true", "1", "yes")
                    bg = (46, 160, 90) if is_on else (80, 30, 30)
                    pygame.draw.rect(screen, bg, tog_rect, border_radius=14)
                    tog_text = val_font.render("ON" if is_on else "OFF", True, (255, 255, 255))
                    screen.blit(tog_text, (tog_rect.centerx - tog_text.get_width() // 2,
                                           tog_rect.centery - tog_text.get_height() // 2))

                elif t == "select":
                    options = d.get("options", [])
                    cur_idx = options.index(val) if val in options else 0
                    # Left arrow
                    la = pygame.Rect(right_x - 180, iy + (ITEM_H - 28) // 2, 28, 28)
                    ra = pygame.Rect(right_x - 30, iy + (ITEM_H - 28) // 2, 28, 28)
                    la_hover = la.collidepoint(mouse_pos)
                    ra_hover = ra.collidepoint(mouse_pos)
                    pygame.draw.rect(screen, (80, 80, 120) if la_hover else (55, 55, 85),
                                     la, border_radius=6)
                    pygame.draw.rect(screen, (80, 80, 120) if ra_hover else (55, 55, 85),
                                     ra, border_radius=6)
                    al = val_font.render("<", True, (255, 255, 255))
                    ar = val_font.render(">", True, (255, 255, 255))
                    screen.blit(al, (la.centerx - al.get_width() // 2, la.centery - al.get_height() // 2))
                    screen.blit(ar, (ra.centerx - ar.get_width() // 2, ra.centery - ar.get_height() // 2))
                    opt_surf = val_font.render(options[cur_idx] if options else "", True, (220, 220, 100))
                    screen.blit(opt_surf, (right_x - 150, iy + (ITEM_H - opt_surf.get_height()) // 2))

                elif t in ("int", "float"):
                    mi = d.get("min", 0)
                    ma = d.get("max", 999)
                    la = pygame.Rect(right_x - 140, iy + (ITEM_H - 28) // 2, 28, 28)
                    ra = pygame.Rect(right_x - 30, iy + (ITEM_H - 28) // 2, 28, 28)
                    la_hover = la.collidepoint(mouse_pos)
                    ra_hover = ra.collidepoint(mouse_pos)
                    pygame.draw.rect(screen, (80, 80, 120) if la_hover else (55, 55, 85),
                                     la, border_radius=6)
                    pygame.draw.rect(screen, (80, 80, 120) if ra_hover else (55, 55, 85),
                                     ra, border_radius=6)
                    al = val_font.render("-", True, (255, 255, 255))
                    ar = val_font.render("+", True, (255, 255, 255))
                    screen.blit(al, (la.centerx - al.get_width() // 2, la.centery - al.get_height() // 2))
                    screen.blit(ar, (ra.centerx - ar.get_width() // 2, ra.centery - ar.get_height() // 2))
                    dv = d.get("display_fmt", "{}").format(val) if val is not None else "?"
                    v_surf = val_font.render(str(dv), True, (220, 220, 100))
                    screen.blit(v_surf, (right_x - 110, iy + (ITEM_H - v_surf.get_height()) // 2))

                elif t == "slider":
                    mi = d.get("min", 0.0)
                    ma = d.get("max", 1.0)
                    SL_W = 160
                    sl_rect = pygame.Rect(right_x - SL_W - 10, iy + (ITEM_H - 12) // 2, SL_W, 12)
                    pygame.draw.rect(screen, (60, 60, 80), sl_rect, border_radius=6)
                    try:
                        frac = (float(val) - mi) / (ma - mi)
                    except (TypeError, ZeroDivisionError):
                        frac = 0
                    frac = max(0.0, min(1.0, frac))
                    fill_rect = pygame.Rect(sl_rect.x, sl_rect.y, int(sl_rect.w * frac), sl_rect.h)
                    pygame.draw.rect(screen, (100, 180, 255), fill_rect, border_radius=6)
                    knob_x = sl_rect.x + int(sl_rect.w * frac)
                    knob_rect = pygame.Rect(knob_x - 8, sl_rect.centery - 8, 16, 16)
                    pygame.draw.circle(screen, (200, 220, 255), knob_rect.center, 8)
                    v_surf = val_font.render(f"{float(val):.2f}" if val is not None else "?",
                                             True, (220, 220, 100))
                    screen.blit(v_surf, (right_x - SL_W - 60, iy + (ITEM_H - v_surf.get_height()) // 2))

                elif t == "action":
                    act_rect = pygame.Rect(right_x - 130, iy + (ITEM_H - 30) // 2, 130, 30)
                    hover = act_rect.collidepoint(mouse_pos)
                    pygame.draw.rect(screen, (70, 70, 130) if hover else (50, 50, 100),
                                     act_rect, border_radius=8)
                    a_surf = btn_font.render(d.get("btn_label", "…"), True, (255, 255, 255))
                    screen.blit(a_surf, (act_rect.centerx - a_surf.get_width() // 2,
                                         act_rect.centery - a_surf.get_height() // 2))

            y_cursor += h

        screen.set_clip(None)

        # Scrollbar
        if total_content_h > list_area_h:
            sb_h = max(30, int(list_area_h * list_area_h / total_content_h))
            sb_y = list_area_top + int(scroll_offset / total_content_h * list_area_h)
            sb_rect = pygame.Rect(box_rect.right - 10, sb_y, 6, sb_h)
            pygame.draw.rect(screen, (100, 100, 140), sb_rect, border_radius=3)

        # Close button
        close_y = list_area_bottom + 10
        close_rect = pygame.Rect(box_rect.centerx - 80, close_y, 160, 34)
        close_hover = close_rect.collidepoint(mouse_pos)
        _draw_rounded_rect(screen, (70, 30, 30) if close_hover else (50, 20, 20),
                           close_rect, radius=8)
        csl = btn_font.render("Close", True, (255, 255, 255))
        screen.blit(csl, (close_rect.centerx - csl.get_width() // 2,
                           close_rect.centery - csl.get_height() // 2))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return current_values
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return current_values
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if close_rect.collidepoint(event.pos):
                    return current_values
                # Hit-test items
                y_cursor2 = list_area_top - scroll_offset
                for idx, (d, h) in enumerate(zip(settings_defs, heights)):
                    iy = y_cursor2
                    t = d["type"]
                    key = d.get("key")
                    val = current_values.get(key) if key else None
                    item_rect = pygame.Rect(box_rect.x + PADDING, iy, BOX_W - PADDING * 2, h)
                    right_x = item_rect.right

                    # Only hit items within the clipping region
                    if iy + h > list_area_top and iy < list_area_bottom:
                        if t == "bool":
                            tog_rect = pygame.Rect(right_x - 70, iy + (ITEM_H - 28) // 2, 70, 28)
                            if tog_rect.collidepoint(event.pos):
                                is_on = str(val).lower() in ("true", "1", "yes")
                                current_values[key] = str(not is_on)
                        elif t == "select":
                            options = d.get("options", [])
                            cur_idx = options.index(val) if val in options else 0
                            la = pygame.Rect(right_x - 180, iy + (ITEM_H - 28) // 2, 28, 28)
                            ra = pygame.Rect(right_x - 30, iy + (ITEM_H - 28) // 2, 28, 28)
                            if la.collidepoint(event.pos) and options:
                                current_values[key] = options[(cur_idx - 1) % len(options)]
                            elif ra.collidepoint(event.pos) and options:
                                current_values[key] = options[(cur_idx + 1) % len(options)]
                        elif t in ("int", "float"):
                            step = d.get("step", 1)
                            mi = d.get("min", 0)
                            ma = d.get("max", 9999)
                            la = pygame.Rect(right_x - 140, iy + (ITEM_H - 28) // 2, 28, 28)
                            ra = pygame.Rect(right_x - 30, iy + (ITEM_H - 28) // 2, 28, 28)
                            try:
                                num = float(val) if t == "float" else int(val)
                            except (TypeError, ValueError):
                                num = d.get("default", 0)
                            if la.collidepoint(event.pos):
                                num = max(mi, num - step)
                                current_values[key] = str(int(num) if t == "int" else round(num, 3))
                            elif ra.collidepoint(event.pos):
                                num = min(ma, num + step)
                                current_values[key] = str(int(num) if t == "int" else round(num, 3))
                        elif t == "action":
                            act_rect = pygame.Rect(right_x - 130, iy + (ITEM_H - 30) // 2, 130, 30)
                            if act_rect.collidepoint(event.pos):
                                action = d.get("action")
                                if action:
                                    action()
                    y_cursor2 += h

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Slider drag start
                y_cursor2 = list_area_top - scroll_offset
                for d, h in zip(settings_defs, heights):
                    iy = y_cursor2
                    if d["type"] == "slider" and iy + h > list_area_top and iy < list_area_bottom:
                        key = d.get("key")
                        right_x = box_rect.x + PADDING + BOX_W - PADDING * 2
                        SL_W = 160
                        sl_rect = pygame.Rect(right_x - SL_W - 10, iy + (ITEM_H - 12) // 2, SL_W, 12)
                        if sl_rect.collidepoint(event.pos):
                            dragging_slider = key
                            _update_slider(d, current_values, event.pos, sl_rect)
                    y_cursor2 += h

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_slider = None

            if event.type == pygame.MOUSEMOTION and dragging_slider:
                y_cursor2 = list_area_top - scroll_offset
                for d, h in zip(settings_defs, heights):
                    if d.get("key") == dragging_slider:
                        right_x = box_rect.x + PADDING + BOX_W - PADDING * 2
                        SL_W = 160
                        sl_rect = pygame.Rect(right_x - SL_W - 10, 0, SL_W, 12)
                        # Approximate y position
                        sl_rect.y = y_cursor2 + (ITEM_H - 12) // 2
                        _update_slider(d, current_values, event.pos, sl_rect)
                        break
                    y_cursor2 += h

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    scroll_offset = max(0, scroll_offset - ITEM_H * 2)
                elif event.button == 5:
                    max_scroll = max(0, total_content_h - list_area_h)
                    scroll_offset = min(max_scroll, scroll_offset + ITEM_H * 2)

            if event.type == pygame.VIDEORESIZE:
                background = screen.copy()
                sw, sh = screen.get_size()
                box_rect = _center_box(screen, BOX_W, BOX_H)
                list_rect = pygame.Rect(box_rect.x, box_rect.y + TITLE_H, BOX_W, list_area_h)


def _update_slider(d, current_values, mouse_pos, sl_rect):
    mi = d.get("min", 0.0)
    ma = d.get("max", 1.0)
    key = d.get("key")
    frac = (mouse_pos[0] - sl_rect.x) / sl_rect.w
    frac = max(0.0, min(1.0, frac))
    val = mi + frac * (ma - mi)
    current_values[key] = str(round(val, 3))
