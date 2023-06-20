#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import pygame, sys
from pygame.locals import *
import random
import math
import heapq
import itertools
import re


#Number of frames per second
FPS = 10

screen_width = 600
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

# reference 
# https://github.com/jansonh/Voronoi.git
# http://www.cs.hmc.edu/~mbrubeck/voronoi.html (C++).

class Point:
    x = 0.0
    y = 0.0
   
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get(self):
        return (self.x, self.y)
  

class Event:
    x = 0.0
    y = 0.0 # dummy
    p = None
    a = None
    valid = True
    
    def __init__(self, x, p, a):
        self.x = x
        self.p = p
        self.a = a
        self.valid = True

class Arc:
    p = None
    pprev = None
    pnext = None
    e = None
    s0 = None
    s1 = None
    
    def __init__(self, p, a=None, b=None):
        self.p = p
        self.pprev = a
        self.pnext = b
        self.e = None
        self.s0 = None
        self.s1 = None

class Segment:
    start = None
    end = None
    done = False
    
    def __init__(self, p, color = BLACK):
        self.start = p
        self.end = None
        self.done = False
        self.color = color

    def finish(self, p):
        if self.done: return
        self.end = p
        self.done = True  

    def get(self):
        if self.start != None and self.end != None:
            return [self.start.get(), self.end.get()]
        elif self.start != None and self.end == None:
            return [self.start.get(), None]
        elif self.start == None and self.end != None:
            return [None, self.end.get()]
        else:
            return None

