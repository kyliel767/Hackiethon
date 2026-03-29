import time

text_state = {
    "current_line": 0,
    "displayed_chars": 0,
    "last_update": time.time(),
    "done": False
}

def draw_animated_text(surface, lines, font, x, y, color=(255, 255, 255), line_spacing=40, char_speed=0.05, line_delay=0.8):
    state = text_state

    # update
    if not state["done"]:
        current_time = time.time()
        if state["current_line"] < len(lines):
            current_full_line = lines[state["current_line"]]
            if state["displayed_chars"] < len(current_full_line):
                if current_time - state["last_update"] > char_speed:
                    state["displayed_chars"] += 1
                    state["last_update"] = current_time
            else:
                if current_time - state["last_update"] > line_delay:
                    state["current_line"] += 1
                    state["displayed_chars"] = 0
                    state["last_update"] = current_time
        else:
            state["done"] = True

    # draw
    for i in range(state["current_line"]):
        text_surface = font.render(lines[i], False, color)
        text_rect = text_surface.get_rect(centerx=x, y=y + i * line_spacing)
        surface.blit(text_surface, text_rect)

    if state["current_line"] < len(lines):
        current = lines[state["current_line"]][:state["displayed_chars"]]
        text_surface = font.render(current, False, color)
        text_rect = text_surface.get_rect(centerx=x, y=y + state["current_line"] * line_spacing)
        surface.blit(text_surface, text_rect)
        