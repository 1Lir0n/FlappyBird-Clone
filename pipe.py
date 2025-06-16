import pygame
import random

class Pipes:

    def __init__(self,surface:pygame.Surface,playerHeight):
        self.rnd=random.Random()

        self.pipes = []
        # pipes sheet
        # sprite
        self.pipes_sprite_sheet = pygame.image.load("pipes.png").convert_alpha()
        self.pipe_sprite_height = self.pipes_sprite_sheet.get_height()
        self.pipe_sprite_width = self.pipes_sprite_sheet.get_width()//2

        self.topFrame = self.pipes_sprite_sheet.subsurface(pygame.Rect(self.pipe_sprite_width,0, self.pipe_sprite_width, self.pipe_sprite_height))
        self.bottomFrame = self.pipes_sprite_sheet.subsurface(pygame.Rect(0,0, self.pipe_sprite_width, self.pipe_sprite_height))

        self.surface = surface

        self.pipeHeight = self.surface.get_height()
        self.pipeWidth = self.surface.get_width() * 0.1
        self.playerHeight = playerHeight
        self.gapSize = int(self.playerHeight * 4)

        self.scaleFactor = self.pipeWidth/self.pipe_sprite_width
        self.newHeight = int(self.pipe_sprite_height*self.scaleFactor)

        self.topFrame = pygame.transform.scale(self.topFrame,( self.pipeWidth, self.newHeight))
        self.bottomFrame = pygame.transform.scale(self.bottomFrame, (self.pipeWidth, self.newHeight))

        self.topPipe = pygame.Rect(self.surface.get_width(), 0, self.pipeWidth, self.pipeHeight)
        self.bottomPipe = pygame.Rect(self.surface.get_width(), 0, self.pipeWidth, self.pipeHeight)

        self.deltaTime = 0

    def set_delta_time(self,dt):
        self.deltaTime = dt
    
    def get_delta_time(self):
        return self.deltaTime  
    
    def get_top_frame(self):
        return self.topFrame
    
    def get_frame_height(self):
        return self.newHeight
    
    def get_bottom_frame(self):
        return self.bottomFrame

    def add_pipe_at_end(self,pipe):
        self.pipes.append(pipe)

    def add_pipe_at_start(self,pipe):
        self.pipes.insert(0,pipe)

    def remove_pipe(self,pipe):
        self.pipes.remove(pipe)
    
    def clear_pipes(self):
        self.pipes.clear()

    def get_pipe_width(self):
        return self.pipeWidth
    
    def get_pipe_height(self):
        return self.pipeHeight
    
    def get_pipes(self):
        return self.pipes
    
    def move_pipes(self):
        for pipe in self.pipes:
           pipe.move_ip(-self.surface.get_width()//2*self.deltaTime,0)  # move pipes to the left
    """
    TODO:
    make it so it spawns pipes at an area from the last spawned pipe so edge case is fine
    """
    def spawn_pipes(self,gapSize = -1,gapLocation = 0.5):
        min_visible_pipe_height = self.surface.get_height()*0.05
        if gapSize<0 or gapSize>self.surface.get_height():
            gapSize = self.gapSize
        gapHalf = gapSize/2
        minCenter = (min_visible_pipe_height + gapHalf)/self.pipeHeight
        maxCenter = 1 - minCenter

        if gapLocation > 1 or gapLocation < 0:
            gapLocation = self.rnd.uniform(minCenter,maxCenter)

        topMargin = gapLocation * self.pipeHeight - gapSize / 2
        bottomMargin = self.pipeHeight - (gapLocation * self.pipeHeight + gapSize / 2)

        topMargin = round(topMargin)
        bottomMargin = round(bottomMargin)

        self.topPipe = pygame.Rect(self.surface.get_width(), 0, self.pipeWidth, topMargin)
        self.bottomPipe = pygame.Rect(self.surface.get_width(), self.surface.get_height() - bottomMargin, self.pipeWidth, bottomMargin)

        self.pipes.append(self.topPipe)
        self.pipes.append(self.bottomPipe)

    def draw_pipes(self):
        for pipe in self.pipes:
            if pipe.y == 0:
                y = pipe.bottom - self.newHeight
                self.surface.blit(self.topFrame, (pipe.left, y))
            else:
                y = pipe.top
                self.surface.blit(self.bottomFrame, (pipe.left, y))
        