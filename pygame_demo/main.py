#--------------------------
# imports & initialisation
#--------------------------
import os
import threading

import pygame
import sys
from dotenv import load_dotenv
from groq import Groq

# load environment variables for API key
load_dotenv()

# this is the prompt

# Prompts
system_prompt = """
You are a kind and curious girl. You love exploring the forest and spending time with your grandmother.
You are friendly, brave, and always eager to learn new things. 
You have a strong connection to nature and often talk to animals in the forest.
You have arrived at your grandmother's house after you have been traveling through the woods
You greet your grandmother without suspicion.
After your grandmother greets you, you notice something strange about her appearance.
You can ask her about one of the following, only ONE at a time:
- great big eyes
- great big ears
- great big teeth
- great big furry coat
Your task is to figure out what is wrong with your grandmother, if there is something wrong.
If it seems that you are in danger or that your grandmother is a wolf in disguise, you should scream for help.
Otherwise, you should have a friendly conversation with your grandmother and ask her about her day.

RULES:
- track your internal state and feelings as you interact with your grandmother.
- At the END of every response, you MUST include a status tag in square brackets indicating how the date is going:
    [STATUS:ongoing] - if you are still unsure about your grandmother and want to keep talking
    [STATUS:accepted] - if grandmother keeps kind tone, mentions love, care, and normal family behavior. If you do not suspect she is a wolf in disguise.
    [STATUS:rejected] - If grandmother gives clear danger signs like talking about eating you
- The status tag must be the very last thing in your message.
- Never mention or explain the status tags.
- Do not convey your actions, for example "*hug*". You are only speaking your dialogue. 
- Keep your replies to a maximum of 1 sentence. Be concise.
"""

# initialise all pygame modules (graphics, input, etc.)
pygame.init()
# initialise pygame's mixer for playing sound/music
pygame.mixer.init()

#--------------------------------
# window, assets and image setup
#--------------------------------
#create game window of width height 
screen = pygame.display.set_mode((1020, 780))
#set the title of the window
pygame.display.set_caption("NPC Chat Demo")

#load world background image
house_background = pygame.image.load("pygame_demo/assets/house.png")
house_background = pygame.transform.scale(house_background, (1020, 780))
#load chat background image
chat_background = pygame.image.load("pygame_demo/assets/interior.jpg")
chat_background = pygame.transform.scale(chat_background, (1020, 780))

#
chat_panel = pygame.Rect(0, 0, 700, 130) #create a rectangle manually
chat_panel.centerx = screen.get_width() // 2 #center horizontally
chat_panel.bottom = screen.get_height() - 20 #place near bottom
#
name_panel = pygame.Rect(0, 0, chat_panel.width, 40)
name_panel.centerx = screen.get_width() // 2
name_panel.top = 20 #place at top of the screen

#load npc sprite
npc_image = pygame.image.load("pygame_demo/assets/red.png")
npc_world = pygame.transform.scale(npc_image, (120, 120))
npc_chat = pygame.transform.scale(npc_image, (400, 400))
#
world_npc_rect = npc_world.get_rect() #create a rectangle from the loaded npc image
world_npc_rect.centerx = screen.get_width() // 2 #center horizontally
world_npc_rect.x = 650
world_npc_rect.y = 130
#
chat_npc_rect = npc_chat.get_rect()
chat_npc_rect.centerx = screen.get_width() // 2
chat_npc_rect.bottom = chat_panel.y + 100

#player sprite
player = pygame.image.load("pygame_demo/assets/wolf.png")
player = pygame.transform.scale(player, (120, 120))
player_rect = player.get_rect()
player_rect.x = 50
player_rect.y = 260
player_speed = 3

#load background music, set volume, and play in loop
# pygame.mixer.music.load("pygame_demo/assets/music.mp3")
# pygame.mixer.music.set_volume(0.5)
# pygame.mixer.music.play(-1) #-1 means loop indefinitely

#--------------------------------
# define colours, font, and clock
#--------------------------------
black = (0, 0, 0)
white = (255, 255, 255)
#default font for displaying text
font = pygame.font.Font(None, 36)
#clock for controlling frame rate (i.e. how fast the game loop runs)
clock = pygame.time.Clock()

#------------
# game state
#------------
game_state = "intro"
waiting_for_ai = False
#messages to display in chat panel (AI will populate greeting dynamically)
messages = []
#player's current typed input
player_input = ""

# AI conversation history and prompt (NPC behavior)
GROQ_MODEL = "llama-3.3-70b-versatile"
conversation_history = [
    {
        "role": "system",
        "content": system_prompt,
    }
]


def extract_status_from_response(text):
    for status in ["accepted", "rejected", "ongoing"]:
        tag = f"[STATUS:{status}]"
        if tag in text:
            return text.replace(tag, "").strip(), status
    return text.strip(), "ongoing"


class AIClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("Missing GROQ_API_KEY in .env")
            sys.exit(1)
        self.client = Groq(api_key=api_key)

    def send_messages(self, messages):
        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                max_tokens=200,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as error:
            return f"[AI Error: {error}] [STATUS:ongoing]"


