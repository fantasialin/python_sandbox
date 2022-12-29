#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import pygame, sys
from pygame.locals import *
import random
from enum import IntEnum
#import optimal.solver as sv
import twophase.solver  as sv

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
        self.gap = 1
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
            pygame.draw.rect(self.surface, black, rect, 2)
        pass

class cube_op:
    def __init__(self):
        R_op_1 = [[3,6,9],[21,24,27],[30,33,36],[52,49,46],[10,11],[16,13],[18,17],[12,15]]
        R_op_2 = [[52,49,46],[3,6,9],[21,24,27],[30,33,36],[12,15],[10,11],[16,13],[18,17]]
        self.R_rotate = [R_op_1, R_op_2] # op_1 --> op_2 CW, op_2 -> op_1 CCW
        L_op_1 = [[1,4,7],[19,22,25],[28,31,34],[54,51,48],[37,38],[39,42],[45,44],[43,40]]
        L_op_2 = [[19,22,25],[28,31,34],[54,51,48],[1,4,7],[39,42],[45,44],[43,40],[37,38]]
        self.L_rotate = [L_op_1, L_op_2] # op_1 --> op_2 CW, op_2 -> op_1 CCW
        U_op_1 = [[19,20,21],[10,11,12],[46,47,48],[37,38,39],[3,6],[9,8],[7,4],[1,2]]
        U_op_2 = [[37,38,39],[19,20,21],[10,11,12],[46,47,48],[9,8],[7,4],[1,2],[3,6]]
        self.U_rotate = [U_op_1, U_op_2] # op_1 --> op_2 CW, op_2 -> op_1 CCW
        D_op_1 = [[25,26,27],[16,17,18],[52,53,54],[43,44,45],[28,29],[30,33],[36,35],[34,31]]
        D_op_2 = [[16,17,18],[52,53,54],[43,44,45],[25,26,27],[30,33],[36,35],[34,31],[28,29]]
        self.D_rotate = [D_op_1, D_op_2] # op_1 --> op_2 CW, op_2 -> op_1 CCW
        F_op_1 = [[7,8,9],[10,13,16],[30,29,28],[45,42,39],[19,20],[21,24],[27,26],[25,22]]
        F_op_2 = [[10,13,16],[30,29,28],[45,42,39],[7,8,9],[21,24],[27,26],[25,22],[19,20]]
        self.F_rotate = [F_op_1, F_op_2] # op_1 --> op_2 CW, op_2 -> op_1 CCW
        B_op_1 = [[1,2,3],[12,15,18],[36,35,34],[43,40,37],[46,47],[48,51],[54,53],[52,49]]
        B_op_2 = [[43,40,37],[1,2,3],[12,15,18],[36,35,34],[48,51],[54,53],[52,49],[46,47]]
        self.B_rotate = [B_op_1, B_op_2] # op_1 --> op_2 CW, op_2 -> op_1 CCW
        self.ops = ['F', 'R', 'B', 'L', 'U', 'D']
        self.ops_target = [self.F_rotate, self.R_rotate, self.B_rotate, self.L_rotate, self.U_rotate, self.D_rotate]

    def doOPS(self, facecube, target):
        idx = self.ops.index(target[0])
        #print("doOPS>>", target[0], " >> ", target[1], " idx >>", idx)
        if int(target[1]) == 3:          
            self.ROTATE(facecube,self.ops_target[idx], False)#print("do CCW")
        else:
            for i in range(int(target[1])):
                self.ROTATE(facecube,self.ops_target[idx], True)#print("do CW")


    def ROTATE(self, facecube, target, cw):  #cw ==True => CW, else CCW
        tmp = list(facecube.f)
        for idx in range(len(target[0])):
            f,t = None, None
            if cw == True:
                f = target[0][idx]
                t = target[1][idx]
            else:
                f = target[1][idx]
                t = target[0][idx]
            for i in range(len(f)):
                tmp[t[i]-1] = facecube.f[f[i]-1]
        facecube.f = list(tmp)

    def R_RCW(self, facecube, isCW):
        self.ROTATE(facecube, self.R_rotate, isCW)
 
    def L_RCW(self, facecube, isCW):
        self.ROTATE(facecube, self.L_rotate, isCW)
        
    def U_RCW(self, facecube, isCW):
        self.ROTATE(facecube, self.U_rotate, isCW)

    def D_RCW(self, facecube, isCW):
        self.ROTATE(facecube, self.D_rotate, isCW)

    def F_RCW(self, facecube, isCW):
        self.ROTATE(facecube, self.F_rotate, isCW)

    def B_RCW(self, facecube, isCW):
        self.ROTATE(facecube, self.B_rotate, isCW)


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

CW, ACW = 'CLOCKWISE', 'ANTICLOCKWISE'
F, B = 'FRONT', 'BACK'
R, L = 'RIGHT', 'LEFT'
U, D = 'UP', 'DOWN'

MOVE_KEY_MAP = {
    pygame.K_f: F,
    pygame.K_b: B,
    pygame.K_l: L,
    pygame.K_r: R,
    pygame.K_u: U,
    pygame.K_d: D,
}


def main():
    pygame.init()
    pygame.display.set_caption('rubik\' cube') 
    surface = pygame.display.set_mode((screen_width,screen_height)) 
    surface.fill(white)
    fpsClock = pygame.time.Clock()
    cubestring = 'DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL'
    #cube_faces = FaceCube("FDLUUURLFLBDFRRDLBBBUBFLDDLFBBUDUBRLURDFLRUFRFLRFBDUDR")
    cube_faces = FaceCube(cubestring)
    #cube_faces = FaceCube() #FaceCube("UUUUUUUUURRRRRRRRRFFFFFFFFFDDDDDDDDDLLLLLLLLLBBBBBBBBB")

    #print(cube_faces.to_string())
    sol_string = sv.solve(cubestring) 
    sol_steps = sol_string.split(' ')
    print(">>", sol_steps)
    


    # init game of life object
    #cube_game = cube_solver(surface, screen_width, screen_height, CellSize)
    cube_draw = draw_cube_face(surface, 100, 100, CellSize, cube_faces)
    op = cube_op()
    #op.R_RCW(cube_faces)

    for ops in sol_steps:
        if ops[0] in op.ops:
            #print(">>", ops)
            pass
        else:
            sol_steps.remove(ops) # remove not ops string

    supress_key_in = False
    solved = False
    current_steps = 0

    #main game loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                direction = ACW if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT] else CW
                if event.key in MOVE_KEY_MAP:
                    face = MOVE_KEY_MAP[event.key]
                    #print("op>> ", face, " direction>> ", direction)
                    if not supress_key_in:
                        if face == R:
                            op.R_RCW(cube_faces, direction == CW)
                        elif face == L:
                            op.L_RCW(cube_faces, direction == CW)
                        elif face == U:
                            op.U_RCW(cube_faces, direction == CW)
                        elif face == D:
                            op.D_RCW(cube_faces, direction == CW)
                        elif face == F:
                            op.F_RCW(cube_faces, direction == CW)
                        elif face == B:
                            op.B_RCW(cube_faces, direction == CW)
                elif event.key == pygame.K_SPACE:
                    print(">>>",cube_faces.to_string())
                elif event.key == pygame.K_s:# step to solve
                    supress_key_in = True
                    if not solved:
                        do_op = sol_steps[current_steps]
                        print(">>", do_op)
                        op.doOPS(cube_faces, do_op)
                        current_steps += 1 # next step
                        if current_steps >= len(sol_steps):
                            solved = True
                            print("Done, Solved!")

        #cube_game.draw()
        cube_draw.draw()

        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()