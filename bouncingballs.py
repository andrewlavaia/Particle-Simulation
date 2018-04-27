'''Program: bouncingballs.py
Provides simple event simulation using a
priority queue to check for collisions
'''

import random
import math
import heapq
import time
from graphics import  *
from datetime import datetime

# Defines a Ball object which can be used in the Collision Simulator
class Ball:
    def __init__(self, x, y, vx, vy, r, windowWidth, windowHeight):
        self.x = x                          # position
        self.y = y                         
        self.vx = vx                        # velocity  
        self.vy = vy
        self.radius = r                     # size of Ball in pixels
        self.circle = Circle(Point(x, y), r)
        self.mass = 1                       # used for collision physics
        self.maxWidth = windowWidth         # highest possible x position
        self.maxHeight = windowHeight       # highest possible y position
        self.collisionCnt = 0               # number of pending collisions
 
    def __eq__(self, other):
        return ((self.x, self.y, self.circle) ==
                (other.x, other.y, other.circle))

    # Moves ball by time * speed
    def move(self, dt):   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    # Draws the Circle to a window
    def draw(self, window):
        self.circle.draw(window)
    
    # Moves Circle to current position on window 
    def update(self, window):    
        self.circle.move(self.x - self.circle.getCenter().getX(), self.y - self.circle.getCenter().getY())

    # Calculates time until collision with another Ball
    def timeToHit(self, that):
        if self == that:
            return math.inf 

        # distance
        dx = that.x - self.x
        dy = that.y - self.y
        
        # speed
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        
        # collision prediction
        # d = (Δv*Δr)^2 − (Δv*Δv)(Δr*Δr − σ^2)
        dvdr = dx*dvx + dy*dvy
        if dvdr > 0: 
            return math.inf
        dvdv = dvx*dvx + dvy*dvy
        drdr = dx*dx + dy*dy
        sigma = self.radius + that.radius
        
        d = (dvdr*dvdr) - (dvdv * (drdr - sigma*sigma))
        if d <= 0: 
            return math.inf

        return -1 * (dvdr + math.sqrt(d)) / dvdv

    def timeToHitHWall(self):
        if self.vy > 0:
            return (self.maxHeight - self.radius - self.y) / self.vy
        elif (self.vy < 0):
            return (0.0 + self.radius - self.y) / self.vy
        elif (self.vy == 0):
            return math.inf

    def timeToHitVWall(self):
        if (self.vx > 0):
            return (self.maxWidth - self.radius - self.x) / self.vx
        elif (self.vx < 0):
            return (0.0 + self.radius - self.x) / self.vx
        elif (self.vx == 0):
            return math.inf


    # adjusts velocity vectors of two objects after a collision
    def bounceOff(self, that):
        dx = that.x - self.x
        dy = that.y - self.y
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy

        # dot product
        dvdr = dx*dvx + dy*dvy


        dist = self.radius + that.radius

        # calculate magnitude of force
        # J = 2 * mass[i] * mass[j] (Δv * Δr) / σ(mass[i] + mass[j])
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        fx = J * dx / dist
        fy = J * dy / dist
        self.vx = self.vx + (fx / self.mass)
        self.vy = self.vy + (fy / self.mass)
        that.vx = self.vx - (fx / that.mass)
        that.vy = self.vy - (fy / that.mass)

        # increase collision count
        self.collisionCnt = self.collisionCnt + 1
        that.collisionCnt = that.collisionCnt + 1

    def bounceOffVWall(self):
        self.vx = -1 * self.vx;
        self.collisionCnt = self.collisionCnt + 1

    def bounceOffHWall(self):
        self.vy = -1 * self.vy; 
        self.collisionCnt = self.collisionCnt + 1


# Defines an Event that will occur at time t between objects a and b
# if neither a & b are None -> collision with another object
# if one of a or b is None -> collision with wall
# if both a & b are None -> do nothing
class Event:
    def __init__(self, t, a, b):
        self.time = t    
        self.a = a
        self.b = b
        if a is not None:
            self.countA = a.collisionCnt
        else:
            self.countA = -1

        if b is not None:
            self.countB = b.collisionCnt
        else:
            self.countB = -1
    
    # comparator
    def __lt__(self, that):
        return self.time <= that.time

    def isValid(self):
        if (self.a is not None and self.countA != self.a.collisionCnt):
            return False
        if (self.b is not None and self.countB != self.b.collisionCnt):
            return False
        return True

