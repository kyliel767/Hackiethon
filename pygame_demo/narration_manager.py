import pygame

# -------
# Narration text
# -------
HOUSE_NARRATION = """Congratulations! You've successfully navigated the forest and reached the cottage. The deed is done. Grandmother was... delicious. With your 'lunch' safely tucked away and her nightgown snugly fitted, the stage is set. You look surprisingly convincing in pink! Now, steel yourself... Your granddaughter and ticket to freedom is right there. Don't let your stomach growl!"""

FOREST_NARRATION = """Wow! I didn’t expect to have another person here so soon... You woke up from that truck collision quicker than the others... I’m guessing you want to return to your world and not be a wolf forever, right? All you have to do is change the ending of Little Red Riding Hood so that the wolf wins in the end. If you don’t change the ending... well, that’s for you to find out... Your first task is to cross the forest so that you reach Grandma’s house."""



#------------
# narration manager
#------------
class NarrationManager:
    def __init__(self, screen, font, panel_image):
        self.screen = screen
        self.font = font
        
        # assets
        self.panel_img = panel_image
        # center the panel in the middle of the screen
        self.panel_rect = self.panel_img.get_rect(center=(510, 390))
        
        # game state
        self.full_text = ""
        self.char_index = 0
        self.speed = 2 # frames per character
        self.timer = 0
        self.is_active = False

    def start_narration(self, text):
        # reset typewriter variables for new text
        self.full_text = text
        self.char_index = 0
        self.is_active = True

    def is_finished(self):
        # returns true if the typewriter effect has reached the end
        return self.char_index >= len(self.full_text)

    def wrap_text(self, text, font, max_width):
        # reused logic from chat_manager for consistent text flow
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            if current:
                test = current + " " + word
            else:
                test = word
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def update(self):
        # handle typewriter timing
        if self.is_active and not self.is_finished():
            self.timer += 1
            if self.timer >= self.speed:
                self.char_index += 1
                self.timer = 0

    def draw(self):
        # only render if narration state is active
        if not self.is_active:
            return
        
        # 1. draw the panel centered on screen
        self.screen.blit(self.panel_img, self.panel_rect)
        
        # 2. get the current "typed" portion of the text
        current_chunk = self.full_text[:self.char_index]
        
        # 3. wrap the text based on panel width
        padding = 50
        max_w = self.panel_rect.width - (padding * 2)
        wrapped_lines = self.wrap_text(current_chunk, self.font, max_w)
        
        # 4. render lines relative to the panel's top-left
        line_height = self.font.get_linesize() + 4
        for i, line in enumerate(wrapped_lines):
            text_surf = self.font.render(line, True, (255, 255, 255))
            self.screen.blit(text_surf, (self.panel_rect.x + padding, self.panel_rect.y + padding + (i * line_height)))

        # 5. draw blinking prompt once text is fully revealed
        if self.is_finished() and (pygame.time.get_ticks() // 500) % 2 == 0:
            prompt = self.font.render("[ Press ENTER ]", True, (200, 200, 200))
            p_rect = prompt.get_rect(centerx=self.panel_rect.centerx, bottom=self.panel_rect.bottom - 25)
            self.screen.blit(prompt, p_rect)