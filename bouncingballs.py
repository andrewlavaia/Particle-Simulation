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

    # Calculates time (in ms) until collision with another Ball
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

    # calculates time (in ms) until collision with horizontal wall
    def timeToHitHWall(self):
        if self.vy > 0:
            return (self.maxHeight - self.radius - self.y) / self.vy
        elif (self.vy < 0):
            return (0.0 + self.radius - self.y) / self.vy
        elif (self.vy == 0):
            return math.inf

    # calculates time (in ms) until collision with vertical wall
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

    # adjusts velocity of object after colliding with vertical wall
    def bounceOffVWall(self):
        self.vx = -1 * self.vx;
        self.collisionCnt = self.collisionCnt + 1

    # adjusts velocity of object after colliding with horizontal wall
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

    # check if event was invalidated from prior collision
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
    FPS = 120          

    def __init__(self, balls):
        self.pq = []                # priority queue    
        self.evtTime = 0.0          # simulation clock time      
        self.balls = list(balls)    # copy of list of balls
        self.lastFrameTime = time.time()


    # Adds all predicted collision times with this object to priority queue
    def predict(self, a, limit):
        if a is None:
            return
        
        # insert predicted collision time with every other 
        # ball into the priority queue
        for b in self.balls:
            dt = a.timeToHit(b)
            evt = Event(self.evtTime + dt, a, b)
            if self.evtTime + dt <= limit:
                heapq.heappush(self.pq, evt)
        
        # insert collision time with every wall into 
        # the priority queue
        dt = a.timeToHitVWall()
        evt = Event(self.evtTime + dt, a, None)
        if self.evtTime + dt <= limit:
            heapq.heappush(self.pq, evt)
        dt = a.timeToHitHWall()
        evt = Event(self.evtTime + dt, None, a)
        if self.evtTime + dt <= limit:   
            heapq.heappush(self.pq, evt) 
        

    # Pre-populates priority queue with all predicted
    # collisions and performs the initial draw call for
    # each object (each object is only drawn once)
    def populatePQ(self, win):
        for ball in self.balls:
            ball.draw(win)
            self.predict(ball, 10000)

    # Processes the events in priority queue until
    # pq is empty or time limit reached    
    def simulate(self, window, limit):
        while self.evtTime < limit:
            # dt is the time delta in seconds (float)
            currentTime = time.time()
            elapsed = currentTime - self.lastFrameTime
            self.lastFrameTime = currentTime
            
            # force updates to be constant
            fixedFrameTime = 1.0/CollisionSystem.FPS
            sleepTime = fixedFrameTime - elapsed
            if sleepTime > 0:
                time.sleep(sleepTime)
            
            # update game logic
            for ball in self.balls:
                ball.move(fixedFrameTime)  # moves each ball in linear line   

            self.evtTime = self.evtTime + fixedFrameTime

            # process all events that occurred last frame
            while len(self.pq) > 0 and self.pq[0].time < self.evtTime:
                # grab top event from priority queue
                evt = heapq.heappop(self.pq)

                # skip event if no longer valid
                if not evt.isValid():
                    continue
                a = evt.a
                b = evt.b

                # process collisions 
                if a is not None and b is not None: 
                    a.bounceOff(b)
                    self.predict(a, 10000)
                    self.predict(b, 10000)
                elif a is not None and b is None:
                    a.bounceOffVWall()
                    self.predict(a, 10000)
                elif a is None and b is not None:
                    b.bounceOffHWall()
                    self.predict(b, 10000)
                elif a is None and b is None:
                    pass

            # draw updates to window
            self.redraw(window)

            # check if user wants to end simulation
            if window.checkMouse() is not None:
                return

    # Update position of all objects on window
    def redraw(self, win):
        for ball in self.balls:
            ball.update(win)  
    
        # used to limit CPU calcs and end program quicker
        #time.sleep(1/10000)

        # push next draw call to pq
        #heapq.heappush(self.pq, Event(self.time + CollisionSystem.drawInterval, None, None))

def main():
    win = GraphWin('Bouncing Balls', 800, 600)
    win.setBackground('white')

    # Create a list of random balls
    balls = []
    n = 50
    for i in range(0, n):
        ballRadius = 10
        randX = random.uniform(0 + ballRadius, win.width - ballRadius)
        randY = random.uniform(0 + ballRadius, win.height - ballRadius)
        randVX = random.uniform(-100, 100)
        randVY = random.uniform(-100, 100)
        balls.append(Ball(randX, randY, randVX, randVY, ballRadius, win.width, win.height))
    
    # add one larger ball
    randX = random.uniform(0 + ballRadius, win.width - ballRadius)
    randY = random.uniform(0 + ballRadius, win.height - ballRadius)
    balls.append(Ball(randX, randY, randVX, randVY, 50, win.width, win.height))
    
    # initialize collision system
    cs = CollisionSystem(balls)
    cs.populatePQ(win)

    # run simulation
    cs.simulate(win, 10000) 
  
    win.close

main()