import pygame
import sys
import os
import time
import threading
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Constants

SCREEN_WIDTH = 800  # Width of the game window in pixels
SCREEN_HEIGHT = 600  # Height of the game window in pixels
FPS = 60  # Target frames per second
GROQ_MODEL = "llama-3.3-70b-versatile"  # Name of AI model we want to use

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BG = (20, 24, 30)  # The dark background color for the chat screen
GRAY = (140, 140, 140)  # Used for subtle hints and dividers
INPUT_BG = (50, 56, 66)  # Background color of the text input box
USER_COLOR = (80, 160, 255)  # Blue — color used for the player's messages
AI_COLOR = (220, 180, 100)  # Gold — color used for the AI character's messages
SYSTEM_COLOR = (160, 160, 160)  # Gray — color for system messages
RED_ACCENT = (255, 100, 100)  # Red — used for rejection banners
TOP_BAR_BG = (40, 44, 52)  # Slightly lighter dark color for the top name bar

# Prompts
system_prompt = """
You are Little Red Riding Hood, a kind and curious character.
You are friendly, brave, and always eager to learn new things. 
You have a strong connection to nature and often talk to animals in the forest.
You greet your grandmother without suspicion.
After greeting your grandmother, and getting a reply from her you notice that your grandmother has great big eyes.
Your task is to figure out what is wrong with your grandmother.
If it seems that your grandmother is not actually your grandmother, you should scream for help.
Otherwise, you should have a friendly conversation with your grandmother and ask her about her day.

RULES:
- Always respond in character as Little Red Riding Hood.
- track your internal state and feelings as you interact with your grandmother.
- At the END of every response, you MUST include a status tag in square brackets indicating how the date is going:
    [STATUS:ongoing] - if you are still unsure about your grandmother and want to keep talking
    [STATUS:accepted] - if you have decided your grandmother is safe and you want to continue
    [STATUS:rejected] - if you have decided your grandmother is not safe and you want to end the conversation by screaming for help
- The status tag must be the very last thing in your message.
- Never mention or explain the status tags.
- Do not convey your actions, for example "*hug*". You are only speaking your dialogue. 
- Keep your replies to a maximum of 1 sentence. Be concise.
"""

def word_wrap(text, font, max_width):
    """Break text into lines that fit within max_width pixels."""
    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)
    return lines


def extract_status_from_response(text):
    """
    AI responses end with a hidden tag like [STATUS:accepted].
    Strips the tag and returns (cleaned_text, status_string).
    """
    for status in ["accepted", "rejected", "ongoing"]:
        tag = f"[STATUS:{status}]"
        if tag in text:
            return text.replace(tag, "").strip(), status
    return text.strip(), "ongoing"



# AI client class responsible for communicating with the GROQ api
class AIClient:
    def __init__(self):
        # Get the API key from environment variables (loaded from .env earlier)
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Missing api key")
            sys.exit(1)  # Close the game if no api key found
        # Create the Groq client object, we later use
        self.client = Groq(api_key=api_key)

    def send_messages(self, messages):
        # Send a list of chat messages to Groq and return the AI's response as a string.
        # 'messages' is a list of dicts in this format: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        # This is the standard format used by OpenAI-compatible APIs.
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,  # Choose your model
                messages=messages,  # The full conversation history
                max_tokens=300,  # Limit response length so it stays concise
                temperature=0.7,  # Higher temperature gives more creative and randomness, lower the opposite
            )
            return response.choices[0].message.content
        except Exception as error:
            # If the API call fails for any reason, return a fallback message
            # We append [STATUS:ongoing] so the game doesn't break from a missing status tag
            return f"[AI Error: {error}] [STATUS:ongoing]"


