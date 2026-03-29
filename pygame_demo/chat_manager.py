import pygame
import threading

#------------
# chat manager
#------------
class ChatManager:
    def __init__(self, screen, ai_client, system_prompt, font, assets, npc_name):
        self.screen = screen
        self.ai_client = ai_client
        self.system_prompt = system_prompt
        self.font = font
        self.npc_name = npc_name
        
        # assets
        self.chat_background = assets['chat_bg']
        self.chat_panel = assets['chat_panel']
        self.chat_panel_rect = assets['chat_panel_rect']
        self.name_panel = assets['name_panel']
        self.name_panel_rect = assets['name_panel_rect']
        self.npc_chat = assets['npc_chat']
        self.chat_npc_rect = assets['chat_npc_rect']

        # game state
        self.messages = []
        self.player_input = ""
        self.waiting_for_ai = False
        self.conversation_history = []

    def enter_chat(self):
        # reset game state variables
        self.player_input = ""
        self.waiting_for_ai = False
        self.messages = []
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        # ask first line from the AI to start the conversation
        self.start_npc_response("Hi! Please say a greeting")

    def wrap_text(self, text, font, max_width):
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

    def start_npc_response(self, user_text):
        # start AI call in background so the main loop stays responsive
        def worker():
            clean, status = self.ask_npc(user_text)
            self.messages.append("NPC: " + clean)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
    

    # handles player input and returns next game state (either stays in chat or goes back to house)
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # ESC to exit chat
            if event.key == pygame.K_ESCAPE:
                if self.npc_name == "Little Red Riding Hood":
                    return "house"
                elif self.npc_name == "Gnome":
                    return "forest"

            if not self.waiting_for_ai:
                # deleting last character
                if event.key == pygame.K_BACKSPACE:
                    self.player_input = self.player_input[:-1]
                # entering input
                elif event.key == pygame.K_RETURN and self.player_input.strip():
                    self.messages.append("> " + self.player_input.strip()) # adds player's message to chat history
                    self.start_npc_response(self.player_input.strip())
                    self.player_input = "" # clear input field
                elif event.unicode and event.unicode.isprintable():
                    # add typed character to current input
                    self.player_input += event.unicode
        if self.npc_name == "Little Red Riding Hood":
                return "chat"
        elif self.npc_name == "Gnome":
                return "minigame"
        else:
            raise ValueError("Unknown NPC name in ChatManager")
    
#------------
# NOTE: THESE FUNCTIONS WILL APPLY DIFFERENTLY FOR THE MINI GAME
#------------
    def extract_status_from_response(self, text):
        for status in ["accepted", "rejected", "ongoing"]:
            tag = f"[STATUS:{status}]"
            if tag in text:
                return text.replace(tag, "").strip(), status
        return text.strip(), "ongoing"

    def ask_npc(self, player_text):
        self.waiting_for_ai = True
        self.conversation_history.append({"role": "user", "content": player_text})
        ai_response = self.ai_client.send_messages(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        clean, status = self.extract_status_from_response(ai_response)
        self.waiting_for_ai = False
        return clean, status

    def draw(self):
        self.screen.blit(self.chat_background, (0,0))
        # draw the npc sprite
        self.screen.blit(self.npc_chat, self.chat_npc_rect)
        # draw chat panel for showing messages
        self.screen.blit(self.chat_panel, self.chat_panel_rect)
        # draw npc's name panel
        self.screen.blit(self.name_panel, self.name_panel_rect)

        # draw 
        name_surface = self.font.render(self.npc_name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=self.name_panel_rect.center)
        self.screen.blit(name_surface, name_rect)

        # draw all messages in the chat panel (wrapped)
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
                if y > self.chat_panel_rect.bottom - padding_y - 10:
                    break

        # draw player input text dynamically
        if self.waiting_for_ai:
            input_surface = self.font.render("Thinking...", True, (255, 255, 255))
        else:
            input_surface = self.font.render("> " + self.player_input, True, (255, 255, 255))
        self.screen.blit(input_surface, (self.chat_panel_rect.x + padding_x, y))