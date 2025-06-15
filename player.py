import pygame

class Player:
    
    def __init__(self,playerHeight,playerWidth,playerX,playerY,jumpHeight,gravity):
        # player size 
        self.playerHeight = playerHeight
        self.playerWidth = playerWidth
        # player location
        self.playerPos = pygame.Vector2(playerX,playerY)
        
        # player sprite data
        self.player_sprite_sheet = pygame.image.load("player.png").convert_alpha()
        self.player_sprite_height = self.player_sprite_sheet.get_height() 
        self.player_sprite_width = self.player_sprite_sheet.get_width() // 3
        # player frames up down and dead
        self.player_frame_up = self.player_sprite_sheet.subsurface(pygame.Rect(0, 0, self.player_sprite_width, self.player_sprite_height))
        self.player_frame_down = self.player_sprite_sheet.subsurface(pygame.Rect( self.player_sprite_width,0, self.player_sprite_width, self.player_sprite_height))
        self.player_frame_dead = self.player_sprite_sheet.subsurface(pygame.Rect( self.player_sprite_width*2,0, self.player_sprite_width, self.player_sprite_height))

        # player jump data
        self.isJumping = False
        self.jumpped = False
        self.jumpHeight = jumpHeight
        self.yVelocity = jumpHeight
        
        # gravity
        self.gravity = gravity
        # delta time
        self.deltaTime = 0

        # score
        self.score = 0

        # death data
        self.died = False
        self.justDied = False


        # player hitbox, used for collision detection
        self.playerHitbox = pygame.Rect(self.playerPos.x - self.playerWidth/2, self.playerPos.y - self.playerHeight/2, self.playerWidth,self.playerHeight) 
        
        # player current selected frame
        self.currentFrame = pygame.transform.scale(self.player_frame_up, (self.playerHitbox.width, self.playerHitbox.height))
        
        pass
        
    def get_height(self):
        return self.playerHeight
    
    def get_width(self):
        return self.playerWidth
    
    def get_Y(self):
        return self.playerPos.y

    def get_X(self):
        return self.playerPos.x
    
    def get_died(self):
        return self.died
    
    def set_died(self,died):
        self.died = died
        self.set_current_frame(self.player_frame_dead)
    
    def get_just_died(self):
        return self.justDied
    
    def set_just_died(self,justDied):
        self.justDied = justDied

    def get_player_hitbox(self):
        return self.playerHitbox
    
    def get_score(self):
        return self.score
    
    def set_score(self,score):
        self.score=score
    
    def set_current_frame(self,frame):
        self.currentFrame = pygame.transform.scale(frame, (self.playerHitbox.width, self.playerHitbox.height))
    
    def get_current_frame(self):
        return self.currentFrame
    
    def get_delta_time(self):
        return self.deltaTime

    def set_delta_time(self,dt):
        self.deltaTime = dt

    def reset_player(self,location):
        self.playerPos = location
        self.playerHitbox = pygame.Rect(self.playerPos.x - self.playerWidth/2, self.playerPos.y - self.playerHeight/2, self.playerWidth, self.playerHeight)
        self.yVelocity = self.jumpHeight
        self.isJumping = False
        self.jumpped = False
        self.died = False
        self.deltaTime = 0
        self.score = 0
        self.set_current_frame(self.player_frame_down)

    def jumping(self,keys_pressed):

        # if pressed space do jump
        if keys_pressed[pygame.K_SPACE]:
            self.isJumping = True
            self.jumpped = True
        else:
            self.jumpped = False

        # jumping algorithem
        if self.isJumping:
            self.playerPos.y -= self.yVelocity * self.deltaTime # move player up
            self.yVelocity -= self.gravity * self.deltaTime # reduce y velocity

            # if y velocity is lower then zero start falling animation
            if self.yVelocity <  self.jumpHeight / 2:
                self.set_current_frame( self.player_frame_down) # set falling frame
                if self.jumpped:
                    self.yVelocity = self.jumpHeight # reset jump power
            # otherwise use jumping animation
            else:
                self.set_current_frame(self.player_frame_up) # set jumping frame
            # transition between falling after jumping and free falling
            if self.yVelocity <= -self.gravity:
                self.isJumping = False
                
        # fall using gravity
        else:
            self.set_current_frame(self.player_frame_down)
            self.playerPos.y += self.gravity * self.deltaTime
        
        # Update hitbox location
        self.playerHitbox.topleft = (self.playerPos.x - self.playerWidth / 2, self.playerPos.y - self.playerHeight / 2)
