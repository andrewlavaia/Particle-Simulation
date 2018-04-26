'''Program: bouncingballs.py
Provides simple event simulation using a
priority queue to check for collisions
'''

import random
import math
from graphics import  *

class Ball:
    x, y = 0, 0         # position
    vx, vy = 0, 0       # velocity
    radius = 1
    mass = 1
    maxWidth = 1
    maxHeight = 1
    collisionCnt = 0   

    def __init__(self, x, y, vx, vy, r, windowWidth, windowHeight):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.radius = r
        self.maxWidth = windowWidth
        self.maxHeight = windowHeight

    def move(self, dt):
        # if collision with wall, reverse speed 
        if self.x + (self.vx * dt) < self.radius or self.x + (self.vx * dt) > self.maxWidth - self.radius:
            self.vx = -self.vx;
        if self.y + (self.vy * dt) < self.radius or self.y + (self.vy * dt) > self.maxHeight - self.radius:
            self.vy = -self.vy;

        # move ball by speed * delta time   
        self.x = self.x + (self.vx * dt)
        self.y = self.y + (self.vy * dt)

    def timeToHit(that):
        if self == that:
            return math.inf 
        # distance
        dx = that.x - self.x
        dy = that.y - self.y;
        
        # speed
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        
        # collision prediction
        # d = (Δv*Δr)^2 − (Δv*Δv)(Δr*Δr − σ^2)
        dvdr = dx*dvx + dy*dvy;
        if dvdr > 0: 
            return math.inf
        dvdv = dvx*dvx + dvy*dvy;
        drdr = dx*dx + dy*dy;
        sigma = self.radius + that.radius;
        d = (dvdr*dvdr) - dvdv * (drdr - sigma*sigma);
        if d < 0:
            return math.inf;
        return -(dvdr + math.sqrt(d)) / dvdv;

    def bounceOff(that):
        dx = that.x - self.x
        dy = that.y - self.y;
        dvx = that.vx - self.vx 
        dvy = that.vy - self.vy
        dvdr = dx*dvx + dy*dvy
        dist = self.radius + that.radius
        J = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)
        Jx = J * dx / dist
        Jy = J * dy / dist
        self.vx += Jx / self.mass
        self.vy += Jy / self.mass
        that.vx -= Jx / that.mass
        that.vy -= Jy / that.mass
        self.collisionCnt = self.collisionCnt + 1
        that.collisionCnt = that.collisionCnt + 1

def main():
    win = GraphWin('Bouncing Balls', 500, 500)
    win.setBackground('white')

    # Create a list of random balls
    balls = []
    n = 50
    for i in range(1, n):
        ballRadius = 5
        randX = random.uniform(0 + ballRadius, win.width - ballRadius)
        randY = random.uniform(0 + ballRadius, win.height - ballRadius)
        randVX = random.uniform(-1, 1)
        randVY = random.uniform(-1, 1)
        balls.append(Ball(randX, randY, randVX, randVY, ballRadius, win.width, win.height))
    
    # Create a list of Circles
    circles = []
    for ball in balls:
        c = Circle(Point(ball.x, ball.y), ball.radius)
        circles.append(c)
        c.draw(win)
 

    # Simulation Loop
    while win.checkMouse() == None:
        i = 0
        for ball in balls:
            ball.move(1)
            circles[i].move(ball.x - circles[i].getCenter().getX(), ball.y - circles[i].getCenter().getY())
            i = i + 1
    
    win.close
    
main()