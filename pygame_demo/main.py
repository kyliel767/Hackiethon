#--------------------------
# imports & initialisation
#--------------------------
import pygame
import sys
import math
from typewriting import draw_animated_text

#initialise all pygame modules (graphics, input, etc.)
pygame.init()
#initialise pygame's mixer for playing sound/music
pygame.mixer.init()

#--------------------------------
# window, assets and image setup
#--------------------------------
#create game window of width 1000 height 500
screen = pygame.display.set_mode((1000, 500))
#set the title of the window
pygame.display.set_caption("NPC Chat Demo")


#load intro background image
intro_background = pygame.image.load("pygame_demo/assets/intro-no-word.png")
intro_background = pygame.transform.scale(intro_background, (1000, 500))

#load world background image
house_background = pygame.image.load("pygame_demo/assets/house_background.jpg")
house_background = pygame.transform.scale(house_background, (1000, 500))
#load chat background image
chat_background = pygame.image.load("pygame_demo/assets/interior.jpg")
chat_background = pygame.transform.scale(chat_background, (1000, 500))

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
world_npc_rect.y = 170
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
# Font path for the pixaleted text
# FONT_FILE = "PressStart2P-Regular.ttf"
#clock for controlling frame rate (i.e. how fast the game loop runs)
clock = pygame.time.Clock()

#------------
# game state
#------------
game_state = "intro"
frozen = False #freeze input after player responds once
#messages to display in chat panel (starting with the default npc greeting)
messages = ["NPC: Hello! What's your name?"]
#player's current typed input
player_input = ""

#------------
# functions
#------------
#def get_pixelated_font(size):
    #return pygame.font.Font(FONT_FILE, size)

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
    global game_state, player_input, frozen, messages
    if player_rect.colliderect(world_npc_rect):
        if keys[pygame.K_e]:
            game_state = "chat"
            #reset game state variables
            player_input = ""
            frozen = False
            messages = ["NPC: Hello! What's your name?"]


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
    if frozen:
        input_surface = font.render("", True, white)
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

            if game_state == "chat" and not frozen: #only allow typing if not frozen
                #deleting last character
                if event.key == pygame.K_BACKSPACE:
                    player_input = player_input[:-1]
                #entering input
                elif event.key == pygame.K_RETURN:
                    messages.append("> " + player_input) #adds player's message to chat history
                    #simple npc response
                    npc_response = "NPC: Nice to meet you " + player_input
                    messages.append(npc_response) #adds npc's message to chat history
                    frozen = True #now that player has responded, we want to stop the game
                    player_input = "" #clear input field

                else:
                    #add typed character to current input
                    player_input += event.unicode

    #--------------
    # world update
    #--------------
    if game_state == "world":
        frozen = False
        handle_player_movement(keys)
        check_npc_interaction(keys)

    #------
    # draw
    #------
    if game_state == "intro":        
        # draw intro screen with title
        screen.blit(intro_background, (0, 0))  # background first
        
        #title = get_pixelated_font(40).render("Welcome to the world of\nLittle Red Riding Hood!", True, (211, 100, 17))
        #title_rect = title.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 100))

        #add bounce timing
        bounce_offset = math.sin(pygame.time.get_ticks() * 0.005) * 8

        # draw instructions below title
        instructions = font.render("Press ENTER to start.", False, black)
        instructions_rect = instructions.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 80 + bounce_offset))
        
        text = "Hello"
        draw_animated_text(screen, text, font, screen.get_width()//2, 150, white)
        
        #screen.blit(title, title_rect)
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