class PriorityQueue:
    def __init__(self):
        self.pq = []
        self.entry_finder = {}
        self.counter = itertools.count()

    def push(self, item):
        # check for duplicate
        if item in self.entry_finder: return
        count = next(self.counter)
        # use x-coordinate as a primary key (heapq in python is min-heap)
        entry = [(item.x,item.y), count, item]
        self.entry_finder[item] = entry
        heapq.heappush(self.pq, entry)

    def remove_entry(self, item):
        entry = self.entry_finder.pop(item)
        entry[-1] = 'Removed'

    def pop(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')

    def top(self):
        while self.pq:
            priority, count, item = heapq.heappop(self.pq)
            if item != 'Removed':
                del self.entry_finder[item]
                self.push(item)
                return item
        raise KeyError('top from an empty priority queue')

    def empty(self):
        return len(self.pq) == 0

class Voronoi:
    def __init__(self, points):
        self.output = [] # list of line segment
        self.arc = None  # binary tree for parabola arcs

        self.points = PriorityQueue() # site events
        self.event = PriorityQueue() # circle events

        # bounding box
        self.X0 = -50.0
        self.X1 = -50.0
        self.Y0 = 550.0
        self.Y1 = 550.0

        # insert points to site event
        for pts in points:
            point = Point(pts[0], pts[1])
            self.points.push(point)
            # keep track of bounding box size
            if point.x < self.X0: self.X0 = point.x
            if point.y < self.Y0: self.Y0 = point.y
            if point.x > self.X1: self.X1 = point.x
            if point.y > self.Y1: self.Y1 = point.y

        # add 20% margins to the bounding box
        dx = (self.X1 - self.X0 + 1.0) / 5.0
        dy = (self.Y1 - self.Y0 + 1.0) / 5.0
        self.X0 -= dx
        self.X1 += dx
        self.Y0 -= dy
        self.Y1 += dy

    # Process the queues; select the top element with smaller x coordinate.
    def process(self):
        while not self.points.empty():
            if not self.event.empty() and (self.event.top().x <= self.points.top().x):
                self.process_event() # handle circle event
            else:
                self.process_point() # handle site event

        # after all points, process remaining circle events
        while not self.event.empty():
            self.process_event()

        self.finish_edges()

    def process_point(self):
        # get next event from site pq
        p = self.points.pop()
        # add new arc (parabola) to the parabolic front
        self.front_insert(p)

    def process_event(self):
        # get next event from circle pq
        e = self.event.pop()

        if e.valid:
            # start new edge
            s = Segment(e.p, RED)
            self.output.append(s)

            # remove associated arc (parabola) from the front
            a = e.a
            if a.pprev != None:
                a.pprev.pnext = a.pnext
                a.pprev.s1 = s
            if a.pnext != None:
                a.pnext.pprev = a.pprev
                a.pnext.s0 = s

            # finish the edges before and after a
            if a.s0 != None: 
                a.s0.finish(e.p)
            if a.s1 != None: 
                a.s1.finish(e.p)

            # recheck circle events on either side of p
            if a.pprev != None: 
                self.check_circle_event(a.pprev, e.x)
            if a.pnext != None: 
                self.check_circle_event(a.pnext, e.x)

    def front_insert(self, p):
        if self.arc == None:
            self.arc = Arc(p)
            return
        
        # find the current arc(s) at height p.y (if there are any).
        i = self.arc # root
        while i != None:
            flag1, z = self.intersect(p, i)
            if flag1:
                # New parabola intersects arc i. If necessary, duplicate i.
                if i.pnext == None:
                    i.pnext = Arc(i.p, i)
                else:
                    flag2, zz = self.intersect(p, i.pnext)
                    if (not flag2):
                        i.pnext.pprev = Arc(i.p, i, i.pnext)
                        i.pnext = i.pnext.pprev
                    else:
                        i.pnext = Arc(i.p, i)
                i.pnext.s1 = i.s1

                # add p between i and i.pnext
                i.pnext.pprev = Arc(p, i, i.pnext)
                i.pnext = i.pnext.pprev

                i = i.pnext # now i points to the new arc

                # add new half-edges connected to i's endpoints
                seg = Segment(z, BLUE)
                self.output.append(seg)
                i.s0 = seg
                i.pprev.s1 = i.s0

                seg = Segment(z, GREEN)
                self.output.append(seg)
                i.s1 = seg
                i.pnext.s0 = i.s1

                # check for new circle events around the new arc
                self.check_circle_event(i, p.x)
                self.check_circle_event(i.pprev, p.x)
                self.check_circle_event(i.pnext, p.x)

                return
                    
            i = i.pnext

        # special case: If p never intersects an arc, append it to the list
        i = self.arc # root
        while i.pnext != None: # Fine the last node.
            i = i.pnext
        
        i.pnext = Arc(p, i)
        # insert new segment between p and i
        x = self.X0
        y = (i.pnext.p.y + i.p.y) / 2.0
        start = Point(x, y)

        seg = Segment(start, BLACK) # BUG
        i.s1 = i.pnext.s0 = seg
        self.output.append(seg)

    # Look for a new circle event for arc i
    def check_circle_event(self, i, x0_):
        # Invalidate any old event.
        if (i.e != None) and (i.e.x  != x0_):
            i.e.valid = False
        i.e = None

        if (i.pprev == None) or (i.pnext == None): return

        flag, x, o = self.circle(i.pprev.p, i.p, i.pnext.p)
        if flag and (x > x0_):
            # Create new event
            i.e = Event(x, o, i)
            self.event.push(i.e)

    def circle(self, a, b, c):
        # check if bc is a "right turn" from ab
        if ((b.x - a.x)*(c.y - a.y) - (c.x - a.x)*(b.y - a.y)) > 0: return False, None, None

        # Joseph O'Rourke, Computational Geometry in C (2nd ed.) p.189
        A = b.x - a.x
        B = b.y - a.y
        C = c.x - a.x
        D = c.y - a.y
        E = A*(a.x + b.x) + B*(a.y + b.y)
        F = C*(a.x + c.x) + D*(a.y + c.y)
        G = 2.0*(A*(c.y - b.y) - B*(c.x - b.x))

        if (G == 0): return False, None, None # Points are co-linear

        # point o is the center of the circle
        ox = (1.0 * (D*E - B*F)) / G
        oy = (1.0 * (A*F - C*E)) / G

        # o.x plus radius equals max x coord
        x_ = ox + math.sqrt((a.x-ox)**2 + (a.y-oy)**2)
        o_ = Point(ox, oy)
           
        return True, x_, o_
        
    # Will a new parabola at point p intersect with arc i ?
    def intersect(self, p, i):
        #if (i == None): return False, None
        if (i.p.x == p.x): return False, None

        a = 0.0
        b = 0.0

        if i.pprev != None: # Get the intersection of i.pprev, i.
            a = (self.intersection(i.pprev.p, i.p, 1.0*p.x)).y
        if i.pnext != None: # Get the intersection of i.pnext, i.
            b = (self.intersection(i.p, i.pnext.p, 1.0*p.x)).y

        if (((i.pprev == None) or (a <= p.y)) and ((i.pnext == None) or (p.y <= b))):
            py = p.y
            px = 1.0 * ((i.p.x)**2 + (i.p.y-py)**2 - p.x**2) / (2*i.p.x - 2*p.x)
            res = Point(px, py)
            return True, res
        return False, None

    # Where do two parabolas intersect?
    def intersection(self, p0, p1, l_):
        
        p = p0
        if (p0.x == p1.x):
            py = (p0.y + p1.y) / 2.0
        elif (p1.x == l_):
            py = p1.y
        elif (p0.x == l_):
            py = p0.y
            p = p1
        else:
            # use quadratic formula
            z0 = 2.0 * (p0.x - l_)
            z1 = 2.0 * (p1.x - l_)

            a = 1.0/z0 - 1.0/z1
            b = -2.0 * (p0.y/z0 - p1.y/z1)
            c = (1.0 * (p0.y**2 + p0.x**2 - l_**2) / z0) - (1.0 * (p1.y**2 + p1.x**2 - l_**2) / z1)

            py = 1.0 * ((-b - math.sqrt(b*b - 4.0*a*c)) / (2.0*a))
            
        # Plug back into one of the parabola equations.
        px = 1.0 * (p.x**2 + (p.y-py)**2 - l_**2) / (2*p.x-2*l_)
        res = Point(px, py)
        return res

    def finish_edges(self):
        # Advance the sweep line so no parabolas can cross the bounding box
        l = self.X1 + (self.X1 - self.X0) + (self.Y1 - self.Y0)

        # Extend each remaing segment to the new parabola intersections.
        i = self.arc # root
        while i.pnext != None:
            if i.s1 != None:
                p = self.intersection(i.p, i.pnext.p, l*2.0)
                # setting end point
                i.s1.finish(p)
            i = i.pnext

    def print_output(self):
        for o in self.output:
            p0 = o.start
            p1 = o.end
            if p0 != None and p1 != None:
                print (p0.x, p0.y, p1.x, p1.y)

    def get_output(self):
        res = []
        for o in self.output:
            p0 = o.start
            p1 = o.end
            if p0 != None and p1 != None:
                res.append((p0.x, p0.y, p1.x, p1.y, o.color))
        return res

class funcBottons:
    def __init__(self, owner, surface, position=(0,0), width=100, height=40, **kwargs):
        self.surface = surface
        self.startX = position[0]
        self.startY = position[1]
        self.Width = width
        self.Height = height
        self.owner = owner
        self.visible = True
        self.isEnabled = True
        self.items = []
        self.dict = {}
        self.font = pygame.font.SysFont(None, 30)

    def draw(self):
        for a in self.items:
            pygame.draw.rect(self.surface, light_gray, a[1])
            pygame.draw.rect(self.surface, dark_gray, a[1], 2)
            text_surface = a[0]
            self.surface.blit(text_surface,text_surface.get_rect(center=a[1].center))

    def addButton(self, text_, callback):
        idx = len(self.items)
        text = self.font.render(text_, True, BLACK)
        rect = pygame.Rect(self.startX + (idx*(self.Width + 20)), self.startY, self.Width, self.Height)
        item = (text, rect, callback) # 0 -> text, 1 -> rect, 2 -> callback
        self.dict[text_] = item
        self.items.append(item)
    
    def handleEvent(self, Event):
        if Event.type not in (MOUSEMOTION, MOUSEBUTTONUP, MOUSEBUTTONDOWN) or not self.visible:
            return False
        #print("pos>> ",self.text, " >> ",Event.pos)
        if self.visible and self.isEnabled:
            for item in self.items:
                if item[1].collidepoint(Event.pos):
                    item[2]() # callback

class fortune_sweep:
    def __init__(self, surface, width, height, voi_width, voi_height, **kwargs):
        self.surface = surface
        self.width = width
        self.height = height
        self.voi_width = voi_width
        self.voi_height = voi_height
        self.visible = True
        self.isEnabled = True
        self.isPause = False
        self.x_offset = kwargs.get('x_offset', 0)
        self.y_offset = kwargs.get('y_offset', 0)
        self.init_random_count = kwargs.get('init_random_count', 100)
        self.output_points_log = kwargs.get('output_points_log', False)
        self.draw_single_color = kwargs.get('draw_single_color', False)
        self.win_area = pygame.Rect(0, 0, voi_width, voi_height)
        self.draw_area = pygame.Rect(self.x_offset, self.y_offset, voi_width+self.x_offset, voi_height+self.y_offset)
        self.image = pygame.Surface((voi_width, voi_height))
        #self.image.fill(WHITE)
        self.child = funcBottons(self, surface, (10, self.voi_height + self.y_offset + 10), 120, 40)
        self.child.addButton("reset", self.reset)
        self.child.addButton("pause", self.pause)
        self.child.addButton("unpause", self.unpause)
        #self.child.addButton("save", self.output_points)
        #self.child.addButton("verify", self.debug_points)
        #self.child.addButton("show", self.debug_draw)
        self.points = []
        self.add_random_points(self.init_random_count)
        if self.output_points_log:
            for x in self.points:
                print(f'{x[0]} {x[1]}')
            print("-1")
        self.outfile = open("voronoi_random_point.txt", "w")

    # destructor
    def __del__(self):
        self.outfile.flush()
        self.outfile.close()    

    def add_random_points(self, count):
        if self.isPause:
            return # just skip
        x = list()
        y = list()
        for i in range(count):
            x.append(random.randint(0,self.voi_width))
            y.append(random.randint(0,self.voi_height))
        count_min = min(len(x), len(y))
        for i in range(count_min):
            if (x[i], y[i]) not in self.points:
                self.points.append((x[i], y[i]))
            else:
                print(f'duplicated!!')

    def calculate_voronoi(self):
        if self.isPause:
            return # just skip
        # create voronoi instance
        voronoi_ = Voronoi(self.points)
        # generate voronoi diagram according to input points
        voronoi_.process()
        # get the lines of voronoi diagram
        lines = voronoi_.get_output()
        self.drawEdge(lines)

    def reset(self):
        self.points = []
        self.isPause = False

    def pause(self):
        self.isPause = True

    def unpause(self):
        self.isPause = False

    def debug_points(self):
        self.points = []
        self.isPause = True
        with open("voronoi_random_point_debug.txt", "r+") as f:
            for line in f:
                point = re.findall(r'\d+', line)
                #print(f'{point[0]} {point[1]}')
                if len(point) == 2:
                    self.points.append((int(point[0]), int(point[1])))
        if len(self.points) > 1:
            self.isPause = False
            print(f'>>>>>>>>>>>>>>>>> DEBUG STRT >>>>>>>>>>>>>>')
            self.calculate_voronoi()
            print(f'>>>>>>>>>>>>>>>>> DEBUG END >>>>>>>>>>>>>>')
            self.isPause = True

    def debug_draw(self):
        self.isPause = True
        debug_line = []
        with open("./_sandbox/result.txt", "r+") as f:
            for line in f:
                point = re.findall(r'[-+]?(?:\d*\.*\d+)', line)
                if len(point) == 4:
                    r = random.randrange(256)
                    g = random.randrange(256)
                    b =random.randrange(256)
                    print(f'{point[0]} {point[1]} {point[2]} {point[3]}')
                    #debug_line.append((float(point[0]), float(point[1]), float(point[2]),float(point[3]), BLACK))
                    debug_line.append((float(point[0]), float(point[1]), float(point[2]),float(point[3]), (r,g,b)))
        if len(debug_line) > 1:
            self.drawEdge(debug_line)

    def get_points_count(self):
        return len(self.points)
    
    def output_points(self):
        for x in self.points:
            data = f'{x[0]} {x[1]}\n'
            self.outfile.write(data)
        self.outfile.flush()
        

    def drawEdge(self, lines):
        # clean off screen surface
        self.image.fill((240,240,240))
        # draw lines to off screen surface
        for a in lines:
            if self.draw_single_color:
                pygame.draw.line(self.image, BLACK, (a[0],a[1]), (a[2], a[3]))
            else:
                pygame.draw.aaline(self.image, a[4], (a[0],a[1]), (a[2], a[3]))
        # draw points
        for a in self.points:
            pygame.draw.circle(self.image, RED, (a[0], a[1]), 2)
        # draw off screen surface frame
        pygame.draw.rect(self.image, dark_gray, self.win_area, 1)
        # copy to diaply surface
        self.surface.blit(self.image, self.draw_area)

    def draw(self):
        # draw self
        self.child.draw()

    def handleEvent(self,Event):
        if self.visible and self.isEnabled:
            #if Event.type == MOUSEBUTTONDOWN:
            self.child.handleEvent(Event)


def main():
    pygame.init()
    pygame.display.set_caption('Fortune\'s algorithm - plane sweep') 
    surface = pygame.display.set_mode((screen_width,screen_height)) 
    surface.fill(WHITE)
    fpsClock = pygame.time.Clock()
    offset = (screen_width - 500)/2
    fortune = fortune_sweep(surface, screen_width, screen_height, 500, 500,
                                x_offset=offset, y_offset=20, init_random_count=10, draw_single_color=True)
    fortune.calculate_voronoi()

    max_count = 100
    total_count = 10
    steps = 2

    # loop
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                fortune.handleEvent(event)

        total_count = fortune.get_points_count()

        if total_count < max_count:
            fortune.add_random_points(steps)
            # draw again
            fortune.calculate_voronoi()

        fortune.draw()

        pygame.display.update()
        fpsClock.tick(FPS)

if __name__ == '__main__':
    main()