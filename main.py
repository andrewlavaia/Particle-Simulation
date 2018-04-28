'''Program: main.py
Particle simulation of different types
of objects colliding with one another
'''

import random
from graphics import  *
from collision import CollisionSystem 
from particles import Ball


def main():
    win = GraphWin('Particle Simulation', 800, 600)
    win.setBackground('white')

    # Create a list of random balls
    balls = []
    n = 50
    for i in range(0, n):
        ballRadius = 5
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