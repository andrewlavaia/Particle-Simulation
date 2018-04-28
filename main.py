'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''

import random
import time
from graphics import  *
from collision import CollisionSystem 
from particles import Ball

def main():
    win = GraphWin('Particle Simulation', 800, 600)
    win.setBackground('white')

    particles = []

    # Create a list of random balls
    n = 50
    for i in range(0, n):
        ballRadius = 5
        randX = random.uniform(0 + ballRadius, win.width - ballRadius)
        randY = random.uniform(0 + ballRadius, win.height - ballRadius)
        randVX = random.uniform(-100, 100)
        randVY = random.uniform(-100, 100)
        particles.append(Ball(randX, randY, randVX, randVY, ballRadius, win.width, win.height))
    
    # add one larger ball
    randX = random.uniform(0 + ballRadius, win.width - ballRadius)
    randY = random.uniform(0 + ballRadius, win.height - ballRadius)
    particles.append(Ball(randX, randY, randVX, randVY, 50, win.width, win.height))

    # draw all particles
    for particle in particles:
        particle.draw(win)

    # initialize collision system
    cs = CollisionSystem(particles)

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    lastFrameTime = time.time()
    FPS = 120

    # Main Simulation Loop
    while simTime < limit:
        # dt is the time delta in seconds (float)
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        lastFrameTime = currentTime
        
        # force updates to be constant time
        fixedFrameTime = 1.0/FPS
        sleepTime = fixedFrameTime - elapsed
        if sleepTime > 0:
            time.sleep(sleepTime)

        # update time
        simTime = simTime + fixedFrameTime
        
        # update simulation logic
        for particle in particles:
            particle.move(fixedFrameTime)  # moves each particle in linear line   

        # process all events that occurred during last frame
        cs.processEvents(simTime)

        # render updates to window
        for particle in particles:
            particle.render(win)  

        # check if user wants to end simulation
        if win.checkMouse() is not None:
            break
  
    win.close

main()