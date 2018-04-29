'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''

import time
from graphics import GraphWin
from collision import CollisionSystem 
from particles import Particle

def main():
    window = GraphWin('Particle Simulation', 800, 600)
    window.setBackground('white')

    particles = []

    # Create a list of random balls
    n = 50
    for i in range(0, n):
        particles.append(Particle(window))
    particles.append(Particle(window, radius = 50, color = "blue")) # add one larger ball

    # draw all particles
    for particle in particles:
        particle.draw()

    # initialize collision system
    cs = CollisionSystem(particles)

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    FPS = 120
    lastFrameTime = time.time()

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
            particle.render()  

        # check if user wants to end simulation
        if window.checkMouse() is not None:
            break
  
    window.close

main()