#!/usr/bin/python3
# -*- coding: UTF-8 -*-

# ref https://en.wikipedia.org/wiki/Conway's_Game_of_Life
#     http://trevorappleton.blogspot.com/2013/07/python-game-of-life.html
#  python gameoflife2.py

import pygame, sys
from pygame.locals import *
import random


#Number of frames per second
FPS = 10

class game_of_life:

    def __init__(self, surface, width, height, cell_size, cell_color, cell_blank, grid_color):
        self.surface = surface
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cell_width = width // cell_size # number of cells wide
        self.cell_height = height // cell_size # Number of cells high
        self.cell_color = cell_color
        self.cell_blank_color = cell_blank
        self.grid_color = grid_color
        self.life = {}
        self.blankGrid()
        self.initLife() # Assign random life

    def drawGrid(self):
        for x in range(0, self.width, self.cell_size): # draw vertical lines
            pygame.draw.line(self.surface, self.grid_color, (x,0),(x,self.height))
        for y in range (0, self.height, self.cell_size): # draw horizontal lines
            pygame.draw.line(self.surface, self.grid_color, (0,y), (self.width, y))

    def blankGrid(self):
        for y in range (self.cell_height):
            for x in range (self.cell_width):
                self.life[x,y] = 0

    def initLife(self):
        for cell in self.life:
            self.life[cell] = random.randint(0,1)

    def colourGrid(self, cell):
        x = cell[0]
        y = cell[1]
        y = y * self.cell_size # translates array into grid size
        x = x * self.cell_size # translates array into grid size
        rect = pygame.Rect(x, y, self.cell_size, self.cell_size)
        if self.life[cell] == 0:
            pygame.draw.rect(self.surface, self.cell_blank_color, rect)
        if self.life[cell] == 1:
            pygame.draw.rect(self.surface, self.cell_color, rect)


    def showLife(self):
        for cell in self.life:
            self.colourGrid(cell)
        self.drawGrid()

    def getNeighbours(self, cell):
        neighbours = 0
        for x in range (-1,2): # -1, 0, 1
            for y in range (-1,2): # -1, 0, 1
                checkCell = (cell[0]+x,cell[1]+y)
                if checkCell[0] < self.cell_width  and checkCell[0] >=0: #boundary condition
                    if checkCell [1] < self.cell_height and checkCell[1]>= 0: #boundary condition
                        if self.life[checkCell] == 1:
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
    def NextGeneration(self):
        newlife = {}
        for cell in self.life:
            numberNeighbours = self.getNeighbours(cell)
            if self.life[cell] == 1:
                if numberNeighbours < 2: # kill under-population, case (1)
                    newlife[cell] = 0
                elif numberNeighbours > 3: #kill over-population, case (3)
                    newlife[cell] = 0
                else:
                    newlife[cell] = 1 # keep status quo (life), case (2)
            elif self.life[cell] == 0:
                if numberNeighbours == 3: # cell reproduces, case (4)
                    newlife[cell] = 1
                else:
                    newlife[cell] = 0 # keep status quo (death)
        self.life = newlife

screen_width = 800
screen_height = 800
CellSize = 10
assert screen_width % CellSize == 0, "Window width must be a multiple of cell size"
assert screen_height % CellSize == 0, "Window height must be a multiple of cell size"

# set up the colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGRAY = (40, 40, 40)
GREEN = (0, 255, 0)


def main():
    pygame.init()
    pygame.display.set_caption('game of life') 
    surface = pygame.display.set_mode((screen_width,screen_height)) 
    surface.fill(WHITE)
    fpsClock = pygame.time.Clock()
    
    # init game of life object
    game = game_of_life(surface, screen_width, screen_height, CellSize, GREEN, WHITE, DARKGRAY)

    #main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        # runs next iteration
        game.NextGeneration()
        # show life status
        game.showLife()

        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()