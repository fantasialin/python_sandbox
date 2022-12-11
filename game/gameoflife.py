#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# ref https://en.wikipedia.org/wiki/Conway's_Game_of_Life
#     http://trevorappleton.blogspot.com/2013/07/python-game-of-life.html
#  python gameoflife.py

import pygame, sys
from pygame.locals import *
import random


#Number of frames per second
FPS = 10

screen_width = 800
screen_height = 800
CellSize = 10
assert screen_width % CellSize == 0, "Window width must be a multiple of cell size"
assert screen_height % CellSize == 0, "Window height must be a multiple of cell size"
cell_width = screen_width // CellSize # number of cells wide
cell_height = screen_height // CellSize # Number of cells high

# set up the colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGRAY = (40, 40, 40)
GREEN = (0, 255, 0)

def drawGrid(surface):
    for x in range(0, screen_width, CellSize): # draw vertical lines
        pygame.draw.line(surface, DARKGRAY, (x,0),(x,screen_height))
    for y in range (0, screen_height, CellSize): # draw horizontal lines
        pygame.draw.line(surface, DARKGRAY, (0,y), (screen_width, y))

def blankGrid():
    gridDict = {}
    for y in range (cell_height):
        for x in range (cell_width):
            gridDict[x,y] = 0
    return gridDict

def initLife(life):
    for item in life:
        life[item] = random.randint(0,1)
    return life

def colourGrid(surface, item, life):
    x = item[0]
    y = item[1]
    y = y * CellSize # translates array into grid size
    x = x * CellSize # translates array into grid size
    if life[item] == 0:
        pygame.draw.rect(surface, WHITE, (x, y, CellSize, CellSize))
    if life[item] == 1:
        pygame.draw.rect(surface, GREEN, (x, y, CellSize, CellSize))
    return None

def showLife(surface, life):
    for cell in life:
        colourGrid(surface, cell, life)

def getNeighbours(item,life):
    neighbours = 0
    for x in range (-1,2): # -1, 0, 1
        for y in range (-1,2): # -1, 0, 1
            checkCell = (item[0]+x,item[1]+y)
            if checkCell[0] < cell_width  and checkCell[0] >=0: #boundary condition
                if checkCell [1] < cell_height and checkCell[1]>= 0: #boundary condition
                    if life[checkCell] == 1:
                        if x == 0 and y == 0: # self
                            pass
                        else:
                            neighbours += 1
    return neighbours

# rules
# 1. Any live cell with fewer than two live neighbours dies, as if by underpopulation.
# 2. Any live cell with two or three live neighbours lives on to the next generation.
# 3. Any live cell with more than three live neighbours dies, as if by overpopulation.
# 4. Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
def NextGeneration(life):
    newlife = {}
    for item in life:
        numberNeighbours = getNeighbours(item, life)
        if life[item] == 1:
            if numberNeighbours < 2: # kill under-population, case (1)
                newlife[item] = 0
            elif numberNeighbours > 3: #kill over-population, case (3)
                newlife[item] = 0
            else:
                newlife[item] = 1 # keep status quo (life), case (2)
        elif life[item] == 0:
            if numberNeighbours == 3: # cell reproduces, case (4)
                newlife[item] = 1
            else:
                newlife[item] = 0 # keep status quo (death)
    return newlife

def main():
    pygame.init()
    pygame.display.set_caption('game of life') 
    surface = pygame.display.set_mode((screen_width,screen_height)) 
    surface.fill(WHITE)
    fpsClock = pygame.time.Clock()
    
    life = blankGrid()
    initLife(life) # Assign random life

    #main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        # runs next iteration
        life = NextGeneration(life)
        # show life status
        showLife(surface, life)
        drawGrid(surface)
        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()