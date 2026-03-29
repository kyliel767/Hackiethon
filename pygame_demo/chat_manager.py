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
        self.status = None
        
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
            self.status = status
            # ----------- FOR DEBUGGYING PURPOSES -----------
            print(f"Extracted status for {self.npc_name}: {status}")
            # -----------------------------------------------
            self.status = status

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
                # 1. Backspace is always allowed
                if event.key == pygame.K_BACKSPACE:
                    self.player_input = self.player_input[:-1]

                # 2. Enter sends ONLY the allowed text to the AI
                elif event.key == pygame.K_RETURN and self.player_input.strip():
                    # We pass the cleaned, visible input to the AI
                    message_to_send = self.player_input.strip()
                    
                    # Log the player's message to the history list
                    self.messages.append("> " + message_to_send)
                    
                    # Start AI call and wipe the input field instantly
                    self.start_npc_response(message_to_send)
                    self.player_input = "" 

                # 3. Text Input Gatekeeper
                elif event.unicode and event.unicode.isprintable():
                    # Define boundaries
                    padding_x = 28
                    max_width = self.chat_panel_rect.width - (padding_x * 2)
                    
                    # PRE-CHECK: What would the line look like if we added this key?
                    test_string = "> " + self.player_input + event.unicode
                    text_width, _ = self.font.size(test_string)

                    # Only add the character to the actual variable if it fits
                    if text_width <= max_width:
                        self.player_input += event.unicode
                    # Else: Do nothing. The character is discarded and never stored.
        # Maintain state
        if self.npc_name == "Little Red Riding Hood":
            return "chat"
        elif self.npc_name == "Gnome":
            return "minigame"
        else:
            raise ValueError("Unknown NPC name in ChatManager")
    

# for little red riding hood
    def extract_status_from_response(self, text):
        for status in ["accepted", "rejected", "ongoing"]:
            tag = f"[STATUS:{status}]"
            if tag in text:
                return text.replace(tag, "").strip(), status
        return text.strip(), "ongoing"
    
# for the gnome 
    def extract_number_from_response(self, text):
        print(f"*********** Extracting text from Gnome response: {text} ***********")
        for status in ["higher", "lower", "accepted"]:
            tag = f"[STATUS:{status}]"
            if tag in text:
                return text.replace(tag, "").strip(), status
        return text.strip(), "ongoing"

    def ask_npc(self, player_text):
        self.waiting_for_ai = True
        self.conversation_history.append({"role": "user", "content": player_text})
        ai_response = self.ai_client.send_messages(self.conversation_history)
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        if self.npc_name == "Little Red Riding Hood":
            clean, status = self.extract_status_from_response(ai_response)
        elif self.npc_name == "Gnome":
            clean, status = self.extract_number_from_response(ai_response)
            self.status = status
        else:
            ValueError("Error with npc")
        self.waiting_for_ai = False
        return clean, status

    def draw(self):
        # Draw chat UI
        self.screen.blit(self.chat_background, (0,0))
        self.screen.blit(self.npc_chat, self.chat_npc_rect)
        self.screen.blit(self.chat_panel, self.chat_panel_rect)
        self.screen.blit(self.name_panel, self.name_panel_rect)

        # Draw NPC Name
        name_surface = self.font.render(self.npc_name, True, (255, 255, 255))
        name_rect = name_surface.get_rect(center=self.name_panel_rect.center)
        self.screen.blit(name_surface, name_rect)

        # Layout math
        padding_x, padding_y = 28, 24
        line_height = self.font.get_linesize() + 2
        max_width = self.chat_panel_rect.width - (padding_x * 2)
        
        # Calculate positions
        npc_y = self.chat_panel_rect.y + padding_y
        # FIXED POSITION: Anchored to the bottom of the chat panel
        input_y = self.chat_panel_rect.bottom - padding_y - line_height

        # --- NPC / THINKING SLOT ---
        if self.waiting_for_ai:
            # Replaces previous NPC text with "Thinking..."
            thinking_surface = self.font.render("Thinking...", True, (180, 180, 180))
            self.screen.blit(thinking_surface, (self.chat_panel_rect.x + padding_x, npc_y))
        else:
            # Only show the latest NPC message
            npc_msgs = [m for m in self.messages if m.startswith("NPC:")]
            if npc_msgs:
                latest = npc_msgs[-1].replace("NPC: ", "")
                curr_y = npc_y
                for line in self.wrap_text(latest, self.font, max_width):
                    # Only draw if the text hasn't reached the fixed input slot
                    if curr_y < input_y - 10:
                        txt = self.font.render(line, True, (255, 255, 255))
                        self.screen.blit(txt, (self.chat_panel_rect.x + padding_x, curr_y))
                        curr_y += line_height

        # --- PLAYER INPUT SLOT ---
        # Disappears while AI is thinking
        if not self.waiting_for_ai:
            input_surface = self.font.render("> " + self.player_input, True, (255, 255, 255))
            self.screen.blit(input_surface, (self.chat_panel_rect.x + padding_x, input_y))
        
    def check_status(self, current_state):
        print(f"Checking status for {self.npc_name}: {self.status}")
        if self.npc_name == "Little Red Riding Hood":
            if self.status == "accepted":
                return "win"
            if self.status == "rejected":
                return "game_over"
        elif self.npc_name == "Gnome":
            if self.status == "accepted":
                return "house"
                
        return current_state