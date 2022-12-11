import pygame
from pygame.locals import *

pygame.init()

screen_width = 800
screen_heigth = 800

screen = pygame.display.set_mode((screen_width, screen_heigth))

done = False

white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)
red = pygame.Color(255, 0, 0)
timesClicked = 0

def plot_line(point1, point2, color):
    x0, y0 = point1
    x1, y1 = point2
    dx = abs(x1 - x0)
    if x0 < x1:
        sx = 1
    else:
        sx = -1
    dy = -abs(y1 - y0)
    if y0 < y1:
        sy = 1
    else:
        sy = -1

    err = dx + dy

    while True:
        screen.set_at((x0, y0), color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy

def drawGrid(surface, width, height, color):
    blockSize = 20 #Set the size of the grid block
    for x in range(0, width, blockSize):
        for y in range(0, height, blockSize):
            rect = pygame.Rect(x, y, blockSize, blockSize)
            pygame.draw.rect(surface, color, rect, 1)

def drawGrid_by_line(surface, width, height, color):
    blockSize = 20 #Set the size of the grid block
    for x in range(0, width, blockSize): # draw vertical lines
        pygame.draw.line(surface, color, (x,0),(x,height))   
    for y in range (0, height, blockSize): # draw horizontal lines
        pygame.draw.line(surface, color, (0,y), (width, y))
    # boundary bold line
    pygame.draw.line(surface, color, (0,0),(0,height),2)
    pygame.draw.line(surface, color, (0,0), (width, 0),2)
    pygame.draw.line(surface, color, (width,0),(width,height),2)
    pygame.draw.line(surface, color, (0,height), (width, height),2)

def drawGrid_by_line2(surface,startX, startY, blockSize, width, height, color):
    shiftWidth = width+startX
    shiftHeight = height+startY
    for x in range(startX, shiftWidth, blockSize): # draw vertical lines
        pygame.draw.line(surface, color, (x,startY),(x,shiftHeight))   
    for y in range (startY, shiftHeight, blockSize): # draw horizontal lines
        pygame.draw.line(surface, color, (startX,y), (shiftWidth, y))
    # boundary bold line
    pygame.draw.line(surface, color, (startX,startY),(startX,shiftHeight),2)
    pygame.draw.line(surface, color, (startX,startY), (shiftWidth, startY),2)
    pygame.draw.line(surface, color, (shiftWidth,startY),(shiftWidth,shiftHeight),2)
    pygame.draw.line(surface, color, (startX,shiftHeight), (shiftWidth, shiftHeight),2)


screen.fill(white)
#drawGrid(screen, 800, 600, black)
drawGrid_by_line(screen, 600, 600, black)
drawGrid_by_line2(screen, 100, 100, 20, 600, 600, red)
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == MOUSEBUTTONDOWN:
            if timesClicked == 0:
                point1 = pygame.mouse.get_pos()
            else:
                point2 = pygame.mouse.get_pos()
            timesClicked += 1
            if timesClicked > 1:
                #plot_line(point1, point2,black)
                pygame.draw.line(screen, green, point1, point2, width=2)
                timesClicked = 0

    pygame.display.update()
pygame.quit()