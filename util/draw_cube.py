#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import pygame, sys
from pygame.locals import *
import random
from enum import IntEnum

#Number of frames per second
FPS = 10

# set up the colours
white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)
red = pygame.Color(255, 0, 0)
blue = pygame.Color(0, 0, 255)
orange = pygame.Color(255, 149, 0)
yellow = pygame.Color(245, 233, 10)
light_gray = pygame.Color(220, 220, 220)
light_blue = pygame.Color(66, 245, 224)
dark_gray = pygame.Color(100, 100, 100)

class Color(IntEnum):
    U = 0
    R = 1
    F = 2
    D = 3
    L = 4
    B = 5

class Corner(IntEnum):
    URF = 0
    UFL = 1
    ULB = 2
    UBR = 3
    DFR = 4
    DLF = 5
    DBL = 6
    DRB = 7


class Edge(IntEnum):
    UR = 0
    UF = 1
    UL = 2
    UB = 3
    DR = 4
    DF = 5
    DL = 6
    DB = 7
    FR = 8
    FL = 9
    BL = 10
    BR = 11


class Facelet(IntEnum):
    U1 = 0
    U2 = 1
    U3 = 2
    U4 = 3
    U5 = 4
    U6 = 5
    U7 = 6
    U8 = 7
    U9 = 8
    R1 = 9
    R2 = 10
    R3 = 11
    R4 = 12
    R5 = 13
    R6 = 14
    R7 = 15
    R8 = 16
    R9 = 17
    F1 = 18
    F2 = 19
    F3 = 20
    F4 = 21
    F5 = 22
    F6 = 23
    F7 = 24
    F8 = 25
    F9 = 26
    D1 = 27
    D2 = 28
    D3 = 29
    D4 = 30
    D5 = 31
    D6 = 32
    D7 = 33
    D8 = 34
    D9 = 35
    L1 = 36
    L2 = 37
    L3 = 38
    L4 = 39
    L5 = 40
    L6 = 41
    L7 = 42
    L8 = 43
    L9 = 44
    B1 = 45
    B2 = 46
    B3 = 47
    B4 = 48
    B5 = 49
    B6 = 50
    B7 = 51
    B8 = 52
    B9 = 53

class FaceCube:
    def __init__(self, cube_string="".join(c * 9 for c in "URFDLB")):
        """
        Initialise FaceCube from cube_string, if cube_string is not provided we
        initialise a clean cube.
        """
        self.f = [0] * 54
        for i in range(54):
            self.f[i] = Color[cube_string[i]]

    def to_string(self):
        """Convert facecube to cubestring"""
        return "".join(Color(i).name for i in self.f)

class draw_cube_face:
    def __init__(self, surface, startX, startY, cell_size, facecube):
        self.surface = surface
        self.startX = startX
        self.startY = startY
        self.gap = 2
        self.cellsize = cell_size+self.gap
        self.facesize = self.cellsize*3 #10(gaps)
        self.shiftWidth = startX + self.facesize*4 #4 faces
        self.shiftHeight = startY + self.facesize*2 # 3 row faces
        self.cell_size = cell_size
        self.facecube = facecube
        print(">>>", "".join(Color(i).name for i in facecube.f))
        grid = [[1, 0],[2, 1],[1, 1],[1, 2],[0, 1],[3, 1]] # U, R, F, D, L, B
        self.colorlist = [yellow, green, red, white, blue, orange] # U, R, F, D, L, B
        self.faces = []

        for x,y in grid:
            #print("x: ", x, "y: ", y)
            x_offset = x
            y_offset = y
            faceStartX = self.startX + x_offset * self.facesize
            faceStartY = self.startY + y_offset * self.facesize
            for yy in range(3):
                for xx in range(3):
                    self.faces.append(pygame.Rect(faceStartX+xx*self.cellsize, faceStartY+yy*self.cellsize, self.cell_size, self.cell_size)) 

    def draw(self):
        #color_string = "".join(Color(i).name for i in self.facecube.f)
        for  idx in range(len(self.faces)):
            rect = self.faces[idx]
            c = self.facecube.f[idx]
            #print(self.colorlist[c])
            pygame.draw.rect(self.surface, self.colorlist[c], rect)
            pygame.draw.rect(self.surface, dark_gray, rect, 2)
        pass

class cube_solver:
    def __init__(self, surface, width, height, cell_size):
        self.surface = surface
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.faces = {}

    def draw(self):
        pass

screen_width = 800
screen_height = 800
CellSize = 20
assert screen_width % CellSize == 0, "Window width must be a multiple of cell size"
assert screen_height % CellSize == 0, "Window height must be a multiple of cell size"




def main():
    pygame.init()
    pygame.display.set_caption('rubik\' cube') 
    surface = pygame.display.set_mode((screen_width,screen_height)) 
    surface.fill(white)
    fpsClock = pygame.time.Clock()
    
    #cube_faces = FaceCube() #FaceCube("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")
    #cube_faces = FaceCube("FDLUUURLFLBDFRRDLBBBUBFLDDLFBBUDUBRLURDFLRUFRFLRFBDUDR")
    cube_faces = FaceCube("DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL")

    #print(cube_faces.to_string())

    # init game of life object
    #cube_game = cube_solver(surface, screen_width, screen_height, CellSize)
    cube_draw = draw_cube_face(surface, 100, 100, CellSize, cube_faces)

    #main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        #cube_game.draw()
        cube_draw.draw()

        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()