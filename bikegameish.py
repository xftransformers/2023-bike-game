x = 0
y = 0
import os
os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'

import pgzrun
import time
from pgzero.builtins import *
import pygame

startTime = time.time()
player = Actor('elf0', center=(150, 350), anchor=('center', 'bottom'))
player.speed = 1
player.frame = player.direction = 0
player.laneY = 375
score = dungeonPos = gametime = lastLap = 0
dungeon_background = [0, 2, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0,
                      0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0,
                      0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0]
muck = [0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,2,1,
         0,0,4,0,1,0,0,0,0,2,0,0,0,3,0,0,0,0,0,
         3,0,0,0,1,2,0,0,0,0,0,0,0,0,0,0,0,0,0]

class spritesheet(object):
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert()
        except pygame.error as message:
            print ('Unable to load spritesheet image:', filename)
            raise SystemExit(message)
    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        """Loads image from x,y,x+offset,y+offset"""
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colorkey is not None:
            if colorkey == -1:
                colorkey = image.get_at((0,0))
            image.set_colorkey(colorkey, pygame.RLEACCEL)
        return image
    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        """Loads multiple images, supply a list of coordinates"""
        return [self.image_at(rect, colorkey) for rect in rects]
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        """Loads a strip of images and returns them as a list"""
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

dungeon_assets = spritesheet(r'images/Medieval_tiles_free_2.0.png')
dungeon_rect = pygame.Rect((64,64),(48,48))

def tilerect(index, index2):
    rect = pygame.Rect(((index*48)-32,(index2*48)-80),(48,48))
    image = dungeon_assets.image_at(rect)
    return image

def draw():
    screen.blit('background', (0,0))
    drawTrack()
    player.draw()
    screen.draw.text("LAP TIME: " + str(int(time.time() - startTime)), (20, 555), color=(255, 255, 255), fontsize=50)
    screen.draw.text("LAST LAP: " + str(lastLap), topright=(780, 555), color=(255, 255, 255), fontsize=50)
    image = dungeon_assets.image_at(dungeon_rect)

def update():
    global dungeonPos, gametime, startTime, lastLap
    if keyboard.right and player.y == player.laneY:
        player.speed = limit(player.speed + 0.1, 1, 5)
    if keyboard.left and player.y == player.laneY:
        player.speed = limit(player.speed - 0.1, 1, 5)
    dungeonPos -= player.speed
    if(dungeonPos < -4800):
        dungeonPos = 0
        lastLap = int(time.time() - startTime)
        startTime = time.time()
    if round(player.y / 2) == round(player.laneY / 2):
        player.y = player.laneY
        player.angle = 0
    if player.direction != 0:
        if player.y <= 375 or player.y >= 525 or player.y == player.laneY:
            player.direction = 0
        else:
            player.y += player.direction * 2
    if (gametime%(int(15 - player.speed))==0):
        player.frame = 1 - player.frame
        a = player.angle
        player.image = "elf" + str(player.frame)
        player.angle = a
        checkBikeRamp()

def on_key_down(key):
    if key.name == "UP":
        player.direction = -1
        player.laneY = limit(player.laneY - 50, 375, 525)
    if key.name == "DOWN":
        player.direction = 1
        player.laneY = limit(player.laneY + 50, 375, 525)
    player.y += player.direction

def drawTrack():
    trackOffset = dungeonPos % 100
    trackBlock = int(-dungeonPos / 100)
    if trackOffset == 0:
        trackBlock -= 1
    for t in range(0,9):
        screen.blit("crowd1",((t*100)+trackOffset-100,0))
        screen.blit("rock1", ((t * 100) + trackOffset - 100, 270))
        screen.blit("rock1", ((t * 100) + trackOffset - 50, 270))
        if dungeon_background[trackBlock + t] == 0:
            screen.blit(tilerect(7,7), ((t*100)+trackOffset-98, 346))
        if dungeon_background[trackBlock + t] == 1:
            screen.blit("jump1", ((t*100)+trackOffset-100, 300))
        if dungeon_background[trackBlock + t] == 2:
            screen.blit("track2", ((t*100)+trackOffset-100, 300))
        if muck[trackBlock+t] > 0:
            screen.blit("muck1",((t*100)+trackOffset-100, 295+(muck[trackBlock+t])*50))

def checkBikeRamp():
    tp = dungeonPos + 25
    trackOffset = tp%100
    trackBlock = int((-tp)/100)+2
    trackheight = 0
    if trackOffset == 0:
        trackBlock -= 1
    if dungeon_background[trackBlock] == 1:
        trackheight = (100-trackOffset)
        if player.y >= player.laneY-trackheight:
            player.y = player.laneY - trackheight
            if player.angle < 45:
                player.angle += player.speed
        if player.angle < -25:
            player.speed = 1
            player.angle = 0
        if player.angle >= -25 and player.angle < 0:
            player.angle = 0
    else:
        if int(player.y) == int(player.laneY) and player.angle < -25:
            player.angle = 0
            player.speed = 1
    if player.y < player.laneY-trackheight and player.direction != 1:
        player.y += (2 - (player.speed / 3))
        if player.direction == 0:
            player.angle -= 1
        if player.speed > 1:
            player.speed -= 0.02
    muckLane = int((player.laneY - 375) / 50) + 1
    if muck[trackBlock] == muckLane and int(player.y) == int(player.laneY):
        player.speed = player.speed / 1.1

def limit(n, minn, maxn):
    return max(min(maxn, n), minn)

pgzrun.go()