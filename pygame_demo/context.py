import pygame
import math

#ai copied
# Scene state
scene_index = 0
displayed_text = ""
char_index = 0
char_timer = 0
scenes = []

def load_scenes(screen, scenes_data):
    global scenes
    for scene in scenes_data:
        bg = pygame.image.load(scene["background"])
        bg = pygame.transform.scale(bg, (screen.get_width(), screen.get_height()))
        scenes.append({
            "background": bg,
            "text": scene["text"]
        })

def update(screen, font):
    global displayed_text, char_index, char_timer

    current = scenes[scene_index]
    screen.blit(current["background"], (0, 0))

    # Type out text
    char_timer += 1
    if char_timer >= 3 and char_index < len(current["text"]):
        displayed_text += current["text"][char_index]
        char_index += 1
        char_timer = 0

    # Draw text
    draw_wrapped_text(screen, font, displayed_text, 50, screen.get_height() - 200)

    # Show prompt when done typing
    if char_index >= len(current["text"]):
        bounce_offset = math.sin(pygame.time.get_ticks() * 0.003) * 10
        if scene_index < len(scenes) - 1:
            prompt = font.render("Press ENTER for next scene...", True, (255, 255, 255))
        else:
            prompt = font.render("Press ENTER to start game...", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(center=(screen.get_width()//2, screen.get_height() - 40 + int(bounce_offset)))
        screen.blit(prompt, prompt_rect)

def handle_input():
    global scene_index, displayed_text, char_index, char_timer

    # If still typing, skip to end
    if char_index < len(scenes[scene_index]["text"]):
        displayed_text = scenes[scene_index]["text"]
        char_index = len(displayed_text)
        return "narrator"

    # Go to next scene
    elif scene_index < len(scenes) - 1:
        scene_index += 1
        displayed_text = ""
        char_index = 0
        char_timer = 0
        return "narrator"

    # Last scene — start game
    else:
        return "game"

def draw_wrapped_text(screen, font, text, x, y):
    words = text.split()
    lines = []
    current_line = ""
    max_width = screen.get_width() - 100

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] < max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + " "
    lines.append(current_line)

    for i, line in enumerate(lines):
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (x, y + i * 30))