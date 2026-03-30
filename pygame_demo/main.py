#--------------------------
# imports & initialisation
#--------------------------
import os
import pygame
import sys
import math
from dotenv import load_dotenv
from groq import Groq

 # import chat manager class
from chat_manager import ChatManager
# import AI client and system prompt
from ai_services import AIClient, RED_SYSTEM_PROMPT, GNOME_SYSTEM_PROMPT
# import narration manager
from narration_manager import NarrationManager, HOUSE_NARRATION, FOREST_NARRATION
# import typewriting effects
from typewriting import draw_animated_text, make_text_state
# import load sprite sheets function
from extract_sprite_sheets import load_spritesheet

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


#load intro background image
intro_background = pygame.image.load("pygame_demo/assets/intro-no-word.png")
intro_background = pygame.transform.scale(intro_background, (1020, 780))

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
# load good ending background
earth_background = pygame.image.load("pygame_demo/assets/earth.png")
earth_background = pygame.transform.scale(earth_background, (1020, 780))

#load failure ending frames into a list
walk_frames = []
for i in range(1, 10):
    frame = pygame.image.load(f"pygame_demo/assets/end{i}.png")
    frame = pygame.transform.scale(frame, (1020, 780))
    walk_frames.append(frame)

#load portal animation
portal_frames = load_spritesheet("pygame_demo/assets/portal_sheet.png", num_frames=8, scale=(200, 200))


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
red_rect.x = 140
red_rect.y = 390
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

# load wolf as grandma
wolf_grandma = pygame.image.load("pygame_demo/assets/grandma.png")
wolf_grandma = pygame.transform.scale(wolf_grandma, (100, 150))
wolf_grandma_rect = wolf_grandma.get_rect()
wolf_grandma_rect.x = 550
wolf_grandma_rect.y = 500
wolf_grandma_speed = 4

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
narration_font = pygame.font.Font(filename="pygame_demo/PressStart2P-Regular.ttf", size=22)
# Font path for the pixaleted text
FONT_FILE = "PressStart2P-Regular.ttf"
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

#-------------------------
# narration manager setup
#-------------------------
# load and scale the narration panel specifically for center display
narration_panel_img = pygame.image.load("pygame_demo/assets/narration_panel.png").convert_alpha()
narrator = NarrationManager(screen, narration_font, narration_panel_img)

#-------------------------
# define variables for ending 
#-------------------------
# animation variables for ending 
current_frame = 0
animation_timer = 0
animation_speed = 150  # milliseconds per frame

# sprite sheet variables for ending
portal_frame = 0
portal_timer = 0
portal_speed = 100

# good ending transition variable 
good_ending_timer = 0
good_ending_delay = 2000  # 3 seconds of portal before fading
good_fade_alpha = 0
good_fading = False
good_fade_surface = pygame.Surface((1020, 780))
good_fade_surface.fill(black)
state1 = make_text_state()
state2 = make_text_state()
state3 = make_text_state()
state4 = make_text_state()

#transition variables to ending
ending_timer = 0



#------------
# game state
#------------
game_state = "house"

#------------
# functions
#------------
#def get_pixelated_font(size):
    #return pygame.font.Font(FONT_FILE, size)

def handle_player_movement(keys, player):
    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_UP]:
        player.y -= player_speed
    if keys[pygame.K_DOWN]:
        player.y += player_speed
    
    #keep player inside screen
    player.x = max(0, min(player.x, screen.get_width() - player.width))
    player.y = max(0, min(player.y, screen.get_height() - player.height))

def check_npc_interaction(keys, player):
    global game_state
    if player.colliderect(gnome_rect) and game_state == "forest":
        if keys[pygame.K_e]:
            game_state = "minigame"
            gnome_chat_manager.enter_chat()
    elif wolf_grandma_rect.colliderect(red_rect) and game_state == "house":
        if keys[pygame.K_e]:
            game_state = "chat"
            red_chat_manager.enter_chat()
    

def draw_house():
    screen.blit(house_background, (0,0))
    screen.blit(red_house_image, red_rect)
    screen.blit(wolf_grandma, wolf_grandma_rect)

    # interacting with little red riding hood
    if wolf_grandma_rect.colliderect(red_rect):
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
    screen.blit(intro_background, (0, 0))  # background first
    
    #title = get_pixelated_font(40).render("Welcome to the world of\nLittle Red Riding Hood!", True, (211, 100, 17))
    #title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))

    #add bounce timing
    bounce_offset = math.sin(pygame.time.get_ticks() * 0.005) * 8

    # draw instructions below title
    instructions = font.render("Press ENTER to start.", False, black)
    instructions_rect = instructions.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50 + bounce_offset))
    
    #screen.blit(title, title_rect)
    screen.blit(instructions, instructions_rect)


