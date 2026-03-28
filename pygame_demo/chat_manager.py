import pygame
import threading

#------------
# chat manager
#------------
class ChatManager:
    def __init__(self, screen, ai_client, system_prompt, font, assets):
        # initialise screen and core services
        self.screen = screen
        self.ai_client = ai_client
        self.system_prompt = system_prompt
        self.font = font
        
        # chat assets passed from main
        self.chat_background = assets['chat_bg']
        self.chat_panel = assets['chat_panel']
        self.chat_panel_rect = assets['chat_panel_rect']
        self.name_panel = assets['name_panel']
        self.name_panel_rect = assets['name_panel_rect']
        self.npc_chat = assets['npc_chat']
        self.chat_npc_rect = assets['chat_npc_rect']

        # local chat state variables
        self.messages = []
        self.player_input = ""
        self.waiting_for_ai = False
        self.conversation_history = []

    def enter_chat(self):
        # reset chat state for a fresh interaction
        self.player_input = ""
        self.waiting_for_ai = False
        self.messages = []
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        # ask first line from the AI to start the conversation
        self.start_npc_response("Hi! Please say a greeting")

    def wrap_text(self, text, font, max_width):
        # split text into multiple lines to fit within the chat panel
        words = text.split(" ")
        lines = []
        current = ""
        for word in words:
            if current:
                test = current + " " + word
            else:
                test = word
            # check if the word fits in the current line
            if font.size(test)[0] <= max_width:
                current = test
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        return lines

    def extract_status_from_response(self, text):
        # look for specific status tags in the ai's raw response
        for status in ["accepted", "rejected", "ongoing"]:
            tag = f"[STATUS:{status}]"
            if tag in text:
                # return cleaned text without the status tag
                return text.replace(tag, "").strip(), status
        return text.strip(), "ongoing"

    def ask_npc(self, player_text):
        # handle the logic of sending data to the ai client
        self.waiting_for_ai = True
        self.conversation_history.append({"role": "user", "content": player_text})
        ai_response = self.ai_client.send_messages(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        # process the response for clean dialogue and game status
        clean, status = self.extract_status_from_response(ai_response)
        self.waiting_for_ai = False
        return clean, status

    def start_npc_response(self, user_text):
        # run the ai call in a background thread to keep pygame responsive
        def worker():
            clean, status = self.ask_npc(user_text)
            self.messages.append("NPC: " + clean)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def handle_event(self, event):
        # handle keyboard input specifically for the chat interface
        if event.type == pygame.KEYDOWN:
            # return to world state if escape is pressed
            if event.key == pygame.K_ESCAPE:
                return "world"

            if not self.waiting_for_ai:
                # delete characters
                if event.key == pygame.K_BACKSPACE:
                    self.player_input = self.player_input[:-1]
                # send message on enter
                elif event.key == pygame.K_RETURN and self.player_input.strip():
                    self.messages.append("> " + self.player_input.strip())
                    self.start_npc_response(self.player_input.strip())
                    self.player_input = "" 
                # capture printable characters
                elif event.unicode and event.unicode.isprintable():
                    self.player_input += event.unicode
        # stay in chat state by default
        return "chat"

    def draw(self):
        # render the background and npc
        self.screen.blit(self.chat_background, (0,0))
        self.screen.blit(self.npc_chat, self.chat_npc_rect)
        
        # render the UI panels
        self.screen.blit(self.chat_panel, self.chat_panel_rect)
        self.screen.blit(self.name_panel, self.name_panel_rect)

        # render the npc name centered in the panel
        npc_name = "Little Red Riding Hood"
        name_surface = self.font.render(npc_name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=self.name_panel_rect.center)
        self.screen.blit(name_surface, name_rect)

        # draw all conversation lines within the text box
        padding_x = 20
        padding_y = 18
        y = self.chat_panel_rect.y + padding_y
        max_width = self.chat_panel_rect.width - (padding_x * 2)
        line_height = self.font.get_linesize() + 2

        for msg in self.messages:
            for line in self.wrap_text(msg, self.font, max_width):
                text_surface = self.font.render(line, True, (255, 255, 255))
                self.screen.blit(text_surface, (self.chat_panel_rect.x + padding_x, y))
                y += line_height
                # stop drawing if we run out of vertical space
                if y > self.chat_panel_rect.bottom - padding_y - 10:
                    break

        # show current player typing or thinking status
        if self.waiting_for_ai:
            input_surface = self.font.render("Thinking...", True, (255, 255, 255))
        else:
            input_surface = self.font.render("> " + self.player_input, True, (255, 255, 255))
        self.screen.blit(input_surface, (self.chat_panel_rect.x + padding_x, y))