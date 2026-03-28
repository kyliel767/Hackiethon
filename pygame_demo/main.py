#--------------------------
# imports & initialisation
#--------------------------
import os
import pygame
import sys
from dotenv import load_dotenv
from groq import Groq

 # import chat manager class
from chat_manager import ChatManager
# import AI client and system prompt
from ai_services import AIClient, SYSTEM_PROMPT

# load environment variables for API key
load_dotenv()

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

# load chat panel artwork (no scaling)
chat_panel = pygame.image.load("pygame_demo/assets/chat_panel.png").convert_alpha()
chat_panel_rect = chat_panel.get_rect()
chat_panel_rect.centerx = screen.get_width() // 2
chat_panel_rect.bottom = screen.get_height() - 20

name_panel = pygame.image.load("pygame_demo/assets/name_panel.png").convert_alpha()
name_panel_rect = name_panel.get_rect()
name_panel_rect.centerx = screen.get_width() // 2
name_panel_rect.top = 20


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
chat_npc_rect.bottom = chat_panel_rect.y + 100

#player sprite
player = pygame.image.load("pygame_demo/assets/wolf.png")
player = pygame.transform.scale(player, (120, 120))
player_rect = player.get_rect()
player_rect.x = 50
player_rect.y = 260
player_speed = 3

#--------------------------------
# define colours, font, and clock
#--------------------------------
black = (0, 0, 0)
white = (255, 255, 255)
#default font for displaying text
font = pygame.font.Font(None, 32)
#clock for controlling frame rate (i.e. how fast the game loop runs)
clock = pygame.time.Clock()

ai_client = AIClient()

#-------------------------
# chat manager setup
#-------------------------
chat_assets = {
    'chat_bg': chat_background,
    'chat_panel': chat_panel,
    'chat_panel_rect': chat_panel_rect,
    'name_panel': name_panel,
    'name_panel_rect': name_panel_rect,
    'npc_chat': npc_chat,
    'chat_npc_rect': chat_npc_rect
}

chat_manager = ChatManager(screen, ai_client, SYSTEM_PROMPT, font, chat_assets)

#------------
# game state
#------------
game_state = "intro"

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
    global game_state
    if player_rect.colliderect(world_npc_rect):
        if keys[pygame.K_e]:
            game_state = "chat"
            chat_manager.enter_chat()

def draw_world():
    screen.blit(house_background, (0,0))
    screen.blit(npc_world, world_npc_rect)
    screen.blit(player, player_rect)

    if player_rect.colliderect(world_npc_rect):
        popup = font.render("Press E to talk", True, white)
        popup_rect = popup.get_rect(center=(world_npc_rect.centerx, world_npc_rect.top-20))
        screen.blit(popup, popup_rect)

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
            
            # handle chat events if in chat state
            if game_state == "chat":
                game_state = chat_manager.handle_event(event)

    #--------------
    # world update
    #--------------
    if game_state == "world":
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
        chat_manager.draw()

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