def draw_bad_ending():
    global current_frame, animation_timer

    animation_timer += clock.tick(60)

    if animation_timer >= animation_speed:
        if current_frame < len(walk_frames) - 1:
            current_frame += 1
        animation_timer = 0

    # draw current frame
    screen.blit(walk_frames[current_frame], (0, 0))

    # blend next frame on top with increasing opacity
    if current_frame < len(walk_frames) - 1:
        next_frame = walk_frames[current_frame + 1].copy()
        alpha = int((animation_timer / animation_speed) * 255)
        next_frame.set_alpha(alpha)
        screen.blit(next_frame, (0, 0))

    if current_frame == len(walk_frames) - 1:
        draw_animated_text(screen, ["YOU", "FAIL!"], pygame.font.Font("pygame_demo/PressStart2P-Regular.ttf", 90), screen.get_width()//2, screen.get_height()//2 - 120, white, 120, line_delay=0.06, state=state4)

def draw_good_ending():

    global portal_frame, portal_timer, good_ending_timer, good_fading, good_fade_alpha

    screen.blit(house_background, (0, 0))

    

    # update animation
    portal_timer += clock.tick(60)
    if portal_timer >= portal_speed:
        portal_frame = (portal_frame + 1) % len(portal_frames)
        portal_timer = 0

    # draw the current frame
    screen.blit(portal_frames[portal_frame], (screen.get_width()//2 - 10, screen.get_height()//2 - 50))
    screen.blit(player, (screen.get_width()//2 - 50 , screen.get_height()//2))
    # count time then start fading
    good_ending_timer += portal_timer
    if good_ending_timer >= good_ending_delay:
        good_fading = True

    # fade to black
    if good_fading:
        good_fade_alpha += 5 # fade speed
        good_fade_surface.set_alpha(good_fade_alpha)
        screen.blit(good_fade_surface, (0, 0))

        # once fully fanded go to the final ending screen
        if good_fade_alpha >= 255:  
            screen.blit(earth_background, (0,0))
            draw_animated_text(screen, ["CONGRATULATIONS"],pygame.font.Font("pygame_demo/PressStart2P-Regular.ttf", 50) , screen.get_width()//2, screen.get_height()//2 - 250, white, state=state1)
            if state1["done"]:
                draw_animated_text(screen, ["YOU WIN!"],pygame.font.Font("pygame_demo/PressStart2P-Regular.ttf", 90) , screen.get_width()//2, screen.get_height()//2 - 120, white, state=state2)
            if state2["done"]:
                draw_animated_text(screen, ["Welcome back to Earth"],pygame.font.Font("pygame_demo/PressStart2P-Regular.ttf", 20) , screen.get_width()//2, screen.get_height()//2 + 30, white, state=state3)

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
                game_state = "forest_narration"
                narrator.start_narration(FOREST_NARRATION)
            
            # handle chat events if in chat state
            elif game_state == "chat":
                game_state = red_chat_manager.handle_event(event)
            
            elif game_state == "minigame":
                game_state = gnome_chat_manager.handle_event(event)
            
            # handle narration events
            elif game_state == "house_narration":
                if event.key == pygame.K_RETURN:
                    if narrator.is_finished():
                        game_state = "house" # unlock player movement
                    else:
                        # finish the typewriter effect instantly
                        narrator.char_index = len(narrator.full_text)
            elif game_state == "forest_narration":
                if event.key == pygame.K_RETURN:
                    if narrator.is_finished():
                        game_state = "forest" # unlock player movement
                    else:
                        # finish the typewriter effect instantly
                        narrator.char_index = len(narrator.full_text)

    #--------------
    # state update
    #--------------
    if game_state == "house":
        handle_player_movement(keys, wolf_grandma_rect)
        check_npc_interaction(keys, wolf_grandma_rect)
    
    if game_state == "forest":
        handle_player_movement(keys, player_rect)
        check_npc_interaction(keys, player_rect)

    # logic for narration (no movement allowed)
    if game_state == "house_narration" or game_state == "forest_narration":
        narrator.update()
    #------
    # draw
    #------
    if game_state == "intro":
        draw_intro()
        
    if game_state == "house" or game_state == "house_narration":
        draw_house() # always draw the room in the background
        if game_state == "house_narration":
            narrator.draw() # draw panel on top of room
    if game_state == "house":
        draw_house()
    elif game_state == "chat":
        red_chat_manager.draw()
    elif game_state == "forest" or game_state == "forest_narration":
        draw_forest()
        if game_state == "forest_narration":
            narrator.draw()
    elif game_state == "minigame":
        gnome_chat_manager.draw()
    elif game_state == "good_ending":
        if pygame.time.get_ticks() - ending_timer >= 4000:
            draw_good_ending()
    elif game_state == "bad_ending":
        if pygame.time.get_ticks() - ending_timer >= 4000:
            draw_bad_ending()


    # ----
    # status update
    # ----
    if game_state == "chat":
        new_state = red_chat_manager.check_status("chat")
        if new_state == "win":
            ending_timer = pygame.time.get_ticks()
            game_state = "good_ending"
        elif new_state == "game_over":
            ending_timer = pygame.time.get_ticks()
            game_state = "bad_ending"

    if game_state == "minigame":
        new_state = gnome_chat_manager.check_status("minigame")
        # only trigger the narration if the state is actually changing right now
        if new_state == "house_narration":
            game_state = "house_narration"
            narrator.start_narration(HOUSE_NARRATION)
        else:
            game_state = new_state

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