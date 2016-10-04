#!/usr/bin/env python

# ---------------------- IMPORTS ---------------------
from pygame import sprite, image, mixer, Surface
from math import sqrt
from constants6 import GRAVITY, MAX_FALL_VELOCITY, COLORS, FPS, ROOT
''' A parent class for all sprites in the game screen, such as the main player,
    all kind of platforms, enemies and so on.'''


# General Block sprite class
class _Block(sprite.Sprite):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height):
        # -- Parent constructor ---------------
        super().__init__()                              # sprite.Sprite.__init__(self)
        self.name = "Block"
        # Animation settings
        self.fps = FPS                                  # Frame Rate
        self.refresh = 0                                # Delay for frame animations
        self.velX = 0
        self.velY = 0
        # We create the block's surface
        self.image = Surface([width, height])
        # We fill this 'surface' with a color
        self.image.fill(color)
        # We get the 'collider' box
        self.rect = self.image.get_rect()

    # ---------- Methods --------------------------
    def get_rect(self):
        return self.rect


# It's alive! Class for animated blocks, with some additions
class _AnimatedBlock(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height):
        # -- Parent constructor ---------------
        super().__init__(color, width, height)
        # Animation attributes
        self.imageList = []                             # Tile container
        self.imageListIndex = 0                         # Tile pointer on animation

    # ---------- Methods --------------------------
    # It loads all tiles incoming from a specified folder
    def set_frames(self, origin, quantity):
        for i in range(quantity):
            self.imageList.append(image.load(ROOT + '/images/' + origin + str(i+1) + '.png').convert())


# Evil army! This class is for all enemy objects (It will extend from _AnimatedBlock in a future; Still lacks tiles)
class _Enemy(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height):
        super().__init__(color, width, height)
        self.life = 0                           # Enemy's life count
        self.isDead = False                     # Enemy's state
        self.firstX = 0


#
class Platform(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height, init_coords, axis='X'):
        super().__init__(color, width, height)
        self.name = "Platform"
        self.initCoords = init_coords
        self.velX = self.velY = 1
        self.maxRun = 50                             # Moving limit
        self.axis = axis

    # ------------ Methods ------------------------
    def update(self):
        # if self.refresh < self.fps:
        #     self.refresh += self.fps
        # else:
        # The current position it's still into the limits
        if self.maxRun >= abs(self.rect.x - self.initCoords[0]) \
                and self.maxRun >= abs(self.rect.y - self.initCoords[1]):
            # It's moving in the X or Y axis?
            if self.axis == 'X':
                self.rect.x += self.velX
            elif self.axis == 'Y':
                self.rect.y += self.velY
        elif self.maxRun < abs(self.rect.x - self.initCoords[0]):
            # We convert the velocity value to its opposite
            self.velX *= -1
            self.rect.x += self.velX
        elif self.maxRun < abs(self.rect.y - self.initCoords[1]):
            # We convert the velocity value to its opposite
            self.velY *= -1
            self.rect.y += self.velY

        # We reset the refresh rating
        # self.refresh = 0


class Snow(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height, screen_size):
        super().__init__(color, width, height)
        self.name = "Snow"
        self.screen_size = screen_size
        self.firstX = 0
        self.acc = 5

    # ---------- Methods --------------------------
    # Update method
    def update(self):
        self.rect.y += 1
        if self.rect.y > self.screen_size[1]:
            self.rect.y = -1

    # Function for falling snow flakes
    def bounce(self):
        if self.rect.x == self.firstX:
            pass
        else:
            pass


# Class for ground floor tiles
class Floor(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height):
        super().__init__(color, width, height)      # Block.__init__(self, color, width, height)
        self.name = "Floor"


# Class for coins
class Coin(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height):
        super().__init__(color, width, height)
        self.name = "Coin"
        self.image = image.load(ROOT + '/images/Coin_Frames/coin.png').convert()
        # We set a transparent color for the image
        self.image.set_colorkey(COLORS['WHITE'])