# Collision System used to predict when two objects will
# colide and store those events in a min priority queue.
# Also used to run simulation.
class CollisionSystem:
    drawInterval = 1000/120         # in ms
    
    def __init__(self, balls):
        self.pq = []                # priority queue    
        self.time = 0.0             # simulation clock time      
        self.balls = list(balls)    # copy of list of balls


    # Adds all predicted collision times with this object to priority queue
    def predict(self, a, limit):
        if a is None:
            return
        
        # insert collision time with all other balls into priority queue
        for b in self.balls:
            dt = a.timeToHit(b)
            evt = Event(self.time + dt, a, b)
            if self.time + dt <= limit:
                heapq.heappush(self.pq, evt)
        
        # insert collision time to hit walls into priority queue
        dt = a.timeToHitVWall()
        evt = Event(self.time + dt, a, None)
        if self.time + dt <= limit:
            heapq.heappush(self.pq, evt)

        dt = a.timeToHitHWall()
        evt = Event(self.time + dt, None, a)
        if self.time + dt <= limit:   
            heapq.heappush(self.pq, evt) 
        

    # Initial draw and inserts initial predicted collision 
    # times into priority queue
    def populatePQ(self, win):
        for ball in self.balls:
            ball.draw(win)
            self.predict(ball, 10000)
        heapq.heappush(self.pq, Event(0, None, None)) # needed for first draw call

    # Processes the events in priority queue until
    # pq is empty or time limit reached    
    def simulate(self, window, limit):
        while len(self.pq) > 0 and self.time < limit:
            # grab top event from priority queue
            evt = heapq.heappop(self.pq)

            # skip event if no longer valid
            if not evt.isValid():
                continue
            a = evt.a
            b = evt.b
            
            # move all balls in linear line 
            for ball in self.balls:
                ball.move(evt.time - self.time)

            '''
            # draw while we wait for time to catch up to event
            while evt.time > self.time:
                time.sleep(1/10000)
                self.redraw(window) 
                self.time = self.time + 5
            '''

            self.time = evt.time 

            # process collisions that will occur 
            # before next draw call
            if a is not None and b is not None: 
                a.bounceOff(b)
                self.predict(a, limit)
                self.predict(b, limit)
            elif a is not None and b is None:
                a.bounceOffVWall()
                self.predict(a, limit)
            elif a is None and b is not None:
                b.bounceOffHWall()
                self.predict(b, limit)
            
            # process draw call
            elif a is None and b is None:
                self.redraw(window)

    # Update position of all circles and push next draw event to pq
    def redraw(self, win):
        # update position of circle objects
        for ball in self.balls:
            ball.update(win)  
    
        # used to limit CPU calcs and end program quicker
        time.sleep(1/10000)

        # push next draw call to pq
        heapq.heappush(self.pq, Event(self.time + CollisionSystem.drawInterval, None, None))

def main():
    win = GraphWin('Bouncing Balls', 800, 600)
    win.setBackground('white')

    # Create a list of random balls
    balls = []
    n = 100
    for i in range(0, n):
        ballRadius = 10
        randX = random.uniform(0 + ballRadius, win.width - ballRadius)
        randY = random.uniform(0 + ballRadius, win.height - ballRadius)
        randVX = random.uniform(-.1, .1)
        randVY = random.uniform(-.1, .1)
        balls.append(Ball(randX, randY, randVX, randVY, ballRadius, win.width, win.height))
 
    balls.append(Ball(randX, randY, randVX, randVY, 50, win.width, win.height))
    cs = CollisionSystem(balls)
    cs.populatePQ(win)
    cs.simulate(win, 100000) 
    
    '''
    # TESTS
    b1 = Ball(1, 1, 1, 1, 5, 350, 350)
    b2 = b1
    b3 = Ball(200, 200, 1, 1, 5, 350, 350)
    e1 = Event(100, b1, b3)
    e2 = Event(200, b1, b3)
    e3 = Event(200, b1, b2)
    print(e3.isValid())
    print(Event(99999, b1, b2).isValid())
    assert 5 == 2 # check if assert is working
    assert e1 < e2
    assert e2 > e1
    assert e2 < e1 
    
    '''
    while win.checkMouse() is None:
        pass
    
    win.close

main()