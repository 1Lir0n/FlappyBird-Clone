import pygame
import time
import random
import player
import pipe as Pipe
import button
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
screenSize = screenResVertical[13][::-1] # screen resolution for the game
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
bird = player.Player(playerHeight=int(min(screenSize)*0.1),
                     playerWidth=int((min(screenSize)*0.1)*(17/12)),
                     playerX=screen.get_width()/2,
                     playerY=screen.get_height()/2,
                     jumpHeight=screen.get_height()*0.4,
                     gravity=screen.get_height()*0.7,)
highscore = 0

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

pipe_sprite_sheet = pygame.image.load("pipes.png").convert_alpha()
pipe_sprite_height = pipe_sprite_sheet.get_height() 
pipe_sprite_width = pipe_sprite_sheet.get_width() // 2

pipe_frame_top = pipe_sprite_sheet.subsurface(pygame.Rect( pipe_sprite_width,0, pipe_sprite_width, pipe_sprite_height))
pipe_frame_bottom = pipe_sprite_sheet.subsurface(pygame.Rect( 0,0, pipe_sprite_width, pipe_sprite_height))

# pipe settings
# pipe width and height
pipeWidth = int(screenSize[0] * 0.1)  # 10% of screen width
pipeHeight = screenSize[1]

pipeGap = int(bird.get_height()*5)  # 5 times the player height, gap between the pipes

def get_pipe_margin(gap_center: float, gap_size: float):
    top = gap_center * pipeHeight - gap_size / 2
    bottom = pipeHeight - (gap_center * pipeHeight + gap_size / 2)
    return (top, bottom)
 

# screen collider  
screenCollider = Rect(0,0,screenSize[0]+pipeWidth*2,screenSize[1])

pipes = []

def spawn_pipes(gaploc=None):
    global pipes

    min_visible_pipe_height = screenSize[1]*0.05  # always leave at least 40px of pipe visible

    # Clamp gap center to avoid fully hidden pipes
    gap_half = pipeGap / 2
    min_center = (min_visible_pipe_height + gap_half) / pipeHeight
    max_center = 1 - min_center
    if not gaploc:
        gapPlace = rnd.uniform(min_center, max_center)
    else:
        gapPlace = gaploc

    # Get top and bottom pipe sizes
    top_margin, bottom_margin = get_pipe_margin(gapPlace, pipeGap)

    # Ensure values are rounded (pygame.Rect expects integers)
    top_margin = round(top_margin)
    bottom_margin = round(bottom_margin)

    pipeTop = Rect(screen.get_width(), 0, pipeWidth, top_margin)
    pipeBottom = Rect(screen.get_width(), screen.get_height() - bottom_margin, pipeWidth, bottom_margin)

    pipes.append(pipeTop)
    pipes.append(pipeBottom)

def events_handler():
    global running, paused, bird, pipes, first, deltaTime,justDied 
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
                    pipes.clear()
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

font = pygame.font.SysFont(None, screenSize[0] // 10)
#program run
while running:

    # event handling, gets all event from the event queue
    events_handler()
    
    # set the frame rate
    deltaTime = clock.tick(fps) / 1000
    bird.set_delta_time(dt=deltaTime)

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
        spawn_pipes(0.5)

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

    pygame.draw.rect(screen, "red", bird.get_player_hitbox())

    # Draw player sprite
    screen.blit(bird.currentFrame, bird.get_player_hitbox().topleft)

    # draw the pipes
    for pipe in pipes:
        # pygame.draw.rect(screen, (15, 171, 41), pipe)

        # Calculate scale factor (scale by width)
        scale_factor = pipe.width / pipe_sprite_width
        new_height = int(pipe_sprite_height * scale_factor)
    
        # Scale uniformly
        if pipe.top == 0:
            pipe_frame = pipe_frame_top
        else:
            pipe_frame = pipe_frame_bottom

        scaled_pipe = pygame.transform.scale(pipe_frame, (pipe.width, new_height))
    
        # Position
        if pipe.top == 0:
            # Align bottom of image with bottom of top pipe
            y = pipe.bottom - new_height
        else:
            # Align top of image with top of bottom pipe
            y = pipe.top
    
        # Draw
        screen.blit(scaled_pipe, (pipe.left, y))

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
    for pipe in pipes:
        pipe.move_ip(-screen.get_width()//2*deltaTime,0)  # move pipes to the left

    # pipe spawning
    try:
        if screen.get_width() < screen.get_height():
            if  pipes[len(pipes)-1][0] <= screen.get_width()/2 - pipeWidth*2:
                spawn_pipes()
        else:
            if  pipes[len(pipes)-1][0] <= screen.get_width()/1.25 - pipeWidth*2:
                spawn_pipes()
    except:
        if not pipes:
            spawn_pipes()

    # pipe remove
    for pipe in pipes:
        if not pipe.colliderect(screenCollider):
            pipes.remove(pipe)
    

    # collision detection
    for pipe in pipes:
        if pipe.colliderect(bird.get_player_hitbox()):
            pygame.time.set_timer(DIED, 1)  # set a timer for the DIED event
        
    if bird.get_player_hitbox()[1] < 0 or bird.get_player_hitbox()[1] > screenSize[1] - bird.get_height():
        pygame.time.set_timer(DIED, 1)  # set a timer for the DIED event

    

    # score calculation
    try:
        if pipes:
            if pipes[len(pipes)-3][0] < bird.get_player_hitbox()[0] and pipes[len(pipes)-3][0] > bird.get_player_hitbox()[0] - screen.get_width()//2*deltaTime:
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