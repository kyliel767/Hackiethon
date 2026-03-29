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
from ai_services import AIClient, RED_SYSTEM_PROMPT, GNOME_SYSTEM_PROMPT

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

#load house background image
house_background = pygame.image.load("pygame_demo/assets/house.png")
house_background = pygame.transform.scale(house_background, (1020, 780))
#load chat background image
chat_background = pygame.image.load("pygame_demo/assets/interior.png")
chat_background = pygame.transform.scale(chat_background, (1020, 780))
#load forest background image
forest_background = pygame.image.load("pygame_demo/assets/forest.png")
forest_background = pygame.transform.scale(forest_background, (1020, 780))
# load gnome interaction background
forest_chat = pygame.image.load("pygame_demo/assets/forest_chat.png")
forest_chat = pygame.transform.scale(forest_chat, (1020, 780))

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
red_image = pygame.image.load("pygame_demo/assets/red.png")
red_house_image = pygame.transform.scale(red_image, (120, 120))
red_chat_image = pygame.transform.scale(red_image, (400, 400))
#
red_rect = red_house_image.get_rect() #create a rectangle from the loaded npc image
red_rect.centerx = screen.get_width() // 2 #center horizontally
red_rect.x = 550
red_rect.y = 130
#
red_chat_rect = red_chat_image.get_rect()
red_chat_rect.centerx = screen.get_width() // 2
red_chat_rect.bottom = chat_panel_rect.y + 100
red_chat_rect.bottom = chat_panel_rect.y + 100

#player sprite
player = pygame.image.load("pygame_demo/assets/wolf.png")
player = pygame.transform.scale(player, (150, 150))
player_rect = player.get_rect()
player_rect.x = 200
player_rect.y = 450
player_speed = 4

# load gnome
gnome_npc = pygame.image.load("pygame_demo/assets/gnome.png")
gnome_npc = pygame.transform.scale(gnome_npc, (200, 200))
gnome_rect = gnome_npc.get_rect()
gnome_rect.x = 700
gnome_rect.y = 400

gnome_chat = pygame.transform.scale(gnome_npc, (400, 400))
gnome_chat_rect = gnome_chat.get_rect()
gnome_chat_rect.centerx = screen.get_width() // 2
gnome_chat_rect.bottom = chat_panel_rect.y + 100
gnome_chat_rect.bottom = chat_panel_rect.y + 100


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
font = pygame.font.Font(None, 32)
#clock for controlling frame rate (i.e. how fast the game loop runs)

clock = pygame.time.Clock()

#-------------------------
# AI client setup
#-------------------------
red_ai = AIClient()
gnome_ai = AIClient()

#-------------------------
# chat manager setup
#-------------------------
red_chat_assets = {
    'chat_bg': chat_background,
    'chat_panel': chat_panel,
    'chat_panel_rect': chat_panel_rect,
    'name_panel': name_panel,
    'name_panel_rect': name_panel_rect,
    'npc_chat': red_chat_image,
    'chat_npc_rect': red_chat_rect
}

gnome_chat_assets = {
    'chat_bg': forest_chat,
    'chat_panel': chat_panel,
    'chat_panel_rect': chat_panel_rect,
    'name_panel': name_panel,
    'name_panel_rect': name_panel_rect,
    'npc_chat': gnome_chat,
    'chat_npc_rect': gnome_chat_rect
}

red_chat_manager = ChatManager(screen, red_ai, RED_SYSTEM_PROMPT, font, red_chat_assets, npc_name = "Little Red Riding Hood")
gnome_chat_manager = ChatManager(screen, gnome_ai, GNOME_SYSTEM_PROMPT, font, gnome_chat_assets, npc_name = "Gnome")

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
    if player_rect.colliderect(gnome_rect) and game_state == "forest":
        if keys[pygame.K_e]:
            game_state = "minigame"
            gnome_chat_manager.enter_chat()
    elif player_rect.colliderect(red_rect) and game_state == "house":
        if keys[pygame.K_e]:
            game_state = "chat"
            red_chat_manager.enter_chat()
    

def draw_house():
    screen.blit(house_background, (0,0))
    screen.blit(red_house_image, red_rect)
    screen.blit(player, player_rect)

    # interacting with little red riding hood
    if player_rect.colliderect(red_rect):
        popup = font.render("Press E to talk", True, white)
        popup_rect = popup.get_rect(center=(red_rect.centerx, red_rect.top-20))
        screen.blit(popup, popup_rect)

def draw_forest():
    screen.blit(forest_background, (0,0))
    screen.blit(gnome_npc, gnome_rect)
    screen.blit(player, player_rect)

    # interacting with gnome
    if player_rect.colliderect(gnome_rect):
        popup = font.render("Press E to talk", True, white)
        popup_rect = popup.get_rect(center=(gnome_rect.centerx, gnome_rect.top-20))
        screen.blit(popup, popup_rect)

def draw_intro():
     # draw intro screen with title
    screen.fill(black)
    title = font.render("Welcome to the house of Little Red Riding Hood!", True, white)
    title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        
    # draw instructions below title
    instructions = font.render("Press ENTER to start.", True, white)
    instructions_rect = instructions.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
    screen.blit(title, title_rect)
    screen.blit(instructions, instructions_rect)

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
                game_state = "forest"
            
            # handle chat events if in chat state
            if game_state == "chat":
                game_state = red_chat_manager.handle_event(event)
            
            if game_state == "minigame":
                game_state = gnome_chat_manager.handle_event(event)

    #--------------
    # house update
    #--------------
    if game_state == "house":
        handle_player_movement(keys)
        check_npc_interaction(keys)
    
    if game_state == "forest":
        handle_player_movement(keys)
        check_npc_interaction(keys)

    #------
    # draw
    #------
    if game_state == "intro":
        draw_intro()
    if game_state == "house":
        draw_house()
    elif game_state == "chat":
        red_chat_manager.draw()
    elif game_state == "forest":
        draw_forest()
    elif game_state == "minigame":
        gnome_chat_manager.draw()


    # ----
    # status update
    # ----
    if game_state == "chat":
        game_state = red_chat_manager.check_status("chat")
    
    if game_state == "minigame":
        game_state = gnome_chat_manager.check_status("minigame")

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