# Date scene that basically handles everything, chat log, input and allat
class DateScene:
    def __init__(self, screen, ai_client):
        self.screen = screen  # The pygame Surface representing the entire window
        self.ai = (
            ai_client  # The AIClient instance we created above for making API calls
        )

        # Set fonts
        self.font = pygame.font.SysFont("comic_sans", 16)  # Main chat text
        self.font_title = pygame.font.SysFont(
            "comic_sans", 22, bold=True
        )  # Top bar title
        self.font_small = pygame.font.SysFont("comic_sans", 14)  # Hints and small text

        # chat_log is a list of (sender, text, color) tuples for display purposes only
        self.chat_log = []
        # conversation_history is the full message list sent to the AI API each time
        # All new messages from the ai and the user are appended at the end to provide full context
        self.conversation_history = []
        # The text the player is currently typing in the input box
        self.typed_text = ""
        # How many pixels the chat has been scrolled down (for when messages overflow)
        self.scroll_offset = 0
        # Tracks where we are in the date: "loading","ongoing","accepted","rejected"
        self.date_status = "loading"
        # Flag to prevent sending another message while waiting for the AI to respond
        self.waiting_for_ai = False

        # fixed hard-coded character identity; no generation needed
        self.character_info = {
            "NAME": "Little Red Riding Hood",
            "JOB": "Fairy Tale Traveler",
        }

        # Initialize conversation with the built-in system prompt (Little Red Riding Hood special behavior)
        self.conversation_history = [{"role": "system", "content": system_prompt}]
        self.date_status = "loading"
        self.waiting_for_ai = False

        # inform player that they are talking to the fixed character
        self.add_to_chat("system", "Talking to Little Red Riding Hood.", SYSTEM_COLOR)

        # Optional: start conversation immediately with an opening request
        greeting_request = self.conversation_history + [
            {
                "role": "user",
                "content": "(Your Grandmother has just approached you. Greet her and ask how her day was.)",
            }
        ]
        ai_response = self.ai.send_messages(greeting_request)
        clean_text, status = extract_status_from_response(ai_response)
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        self.add_to_chat("ai", f"Little Red Riding Hood: {clean_text}", AI_COLOR)
        self.date_status = status or "ongoing"

    def add_to_chat(self, sender, text, color):
        # Lil helper to add da messages to the chatlog
        # Also croll to the bottom so the new message is always visible.
        self.chat_log.append((sender, text, color))
        total = self._total_chat_height()  # Total pixel height of all messages
        visible = self._visible_chat_height()  # How tall the visible chat area is
        # Scroll to the bottom: max(0, ...) prevents negative scroll
        self.scroll_offset = max(0, total - visible)

    def _visible_chat_height(self):
        # 40 for top bar and 80 for input bar
        return SCREEN_HEIGHT - 40 - 80

    def _total_chat_height(self):
        # Calculate the total height in pixels of all messages in the chat log so far
        # We need this to know when to enable scrolling and how far to scroll
        total = 0
        for _, text, _ in self.chat_log:
            # word wrap just makes long text fit in the screen width
            lines = word_wrap(text, self.font, SCREEN_WIDTH - 40)
            # Each line is 20px tall, plus 8px of padding between messages
            total += len(lines) * 20 + 8
        return total

    def _start_character_generation(self):
        # Character generation is disabled in this mode; we use the hard-coded system_prompt instead.
        return

    def _send_player_message(self, message):
        # Send the player's message to the AI in the background
        # Set waiting_for_ai to True to stop the user from more messages when the response is generating
        self.waiting_for_ai = True
        character_name = "Little Red Riding Hood"

        def do_send():
            # Add the player's message to the conversation history in API format
            self.conversation_history.append({"role": "user", "content": message})
            # Send the full conversation history so the AI has all context
            ai_response = self.ai.send_messages(self.conversation_history)
            # Save the AI's response to history so future messages retain context
            self.conversation_history.append(
                {"role": "assistant", "content": ai_response}
            )

            # Strip the status tag for display, but keep the status value
            clean_text, status = extract_status_from_response(ai_response)
            self.add_to_chat("ai", f"{character_name}: {clean_text}", AI_COLOR)
            # Update game state based on what the AI decided (ongoing/accepted/rejected)
            self.date_status = status
            # Unblock the input box — player can type again
            self.waiting_for_ai = False

        # Same as above
        thread = threading.Thread(target=do_send, daemon=True)
        thread.start()

    def update(self, events):
        # Process all input events that happened since the last frame.
        # Returns 1 of 3 strings: "win" or "retry" or "none" to see if the scene needs changing
        for event in events:
            # Check if the user scrolled
            if event.type == pygame.MOUSEWHEEL:
                # event.y is +1 for scroll up, -1 for scroll down
                # We invert it (subtract) so scrolling up moves the view up (less offset)
                self.scroll_offset -= event.y * 30
                # Clamp: scroll_offset can't go below 0 (can't scroll above the top)
                self.scroll_offset = max(0, self.scroll_offset)
                # Clamp: can't scroll below the bottom of all content
                max_scroll = max(
                    0, self._total_chat_height() - self._visible_chat_height()
                )
                self.scroll_offset = min(max_scroll, self.scroll_offset)
                continue  # Skip to the next event — no key handling needed here

            # We only care about key presses from here
            if event.type != pygame.KEYDOWN:
                continue

            # escape just quits the game
            if event.key == pygame.K_ESCAPE:
                pygame.quit()  # Shut down pygame first
                sys.exit()  # Then kill python

            if event.key == pygame.K_RETURN and self.typed_text.strip():
                # .strip() removes whitespace to prevent blank messages
                if self.date_status == "accepted":
                    # Go to da final screen
                    return "win"
                elif self.date_status == "rejected":
                    # You failed gng, start a new datescene
                    return "retry"
                elif self.date_status == "ongoing" and not self.waiting_for_ai:
                    # Send your message cuz its still going
                    message = self.typed_text.strip()
                    self.add_to_chat("user", f"You: {message}", USER_COLOR)
                    self.typed_text = ""  # Reset the input box
                    self._send_player_message(message)  # Use the function above

            elif event.key == pygame.K_BACKSPACE:
                # Remove the last character from the input box
                self.typed_text = self.typed_text[:-1]  # String splicing
            elif event.unicode and event.unicode.isprintable():
                # filter out non unicode characters
                self.typed_text += event.unicode

        return None

    def draw(self):
        # Draws the entire DateScene to the screen
        # This is called every frame, so everything is redrawn from scratch each tick

        # Give it some background color first
        self.screen.fill(DARK_BG)

        # Build the title text for the top bar
        name = self.character_info.get("NAME", "Loading...")
        job = self.character_info.get("JOB", "")
        title_text = f"{name} the {job}" if job else name

        # Big rectangle on da top as top bar
        pygame.draw.rect(self.screen, TOP_BAR_BG, (0, 0, SCREEN_WIDTH, 40))
        # font.render(text, antialias, color) returns the unicode text as a rendered surface
        # blit() basically draws onto the current surface
        self.screen.blit(self.font_title.render(title_text, True, AI_COLOR), (10, 8))
        self.screen.blit(
            self.font_small.render("[ESC] quit", True, GRAY), (SCREEN_WIDTH - 90, 12)
        )

        # We draw the chat onto a separate off-screen Surface first, then stamp it onto the screen.
        # This is needed for scrolling: we can position the chat_surface up or down to show
        # different parts, which is simpler than clipping every individual message.
        chat_top = 44  # offset from the top bar
        chat_height = self._visible_chat_height()
        # Create a new Surface the size of the visible chat area
        chat_surface = pygame.Surface((SCREEN_WIDTH, chat_height))
        chat_surface.fill(DARK_BG)

        # y starts at negative scroll_offset so scrolled-up content starts above the visible area
        y = -self.scroll_offset
        for _, text, color in self.chat_log:
            lines = word_wrap(
                text, self.font, SCREEN_WIDTH - 40
            )  # Split into displayable lines
            for line in lines:
                # Only bother rendering lines that are at least partially visible
                # This avoids drawing stuff outside of our visible range
                if -20 < y < chat_height + 20:
                    chat_surface.blit(self.font.render(line, True, color), (20, y))
                y += 20  # Move down one line height
            y += 8  # Extra padding between different messages

        # Draw the completed chat surface onto the main screen starting at chat_top
        self.screen.blit(chat_surface, (0, chat_top))

        # Render accepted or rejected banners at the end
        # Overlay on top of the chat area when the date ends
        if self.date_status == "accepted":
            # Center the banner horizontally using its pixel width
            # Logic is pretty self explanatory
            banner = self.font_title.render(
                "They agreed to date you!", True, (255, 100, 150)
            )
            self.screen.blit(
                banner,
                (SCREEN_WIDTH // 2 - banner.get_width() // 2, SCREEN_HEIGHT - 78),
            )
            hint = self.font_small.render("[ENTER] to continue", True, WHITE)
            self.screen.blit(
                hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 55)
            )

        elif self.date_status == "rejected":
            banner = self.font_title.render("They rejected you!", True, RED_ACCENT)
            self.screen.blit(
                banner,
                (SCREEN_WIDTH // 2 - banner.get_width() // 2, SCREEN_HEIGHT - 78),
            )
            hint = self.font_small.render("[ENTER] to try someone new", True, WHITE)
            self.screen.blit(
                hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 55)
            )

        # The input box is fixed at the bottom of the screen
        input_y = SCREEN_HEIGHT - 40
        # Draw the input box background
        pygame.draw.rect(self.screen, INPUT_BG, (0, input_y, SCREEN_WIDTH, 40))
        # Draw a horizontal line along the top of the input box to separate it from the rest
        pygame.draw.line(self.screen, GRAY, (0, input_y), (SCREEN_WIDTH, input_y))
        # Little ">" to show where you are typing right now
        self.screen.blit(
            self.font.render(f"> {self.typed_text}", True, WHITE), (10, input_y + 10)
        )


