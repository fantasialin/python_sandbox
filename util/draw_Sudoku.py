# ref : https://stackoverflow.com/questions/45471152/how-to-create-a-sudoku-puzzle-in-python
# for Sudoku generation

import pygame
from pygame.locals import *
import random


#Number of frames per second
FPS = 10

pygame.init()

screen_width = 800
screen_heigth = 800

screen = pygame.display.set_mode((screen_width, screen_heigth))

fpsClock = pygame.time.Clock()

font = pygame.font.SysFont(None, 40)

done = False

white = pygame.Color(255, 255, 255)
green = pygame.Color(0, 255, 0)
black = pygame.Color(0, 0, 0)
red = pygame.Color(255, 0, 0)
blue = pygame.Color(0, 0, 255)
orange = pygame.Color(245, 138, 66)
light_gray = pygame.Color(220, 220, 220)
light_blue = pygame.Color(66, 245, 224)
dark_gray = pygame.Color(100, 100, 100)

class numberBoard:
    def __init__(self, surface, startX, startY, blockSize, gap):
        self.surface = surface
        self.startX = startX
        self.startY = startY
        self.shiftWidth = startX+(blockSize*9)+gap*8
        self.shiftHeight = blockSize+startY
        self.blockSize = blockSize
        self.gap = gap
        self.text = []
        self.num = [x for x in range(1,10)]
        #print(self.num)
        for i in self.num:
            self.text.append(font.render(str(i), False, black))
        self.buttons = []
        for i in range(9):
            self.buttons.append(pygame.Rect(self.startX+(i*(self.blockSize+self.gap)), self.startY, self.blockSize, self.blockSize))
    
    def draw(self):
        for i in range (9):
            rect = self.buttons[i]
            pygame.draw.rect(self.surface, light_gray, rect)
            pygame.draw.rect(self.surface, dark_gray, rect, 2)
            text_surface = self.text[i]
            self.surface.blit(text_surface,text_surface.get_rect(center=rect.center))

    def onSelected(self,position):
        #print(">> x, y ", position, " ( ", position[0], " , ", position[1], " )")
        if((position[0] >= self.startX and  position[0] <= self.shiftWidth) 
            and (position[1] >= self.startY and position[1] <= self.shiftHeight)):
            for i in range (9):
                if(True == self.buttons[i].collidepoint(position)):
                    print("press >> ", self.num[i])
                    #need callback to Sudoku board
                    break

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
        self.selected = (9,9)
        self.board = {}
        self.solution = {}
        self.text = []
        self.texthighlight = []
        self.blankBoard()
        self.generateNew()

        for i in range (10):
            self.text.append(font.render(str(i), False, black))

        for i in range (10):
            self.texthighlight.append(font.render(str(i), False, blue))

        self.input = numberBoard(surface, startX, startY+blockSize*9+10, blockSize-10, 10)  # "10" is gap between buttons


    def blankBoard(self):
        for y in range (9):
            for x in range (9):
                self.board[x,y] = 0 #random.randint(0,9)
                self.solution[x,y] = 0

    def draw(self):
        self.drawBackground()
        self.drawHighlightCross()
        self.drawSelected()
        self.drawGrid()
        self.drawNumbers()
        # input pad
        self.input.draw()

    def generateNew(self):
        base  = 3
        side  = base*base
        # pattern for a baseline valid solution
        def pattern(r,c): 
            return (base*(r%base)+r//base+c)%side
        # randomize rows, columns and numbers (of valid base pattern)
        from random import sample
        def shuffle(s): 
            return sample(s,len(s)) 

        rBase = range(base) 
        rows  = [ g*base + r for g in shuffle(rBase) for r in shuffle(rBase) ] 
        cols  = [ g*base + c for g in shuffle(rBase) for c in shuffle(rBase) ]
        nums  = shuffle(range(1,base*base+1))

        # produce board using randomized baseline pattern
        board = [ [nums[pattern(r,c)] for c in cols] for r in rows ]

        # set as solution self.solution[x,y]
        y = 0
        for line in board:
            for x in range(9):
                self.solution[x,y] = line[x]
            y += 1

        #for line in board: print(line)

        squares = side*side
        empties = squares * 3//4
        for p in sample(range(squares),empties):
            board[p//side][p%side] = 0

        #numSize = len(str(side))
        #for line in board:
        #    print(*(f"{n or '.':{numSize}} " for n in line))
        #for line in board: print(line)

        y = 0
        for line in board:
            for x in range(9):
                self.board[(x,y)] = line[x]
            y += 1

        # further to make sure only one solution

    def drawSelected(self):
        if(self.selected[0]>=0 and self.selected[0]<9) and (self.selected[1]>=0 and self.selected[1]<9):
            #print("selected>>", self.selected)
            if(self.board[self.selected] == 0): # only value is 0 can be select for input
                x = self.selected[0] * self.blockSize # translates array into grid size
                y = self.selected[1] * self.blockSize # translates array into grid size
                rect = pygame.Rect(self.startX+x, self.startY+y, self.blockSize, self.blockSize)
                pygame.draw.rect(self.surface, orange, rect, 5)

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
            #text_surface = self.text[self.board[cell]]
            #self.surface.blit(text_surface,text_surface.get_rect(center=rect.center))
            pass
        else:
            #pygame.draw.rect(self.surface, green, rect)
            text_surface = None
            if(self.selected[0]>=0 and self.selected[0]<9) and (self.selected[1]>=0 and self.selected[1]<9):
                if self.board[cell] == self.board[self.selected]:
                    text_surface = self.texthighlight[self.board[cell]]
                else:
                    text_surface = self.text[self.board[cell]]
            else:
                text_surface = self.text[self.board[cell]]
            self.surface.blit(text_surface,text_surface.get_rect(center=rect.center))
        
    def drawNumbers(self):
        for cell in self.board:
            self.drawCell(cell)

    def drawBackground(self):
        rect0 = pygame.Rect(self.startX, self.startY, self.blockSize*9, self.blockSize*9)
        rect1 = pygame.Rect(self.startX+self.blockSize*3, self.startY, self.blockSize*3, self.blockSize*9)
        rect2 = pygame.Rect(self.startX, self.startY+self.blockSize*3, self.blockSize*9, self.blockSize*3)
        pygame.draw.rect(self.surface, white, rect0) # entire board
        pygame.draw.rect(self.surface, light_gray, rect1) # vertical of cross
        pygame.draw.rect(self.surface, light_gray, rect2) # horizontal of cross

    def drawHighlightCross(self):
        if(self.selected[0]>=0 and self.selected[0]<9) and (self.selected[1]>=0 and self.selected[1]<9):
            #print("highlight cross >>", self.selected)
            rect1 = pygame.Rect(self.startX+self.blockSize*self.selected[0], self.startY, self.blockSize, self.blockSize*9)
            rect2 = pygame.Rect(self.startX, self.startY+self.blockSize*self.selected[1], self.blockSize*9, self.blockSize)
            pygame.draw.rect(self.surface, light_blue, rect1) # vertical of cross
            pygame.draw.rect(self.surface, light_blue, rect2) # horizontal of cross

    def onSelect(self, position):
        #print(">> x, y ", position, " ( ", position[0], " , ", position[1], " )")
        #check in board range
        if((position[0] >= self.startX and  position[0] <= self.shiftWidth) 
            and (position[1] >= self.startY and position[1] <= self.shiftHeight)):
            selected = (position[0]-self.startX) // self.blockSize, (position[1]-self.startY) // self.blockSize
            #print("on board range", selected)
            self.selected = selected
            #print("on board range", self.selected)
        else:
            # check input pad
            self.input.onSelected(position)


screen.fill(white)

board = SudokuBoard(screen, 100, 100, 40, black,3)
board.draw()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == MOUSEBUTTONDOWN:
            board.onSelect(pygame.mouse.get_pos())
    board.draw()
    pygame.display.update()
    fpsClock.tick(FPS)

pygame.quit()