# Class for hole tiles
class Hole(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height, img=None):
        super().__init__(color, width, height)
        self.name = "Hole"
        if img is not None:
            self.image = image.load(ROOT + '/images/plain_hole/' + img + '.png').convert()


# Class for saving point tiles
class SavePoint(_AnimatedBlock):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height):
        super().__init__(color, width, height)  # Block.__init__(self, color, width, height)
        self.name = "SavePoint"
        # Animation image frames
        self.set_frames('SP_Frames/save_point', 12)
        self.image = self.imageList[self.imageListIndex]
        # We set a transparent color for the image
        self.image.set_colorkey(COLORS['BLACK'])

    # ---------- Methods --------------------------
    # Update method for animation
    def update(self):
        # We configure the refresh rating here
        if self.refresh < self.fps:
            self.refresh += self.fps / 2
        else:
            # We switch the current tile to next in a concrete sequence
            if self.imageListIndex < len(self.imageList) - 1:
                self.imageListIndex += 1
            else:
                self.imageListIndex = 0
            self.image = self.imageList[self.imageListIndex]
            self.image.set_colorkey(COLORS['BLACK'])
            # We reset the refresh state
            self.refresh = 0


# Class for the player character (It will extend from _AnimatedBlock in a future; Still lacks tiles)
class Player(_Block):
    # ---------- Constructor ----------------------
    def __init__(self, color, width, height, save_file=None):
        super().__init__(color, width, height)      # Block.__init__(self, color, width, height)
        # We set its conditions depending on the save file
        if save_file is not None:
            self.name = save_file['Name']
            self.life = save_file['Life'][0]
            self.maxLife = save_file['Life'][1]
            self.energy = save_file['Energy'][0]
            self.maxEnergy = save_file['Energy'][1]
            self.coins = save_file['Coins'][0]
            self.maxWallet = save_file['Coins'][1]
        else:
            # These attributes could be higher across the game, by power-ups that increase this limits
            self.name = "Player"
            self.life = self.maxLife = 100
            self.energy = self.maxEnergy = 100
            self.coins = 5
            self.maxWallet = 100
        # Insert here your favourite sound, and all coins will go 'tink' when you touch them!
        self.coinSound = mixer.Sound(ROOT + '/sounds/coin.wav')
        self.maxFallVelocity = MAX_FALL_VELOCITY    # A limit to gravity acceleration
        self.saveFlag = False                       # Enable/Disable saving feature
        self.plainLevel = False                     # Enable/Disable horizontal gravity
        self.jumping = False                        # Jumping state flag
        self.isDead = False                         # Living state flag

    # ---------- Methods --------------------------
    # Update method
    def update(self, solid, weak):
        # Collecting all 'solid' boxes (they don't vanish for colliding)
        solid_boxes = solid
        # Collecting all 'weak' boxes (they'll disappear for colliding)
        weak_boxes = weak
        # Cleaning flags
        if self.saveFlag:
            self.saveFlag = False
        # ------- HORIZONTAL CHECKING -------------------
        # We move the player on the X axis
        self.rect.x += self.velX
        # We merge all collisions done in two lists (False for avoiding automatic drop)
        solid_collide_list = sprite.spritecollide(self, solid_boxes, False)
        weak_collide_list = sprite.spritecollide(self, weak_boxes, True)
        for body in solid_collide_list:
            if isinstance(body, Floor) or isinstance(body, Platform):
                # Moving to the right
                if self.velX > 0:
                    self.rect.right = body.get_rect().left
                # Moving to the left
                elif self.velX < 0:
                    self.rect.left = body.get_rect().right
            elif isinstance(body, Hole):
                if self.distance(self.rect.centerx, self.rect.centery,
                                 body.get_rect().centerx, body.get_rect().centery) < body.rect.width*0.75:
                    if self.rect.x > body.get_rect().x:
                        self.rect.x -= 2
                    elif self.rect.x < body.get_rect().x:
                        self.rect.x += 2
            elif isinstance(body, SavePoint):
                if self.distance(self.rect.centerx, self.rect.centery,
                                 body.get_rect().centerx, body.get_rect().centery) < body.rect.width / 2:
                    self.saveFlag = True

        for body in weak_collide_list:
            if isinstance(body, Snow):
                self.life -= 1
                if self.life <= 0:
                    self.isDead = True
            elif isinstance(body, Coin):
                # It prevents us for taking more coins than we can get
                if self.coins < self.maxWallet:
                    self.coins += 1
                self.coinSound.play()

        # ------- VERTICAL CHECKING -------------------
        # We move the player on the Y axis
        self.rect.y += self.velY
        # We merge all collisions done in two lists (False for avoiding automatic drop)
        solid_collide_list = sprite.spritecollide(self, solid_boxes, False)
        weak_collide_list = sprite.spritecollide(self, weak_boxes, True)
        for body in solid_collide_list:
            if isinstance(body, Floor) or isinstance(body, Platform):
                # Wall under the player
                if self.velY > 0:
                    self.stop_fall()
                    self.rect.bottom = body.get_rect().top
                # Wall upon the player
                elif self.velY < 0:
                    self.stop_y()
                    self.rect.top = body.get_rect().bottom

            elif isinstance(body, Hole):
                if self.distance(self.rect.centerx, self.rect.centery,
                                      body.get_rect().centerx, body.get_rect().centery) < body.rect.width*0.75:
                    if self.rect.y > body.get_rect().y:
                        self.rect.y -= 2
                    elif self.rect.y < body.get_rect().y:
                        self.rect.y += 2

            elif isinstance(body, SavePoint):
                if self.distance(self.rect.centerx, self.rect.centery,
                                 body.get_rect().centerx, body.get_rect().centery) < body.rect.width / 2:
                    self.saveFlag = True

        for body in weak_collide_list:
            if isinstance(body, Snow):
                self.life -= 1
                if self.life <= 0:
                    self.isDead = True
                    return True
            elif isinstance(body, Coin):
                # It prevents us for taking more coins than we can get
                if self.coins < self.maxWallet:
                    self.coins += 1
                self.coinSound.play()

        if not self.plainLevel:
            self.fall()

    # X movement to the left
    def go_left(self):
        # print "Goin' left"
        self.velX = -3

    # X movement to the right
    def go_right(self):
        # print "Goin' right"
        self.velX = 3

    # Y up movement (Only used on plain levels)
    def go_up(self):
        self.velY = -3

    # Y down movement (Only used on plain levels)
    def go_down(self):
        self.velY = 3

    # Stop for the X axis
    def stop_x(self):
        # print "Stoppin'"
        self.velX = 0

    # Stop for the X axis
    def stop_y(self):
        # print "Stoppin'"
        self.velY = 0

    # Y movement for jumping
    def jump(self):
        # print "Jumpin'"
        if not self.jumping:
            self.velY = -10
            self.jumping = True

    # Stop for the Y axis
    def stop_fall(self):
        # print "Fall complete"
        self.velY = 0
        self.jumping = False

    # This is a simple gravity calculus for player's fall velocity
    def fall(self):
        # print "Falling"
        self.velY += GRAVITY
        if self.velY > self.maxFallVelocity:
            self.velY = self.maxFallVelocity

    # Calculates a distance between central points of the player and other bodies
    def distance(self, player_center_x, player_center_y, body_center_x, body_center_y):
        # It emulates the following formula:
        #        _____________________________
        #  d = \/(x_2 - x_1)^2 + (y_2 - y_1)^2
        x_1 = player_center_x * 1.0
        y_1 = player_center_y * 1.0
        x_2 = body_center_x * 1.0
        y_2 = body_center_y * 1.0
        # Calculation time
        x_operator = (x_2 - x_1) * (x_2 - x_1)
        y_operator = (y_2 - y_1) * (y_2 - y_1)
        return sqrt(x_operator + y_operator)