# Da final Scene
class FinishScene:
    def __init__(self, screen, total_seconds):
        self.screen = screen
        self.total_seconds = (
            total_seconds  # How long the player took, in seconds (float)
        )
        # Set the fonts
        self.font_big = pygame.font.SysFont("comic_sans", 42, bold=True)
        self.font_medium = pygame.font.SysFont("comic_sans", 24)
        self.font_small = pygame.font.SysFont("comic_sans", 18)

    def update(self, events):
        # Self explanatory
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "restart"  # Signal Game to go back to a new DateScene
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        return None

    def draw(self):
        self.screen.fill(DARK_BG)

        # "YOU WIN!" title, centered horizontally at y=100
        title = self.font_big.render("YOU WIN!", True, (255, 200, 100))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        subtitle = self.font_medium.render("You got a date!", True, (255, 100, 150))
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 170))

        # Format total_seconds as MM:SS and display
        minutes = int(self.total_seconds // 60)
        seconds = int(self.total_seconds % 60)
        time_surface = self.font_big.render(
            f"Time: {minutes:02d}:{seconds:02d}",
            True,
            WHITE,
        )
        self.screen.blit(
            time_surface, (SCREEN_WIDTH // 2 - time_surface.get_width() // 2, 260)
        )

        hint = self.font_small.render(
            "[ ENTER to play again  |  ESC to quit ]", True, GRAY
        )
        self.screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, 400))


