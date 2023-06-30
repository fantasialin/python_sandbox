#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import pygame, sys
from pygame.locals import *
import random
import math


#Number of frames per second
FPS = 10

screen_width = 800
screen_height = 600

# set up the colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARKGRAY = (40, 40, 40)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
orange = (245, 138, 66)
light_gray = (220, 220, 220)
light_blue = (66, 245, 224)
dark_gray = (100, 100, 100)

gridOriginX = 20
gridOriginY = 20
gridWidth = 20
gridHeight = 20
hexSize = 20
hexWidth = (3.0/2.0) * hexSize
hexHeight = math.sqrt(3.0) * hexSize

class draw_hexagon:
    def __init__(self, surface, width, height, draw_width, draw_height, **kwargs):
        self.surface = surface
        self.width = width
        self.height = height
        self.draw_width = draw_width
        self.draw_height = draw_height
        self.visible = True
        self.isEnabled = True
        self.isPause = False
        self.x_offset = kwargs.get('x_offset', 0)
        self.y_offset = kwargs.get('y_offset', 0)
        self.win_area = pygame.Rect(0, 0, draw_width, draw_height)
        self.draw_area = pygame.Rect(self.x_offset, self.y_offset, draw_width+self.x_offset, draw_height+self.y_offset)
        self.image = pygame.Surface((draw_width, draw_height))
        self.Hex = []
        self.selected_cell = []
        self.Hex_coord = {}
        # Draw Hex Grid
        for y in range(0,gridHeight,1):
            for x in range(0,gridWidth, 1):
                centreX = int(gridOriginX + x*hexWidth)
                centreY = int(gridOriginY + y*hexHeight)
                if x % 2 == 0:
                    centreY += int(hexHeight/2.0)
                hex_ = self.genHexagon(centreX, centreY, hexSize)
                tmp = {}
                tmp["x_idx"] = x
                tmp["y_idx"] = y
                tmp["area"] = hex_
                tmp["highlight"] = False
                tmp["aabb"] = self.aabb(hex_)
                self.Hex_coord[x,y] = tmp
                self.Hex.append(tmp)
        ''' # for test one cell
        hex_ = self.genHexagon(100, 100, hexSize)
        tmp = {}
        tmp["x_idx"] = 0
        tmp["y_idx"] = 0
        tmp["area"] = hex_
        tmp["highlight"] = False
        tmp["aabb"] = self.aabb(hex_)
        self.Hex_coord[0,0] = tmp
        self.Hex.append(tmp)
        '''

    # destructor
    def __del__(self):
        pass

    def genHexagon(self, x, y, radius):
        hexPoints = []
        for i in range(6):
            angle = 60.0*float(i)
            angle_rad = (math.pi/180.0) * angle
            x_ = x + radius*math.cos(angle_rad)
            y_ = y + radius*math.sin(angle_rad)
            hexPoints.append((int(x_),int(y_)))
        # repeat the first vertex at end, not affect draw polygon but help point in hexagon detection
        hexPoints.append((hexPoints[0][0],hexPoints[0][1]))
        return hexPoints
    
    def aabb(self, points):
        x_min = points[0][0]
        y_min = points[0][1]
        x_max = points[0][0]
        y_max = points[0][1]

        for point in points:
            if point[0] < x_min: x_min = point[0]
            elif point[0] > x_max: x_max = point[0]
            if point[1] < y_min: y_min = point[1]
            elif point[1] > y_max: y_max = point[1]
        # return a pygrame rect for mouse event collide detection
        return pygame.Rect(x_min,y_min,x_max-x_min,y_max-y_min)

    def draw(self):
        # draw self
        self.image.fill((240,240,240))
        # draw lines to off screen surface
        for a in self.Hex:
            if a["highlight"] == True:
                pygame.draw.polygon(self.image, WHITE, a["area"])
                pygame.draw.aalines(self.image, RED, True, a["area"], 2)
            else:
                pygame.draw.polygon(self.image, orange, a["area"])
                pygame.draw.aalines(self.image, DARKGRAY, True, a["area"], 2)
        ''' # for test
        for a in self.Hex:
            #for v in a["area"]:
            v = a["area"][0]
            pygame.draw.circle(self.image, RED, (v[0], v[1]), 2)
            v = a["area"][1]
            pygame.draw.circle(self.image, GREEN, (v[0], v[1]), 2)
        '''
        for s in self.selected_cell:
            cell = self.Hex_coord[s]
            pygame.draw.polygon(self.image, light_blue, cell["area"])
            pygame.draw.aalines(self.image, BLUE, True, cell["area"], 4)

        if len(self.selected_cell) > 0:
            pass
        #self.child.draw()

        # bitblt
        self.surface.blit(self.image, self.draw_area)
    '''
    crossing number test for a point in a polygon
    P = a point
    v[] = vetex points of a polygon V[n+1] with V[n] = V[0]
    0 = outside, 1 = inside
    This code is patterned after [Franklin, 2000]
    '''
    def hex_cn_PnPoly(self, point, polygon):
        cn = 0    # the crossing number counter
        vertex_count = len(polygon) - 1
        # loop through all edges of the polygon
        for i in range(vertex_count):
            if ((polygon[i][1] <= point[1] and polygon[i+1][1] > point[1])   # an upward crossing
                or (polygon[i][1] > point[1] and polygon[i+1][1] <= point[1])):  # a downward crossing
                # compute the actual edge-ray intersect x-coordinate
                vt = (point[1] - polygon[i][1]) / float(polygon[i+1][1] - polygon[i][1])
                if point[0] < polygon[i][0] + vt * (polygon[i+1][0] - polygon[i][0]): # P[0] < intersect
                    cn += 1  # a valid crossing of y=P[1] right of P[0]

        return cn % 2   # 0 if even (out), and 1 if odd (in)

    # reference : https://www.algorithms-and-technologies.com/point_in_polygon/python
    def hex_collide(self, point, polygon):
        odd = False
        vertex_count = len(polygon) - 1
        for i in range(vertex_count):
            # If a line from the point into infinity crosses this edge
            # One point needs to be above, one below our y coordinate
            # ...and the edge doesn't cross our Y corrdinate before our x coordinate 
            # (but between our x coordinate and infinity)
            if (((polygon[i][1] > point[1]) != (polygon[i+1][1] > point[1])) and 
                (point[0] < 
                 ((polygon[i+1][0] - polygon[i][0]) * (point[1] - polygon[i][1]) / (polygon[i+1][1] - polygon[i][1])) + polygon[i][0])):
                # Invert odd
                odd = not odd
        # If the number of crossings was odd, the point is in the polygon
        return odd
    
    '''
    tests if a point is Left/On/Right of an infinite line.
    three points P0, P1, and P2
    >0 for P2, left of the line through P0 and p1
    =0 for P2, on the line
    <0 for P2, right of the line
    ((P1.x - P0.x) * (P2.y - P0.y)
      - (P2.x - P0.x) * (P1.y - P0.y))
    '''
    def insideHexagon(self, point, polygon):
        vertex_count = len(polygon) - 1
        for i in range(vertex_count):
            D = ((polygon[i+1][0] - polygon[i][0]) * (point[1] - polygon[i][1]) 
                 - (point[0] - polygon[i][0]) * (polygon[i+1][1] - polygon[i][1]))
            if D <= 0:
                return False
        return True


    def handleEvent(self, Event):
        if self.visible and self.isEnabled:
            point = (int(Event.pos[0] - self.x_offset), int(Event.pos[1] - self.y_offset))
            if Event.type == MOUSEBUTTONDOWN :
                #print(f' event pos -> {Event.pos} offset {point}')
                for a in self.Hex:
                    #if self.hex_collide(point,a["area"]):
                    if a["aabb"].collidepoint(point):
                        #print(f' event pos -> {point} --> {a["area"]}')
                        #if self.hex_collide(point,a["area"]):
                        #if self.hex_cn_PnPoly(point,a["area"]):
                        if self.insideHexagon(point,a["area"]):
                            #print(f'haxagon grid x, y --> {a["x_idx"]}, {a["y_idx"]}')
                            target = (a["x_idx"], a["y_idx"])
                            if target in self.selected_cell:
                                self.selected_cell.remove(target)
                            else:
                                self.selected_cell.append(target)
            elif Event.type == MOUSEMOTION:
                for a in self.Hex:
                    if a["aabb"].collidepoint(point):
                        #if self.hex_collide(point,a["area"]):
                        #if self.hex_cn_PnPoly(point,a["area"]):
                        if self.insideHexagon(point,a["area"]):
                            a["highlight"] = True
                        else:
                            a["highlight"] = False
                    else:
                        a["highlight"] = False

            #self.child.handleEvent(Event)
            pass



def main():
    pygame.init()
    pygame.display.set_caption('draw hexagons') 
    surface = pygame.display.set_mode((screen_width,screen_height)) 
    surface.fill(WHITE)
    fpsClock = pygame.time.Clock()

    offset = (screen_width - 500)/2

    HexMap = draw_hexagon(surface, screen_width, screen_height, 500, 500,
                                x_offset=offset, y_offset=20, init_random_count=10, draw_single_color=True)

    # loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                HexMap.handleEvent(event)
            elif event.type == MOUSEMOTION:
                HexMap.handleEvent(event)

        HexMap.draw()

        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()