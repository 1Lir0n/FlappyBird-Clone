import pygame
import time
import random
from player import *
from pipe import *
from button import *
rnd = random.Random()

screenResVertical = [(240,320),     # 240p          1
                     (320,480),     # 320p          2
                     (360,640),     # 360p          3
                     (480,854),     # 480p          4
                     (540,960),     # 540p          5
                     (600,800),     # 600p          6
                     (720,1280),    # 720p          7
                     (768,1024),    # 768p          8
                     (768,1366),    # 768p (HD)     9
                     (800,1280),    # 800p          10
                     (900,1440),    # 900p          11
                     (1024,1280),   # 1024p         12
                     (1050,1680),   # 1050p         13
                     (1080,1920),   # 1080p         14
                     (1080,2048),   # 1080p (2K)    15
                     (1440,2560),   # 1440p         16
                     (2160,3840),   # 2160p         17
                     (2160,4096)]   # 2160p (4K)    18

# game settings
screenSize = screenResVertical[3][::1] # screen resolution for the game
fps = 60 # game frame per second lock

# pygame setup
pygame.init()
Rect = pygame.Rect
screen = pygame.display.set_mode(screenSize)
clock = pygame.time.Clock()
running = True
paused = False
deltaTime = 0
first=True
DIED = pygame.USEREVENT + 1  # custom event for player death
inMenu = False

# player settings
bird = Player(playerHeight=int(min(screenSize)*0.05),
                     playerWidth=int((min(screenSize)*0.05)*(17/12)),
                     playerX=screen.get_width()/2,
                     playerY=screen.get_height()/2,
                     jumpHeight=screen.get_height()*0.4,
                     gravity=screen.get_height()*0.7,)
highscore = 0

pipes = Pipes(playerHeight=int(min(screenSize)*0.1),
              surface=screen)

# load background image
background_img = pygame.image.load("background.png").convert()
background_width = background_img.get_width()
background_height = background_img.get_height()
scale_ratio = screenSize[1] / background_height
new_width = int(background_width * scale_ratio)
background_img = pygame.transform.scale(background_img, (new_width, screenSize[1]))
background_width = new_width
bg_scroll_x = 0
bg_scroll_speed = screen.get_width()//4  # background moves slower than pipes 

# screen collider  
screenCollider = Rect(0,0,screenSize[0]+pipes.get_pipe_width()*2,screenSize[1])

def events_handler():
    global running, paused, bird, pipes, first, deltaTime 
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) :
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if bird.get_died():
                    continue
                paused = not paused
        if event.type == DIED:
            pygame.time.set_timer(DIED, 0)  # stop the DIED event timer
            bird.set_died(True)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if bird.get_died():
                    paused = False
                    bird.set_just_died(True)
                    # reset the game state
                    pipes.clear_pipes()
                    first = True
                    bird.reset_player(location=pygame.Vector2(screen.get_width()/2,screen.get_height()/2))

def draw_text_with_outline(text, font, text_color, outline_color, screen, location,outline_thickness=2):
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(location[0], location[1]))

    # Draw outline around the text
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:
                outline_surf = font.render(text, True, outline_color)
                outline_rect = outline_surf.get_rect(center=(text_rect.centerx + dx, text_rect.centery + dy))
                screen.blit(outline_surf, outline_rect)

    # Draw main text
    screen.blit(text_surface, text_rect)

def draw_outlined_multiline_text_centered(text, font, text_color, outline_color, screen, line_spacing=5, outline_thickness=2):
    lines = text.split('\n')
    line_surfaces = [font.render(line, True, text_color) for line in lines]
    line_outlines = [
        [font.render(line, True, outline_color) for _ in range(8)]
        for line in lines
    ]

    total_height = sum(surf.get_height() + line_spacing for surf in line_surfaces) - line_spacing
    start_y = screen.get_height() // 2 - total_height // 2

    for i, (surf, outlines) in enumerate(zip(line_surfaces, line_outlines)):
        center_x = screen.get_width() // 2
        y = start_y + surf.get_height() // 2

        # Offsets for outline (8 directions)
        offsets = [(-outline_thickness, 0), (outline_thickness, 0),
                   (0, -outline_thickness), (0, outline_thickness),
                   (-outline_thickness, -outline_thickness), (-outline_thickness, outline_thickness),
                   (outline_thickness, -outline_thickness), (outline_thickness, outline_thickness)]

        # Draw outline
        for offset in offsets:
            outline_rect = surf.get_rect(center=(center_x + offset[0], y + offset[1]))
            screen.blit(font.render(lines[i], True, outline_color), outline_rect)

        # Draw main text
        text_rect = surf.get_rect(center=(center_x, y))
        screen.blit(surf, text_rect)

        start_y += surf.get_height() + line_spacing

