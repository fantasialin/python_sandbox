import pygame
from pygame.locals import *
import random

pygame.init()

screen_width = 800
screen_heigth = 800

screen = pygame.display.set_mode((screen_width, screen_heigth))

font = pygame.font.SysFont(None, 40)

done = False

white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)
red = pygame.Color(255, 0, 0)
light_gray = pygame.Color(220, 220, 220)
timesClicked = 0

class SudokuBoard:
    def __init__(self, surface, startX, startY, blockSize, color, boldsize):
        self.surface = surface
        self.startX = startX
        self.startY = startY
        self.shiftWidth = (blockSize*9)+startX
        self.shiftHeight = (blockSize*9)+startY
        self.blockSize = blockSize
        self.color = color
        self.boldsize = boldsize
        self.board = {}
        self.text = []
        self.blankBoard()
        for i in range (10):
            self.text.append(font.render(str(i), False, black))


    def blankBoard(self):
        for y in range (9):
            for x in range (9):
                self.board[x,y] = random.randint(0,9)

    def draw(self):
        self.drawBackground()
        self.drawNumbers()
        self.drawGrid()

    def drawGrid(self):
        count = 0
        for x in range(self.startX, self.shiftWidth, self.blockSize): # draw vertical lines
            if count%3 == 0:
                pygame.draw.line(self.surface, self.color, (x,self.startY),(x,self.shiftHeight),self.boldsize)
            else:
                pygame.draw.line(self.surface, self.color, (x,self.startY),(x,self.shiftHeight))
            count += 1
        count = 0
        for y in range (self.startY, self.shiftHeight, self.blockSize): # draw horizontal lines
            if count%3 == 0:
                pygame.draw.line(self.surface, self.color, (self.startX,y), (self.shiftWidth, y),self.boldsize)
            else:
                pygame.draw.line(self.surface, self.color, (self.startX,y), (self.shiftWidth, y))
            count += 1
        
        # boundary bold line
        #pygame.draw.line(self.surface, self.color, (self.startX,self.startY),(self.startX,self.shiftHeight),self.boldsize)
        #pygame.draw.line(self.surface, self.color, (self.startX,self.startY), (self.shiftWidth, self.startY),self.boldsize)
        pygame.draw.line(self.surface, self.color, (self.shiftWidth,self.startY),(self.shiftWidth,self.shiftHeight),self.boldsize)
        pygame.draw.line(self.surface, self.color, (self.startX,self.shiftHeight), (self.shiftWidth, self.shiftHeight),self.boldsize)

    def drawCell(self, cell):
        x = cell[0]
        y = cell[1]
        y = y * self.blockSize # translates array into grid size
        x = x * self.blockSize # translates array into grid size
        
        rect = pygame.Rect(self.startX+x, self.startY+y, self.blockSize, self.blockSize)
        if self.board[cell] == 0:
            #pygame.draw.rect(self.surface, red, rect)
            text_surface = self.text[self.board[cell]]
            self.surface.blit(text_surface,text_surface.get_rect(center=rect.center))
            pass
        else:
            #pygame.draw.rect(self.surface, green, rect)
            text_surface = self.text[self.board[cell]]
            self.surface.blit(text_surface,text_surface.get_rect(center=rect.center))
        
    def drawNumbers(self):
        for cell in self.board:
            self.drawCell(cell)

    def drawBackground(self):
        rect1 = pygame.Rect(self.startX+self.blockSize*3, self.startY, self.blockSize*3, self.blockSize*9)
        rect2 = pygame.Rect(self.startX, self.startY+self.blockSize*3, self.blockSize*9, self.blockSize*3)
        pygame.draw.rect(self.surface, light_gray, rect1)
        pygame.draw.rect(self.surface, light_gray, rect2)


screen.fill(white)

board = SudokuBoard(screen, 100, 100, 40, black,3)
board.draw()

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
                pygame.draw.line(screen, green, point1, point2, width=2)
                timesClicked = 0

    pygame.display.update()
pygame.quit()