ai_client = AIClient()


def ask_npc(player_text):
    global waiting_for_ai, conversation_history
    waiting_for_ai = True
    conversation_history.append({"role": "user", "content": player_text})
    ai_response = ai_client.send_messages(conversation_history)
    conversation_history.append({"role": "assistant", "content": ai_response})
    clean, status = extract_status_from_response(ai_response)
    waiting_for_ai = False
    return clean, status


def start_npc_response(user_text):
    # start AI call in background so the main loop stays responsive
    def worker():
        clean, status = ask_npc(user_text)
        messages.append("NPC: " + clean)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


#------------
# functions
#------------

def handle_player_movement(keys):
    if keys[pygame.K_LEFT]:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += player_speed
    if keys[pygame.K_UP]:
        player_rect.y -= player_speed
    if keys[pygame.K_DOWN]:
        player_rect.y += player_speed
    
    #keep player inside screen
    player_rect.x = max(0, min(player_rect.x, screen.get_width() - player_rect.width))
    player_rect.y = max(0, min(player_rect.y, screen.get_height() - player_rect.height))

def check_npc_interaction(keys):
    global game_state, player_input, messages, waiting_for_ai, conversation_history
    if player_rect.colliderect(world_npc_rect):
        if keys[pygame.K_e]:
            game_state = "chat"
            # reset game state variables
            player_input = ""
            waiting_for_ai = False
            messages = []
            conversation_history = [{"role": "system", "content": system_prompt}]

            # ask first line from the AI to start the conversation
            start_npc_response("Hi! Please say a greeting as Little Red Riding Hood.")


def draw_world():
    screen.blit(house_background, (0,0))
    screen.blit(npc_world, world_npc_rect)
    screen.blit(player, player_rect)

    if player_rect.colliderect(world_npc_rect):
        popup = font.render("Press E to talk", True, white)
        popup_rect = popup.get_rect(center=(world_npc_rect.centerx, world_npc_rect.top-20))
        screen.blit(popup, popup_rect)

def draw_chat():
    screen.blit(chat_background, (0,0))
    #draw the npc sprite
    screen.blit(npc_chat, chat_npc_rect)

    #draw chat panel for showing messages
    pygame.draw.rect(screen, black, chat_panel)

    #draw npc's name panel
    pygame.draw.rect(screen, black, name_panel)
    npc_name = "Little Red Riding Hood"
    name_surface = font.render(npc_name, True, white)
    name_rect = name_surface.get_rect(center=name_panel.center)
    screen.blit(name_surface, name_rect)

    #draw all messages in the chat panel
    y = chat_panel.y + 10
    for msg in messages:
        text_surface = font.render(msg, True, white)
        screen.blit(text_surface, (chat_panel.x + 10, y))
        y += 30 #move down for next line

    #draw player input text dynamically
    if waiting_for_ai:
        input_surface = font.render("NPC is thinking...", True, white)
    else:
        input_surface = font.render("> " + player_input, True, white)
    screen.blit(input_surface, (chat_panel.x + 10, y))


#----------------
# main game loop
#----------------
running = True #loop continues until window is closed
while running:

    keys = pygame.key.get_pressed()

    #-----------------------------------------
    # event handling (quit, keyboard, etc.)
    #-----------------------------------------
    for event in pygame.event.get():
        
        #close window if user clicks the close button
        if event.type == pygame.QUIT:
            running = False
        
        #detect key presses
        if event.type == pygame.KEYDOWN:
            # ENTER to start game from intro screen
            if game_state == "intro" and event.key == pygame.K_RETURN:
                game_state = "world"
            
            # ESC to exit chat
            if game_state == "chat" and event.key == pygame.K_ESCAPE:
                game_state = "world"

            if game_state == "chat" and not waiting_for_ai:
                #deleting last character
                if event.key == pygame.K_BACKSPACE:
                    player_input = player_input[:-1]
                #entering input
                elif event.key == pygame.K_RETURN and player_input.strip():
                    messages.append("> " + player_input.strip()) #adds player's message to chat history
                    start_npc_response(player_input.strip())
                    player_input = "" #clear input field

                elif event.unicode and event.unicode.isprintable():
                    #add typed character to current input
                    player_input += event.unicode

    #--------------
    # world update
    #--------------
    if game_state == "world":
        waiting_for_ai = False
        handle_player_movement(keys)
        check_npc_interaction(keys)

    #------
    # draw
    #------
    if game_state == "intro":
        # draw intro screen with title
        screen.fill(black)
        title = font.render("Welcome to the world of Little Red Riding Hood!", True, white)
        title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        
        # draw instructions below title
        instructions = font.render("Press ENTER to start.", True, white)
        instructions_rect = instructions.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
        screen.blit(title, title_rect)
        screen.blit(instructions, instructions_rect)
    if game_state == "world":
        draw_world()
    if game_state == "chat":
        draw_chat()

    #----------------------------------------
    # update the display and control fps
    #----------------------------------------
    pygame.display.flip()
    clock.tick(60) #60 fps is standard

#------------
# clean exit
#------------
pygame.quit()
sys.exit()