# Game initialization
class Game:
    def __init__(self):
        pygame.init()  # Initialize pygame
        # Create the game window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("AI Dating Sim")  # Set the window title
        # Clock is used to enforce the FPS cap so the game doesn't run at an insane fps
        self.clock = pygame.time.Clock()
        # initialize the ai client
        self.ai_client = AIClient()
        # Start the date scene
        self.current_scene = DateScene(self.screen, self.ai_client)
        # Record when the game started
        self.timer_start = time.time()

    def run(self):
        # Da main game loop, runs forever, iterates once per frame
        while True:
            # Get all the events that happened every frame
            events = pygame.event.get()

            # Quit the game when the x is pressed
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Call the current scene's update function based off the events we got
            result = self.current_scene.update(events)
            if result is not None:
                self.handle_scene_change(
                    result
                )  # Switch to a different scene if we got a flag

            # Call the draw function of the scene each frame
            self.current_scene.draw()

            # .flip() sends the stuff we drew to the actual game window
            pygame.display.flip()

            # Wait until we've used up the time for one frame at our target FPS
            # Without this, the loop would waste a bunch of iterations since we only need 60 fps
            self.clock.tick(FPS)

    def handle_scene_change(self, result):
        # Switch the active scene based on the return of update()
        if result == "win":
            # Player won: show the finish screen with the time spent
            elapsed = time.time() - self.timer_start
            self.current_scene = FinishScene(self.screen, elapsed)

        elif result == "retry":
            # Got rejected: swap in a fresh DateScene with a new AI character
            self.current_scene = DateScene(self.screen, self.ai_client)

        elif result == "restart":
            # Start new game
            self.current_scene = DateScene(self.screen, self.ai_client)
            self.timer_start = time.time()  # Reset the timer for the new run


if __name__ == "__main__":
    game = Game()
    game.run()  # Start the game loop — this never returns until the player quits