counter = 0
font = pygame.font.SysFont(None, screenSize[0] // 10)
#program run
while running:

    # event handling, gets all event from the event queue
    events_handler()
    
    # set the frame rate
    deltaTime = clock.tick(fps) / 1000
    bird.set_delta_time(dt=deltaTime)
    pipes.set_delta_time(dt=deltaTime)

    if inMenu:
        print("UI time")
        continue

    # if the game is paused, skip the rest of the loop
    if paused:
        draw_outlined_multiline_text_centered(
            "Game Paused",
            font,
            text_color=(255, 255, 255),
            outline_color=(0, 0, 0),
            screen=screen,
            line_spacing=10,
            outline_thickness=2
        )
        pygame.display.flip()
        # if the game is paused, skip the rest of the loop
        continue

    #ensures the pipes are spawned at the start of the game
    if first:
        first=False
        pipes.spawn_pipes()

    # fill the screen with a color to wipe away anything from last frame
    screen.fill((135,206,255))
    
    # Update background scroll if not dead
    if not bird.get_died():
        bg_scroll_x -= bg_scroll_speed * deltaTime
        if bg_scroll_x <= -background_width:
            bg_scroll_x = 0

    # Draw two copies side-by-side for seamless scrolling
    screen.blit(background_img, (bg_scroll_x, 0))
    screen.blit(background_img, (bg_scroll_x + background_width, 0))

    # Draw player sprite
    screen.blit(bird.currentFrame, bird.get_player_hitbox().topleft)

    # draw the pipes
    pipes.draw_pipes()

    # death handling
    if bird.get_died():
        draw_outlined_multiline_text_centered(
            ("You Died!\nFinal Score: "+ str(bird.get_score())+"\nHigh Score: "+ str(highscore)) if highscore>bird.get_score() else ("You Died!\nNew High Score!\nHigh Score: "+ str(bird.get_score())) ,
            font,
            text_color=(255, 255, 255),
            outline_color=(0, 0, 0),
            screen=screen,
            line_spacing=10,
            outline_thickness=2
        )
        if highscore<bird.get_score():
            highscore=bird.get_score()
        time.sleep(0.1)  # wait for 2 seconds before restarting
        pygame.display.flip()
        continue

    # key handling
    # get the set of keys pressed
    keys_pressed = pygame.key.get_pressed()

    if bird.get_just_died():
        time.sleep(0.1)  # wait for a short moment to show the death screen
        bird.set_just_died(False)
    
    else:
        # jumping
        bird.jumping(keys_pressed)

    # pipe movement
    pipes.move_pipes() # move pipes to the left
    # pipe spawning
    try:
        if screen.get_width() < screen.get_height():
            if  pipes.get_pipes()[len(pipes.get_pipes())-1][0] <= screen.get_width()/2 - pipes.get_pipe_width()*2:
                pipes.spawn_pipes(gapLocation=2)
        else:
            if  pipes.get_pipes()[len(pipes.get_pipes())-1][0] <= screen.get_width()/1.25 - pipes.get_pipe_width()*2:
                pipes.spawn_pipes(gapLocation=2)
    except Exception as e:
        print(e)
        if not pipes.get_pipes():
            pipes.spawn_pipes(gapLocation=2 )

    # pipe remove
    for pipe in pipes.get_pipes():
        if not pipe.colliderect(screenCollider):
            pipes.remove_pipe(pipe)
    

    # collision detection
    for pipe in pipes.get_pipes():
        if pipe.colliderect(bird.get_player_hitbox()):
            pygame.time.set_timer(DIED, 1)  # set a timer for the DIED event
        
    if bird.get_player_hitbox()[1] < 0 or bird.get_player_hitbox()[1] > screenSize[1] - bird.get_height():
        pygame.time.set_timer(DIED, 1)  # set a timer for the DIED event


    # score calculation
    try:
        if pipes.get_pipes():
            if pipes.get_pipes()[len(pipes.get_pipes())-3][0] < bird.get_player_hitbox()[0] and pipes.get_pipes()[len(pipes.get_pipes())-3][0] > bird.get_player_hitbox()[0] - screen.get_width()//2*deltaTime:
                bird.set_score(bird.get_score()+1)
    except IndexError:
        pass
    
    draw_text_with_outline (
        str(bird.get_score()),
        font,
        text_color=(255, 255, 255),
        outline_color=(0, 0, 0),
        screen=screen,
        location=(screenSize[0]//2,screenSize[1]*0.1),
        outline_thickness=2
    )

    # flip() the display to put your work on screen
    pygame.display.flip()


pygame.quit()