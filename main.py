'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import time
import multiprocessing as mp

from graphics import GraphWin, Text, Point, Entry, Line
from collision import CollisionSystem 
from particles import Particle, Immovable, RectParticle, Wall, ParticleShape
from menu import MainMenu

# import os
# import sys
# import pdb

def main():
    menu_options = {"New": main_menu.run, "Restart": main, "Exit": window.close}
    window.addMenu(menu_options)
    window.setBackground('white')
    window.clear()

    # globals
    pq = []
    particles = []
    particle_shapes = []

    # create particles from config file
    dataMap = main_menu.getConfigData()
    for key in dataMap['particles']:
        curr = dataMap['particles'][key]
        n = int(curr['n'])
        for i in range(0, n):
            # TODO replace with a factory method that will
            # create the particle and particle shape, keep
            # a reference count, and add them to the appropriate
            # containers in lockstep
            particles.append(Particle(i, window, 
                    radius = float(curr['radius']),
                    color = curr['color'],
                    mass = float(curr['mass']),
                    shape = curr['shape'],
                    width = float(curr['width']),
                    height = float(curr['height'])
            ))
            particle_shapes.append(ParticleShape(i, window, 
                    shape = curr['shape'], 
                    x = particles[i].x, 
                    y = particles[i].y, 
                    radius = float(curr['radius']), 
                    color = curr['color']
            ))

    # initialize multithreading variables
    work_completed_q = mp.Queue()
    work_requested_q = mp.Queue()

    # initialize workers
    num_workers = 4
    workers = []
    for n in range(0, num_workers):
        workers.append(mp.Process(target=CollisionSystem.processWorkRequests, args=(work_requested_q, work_completed_q)))
        workers[n].daemon = True
        workers[n].start()

    # draw all particles
    for particle_shape in particle_shapes:
        particle_shape.draw()
    
    for particle in particles:
        CollisionSystem.predict(particle, 0.0, 10000, particles, work_completed_q)

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    TICKS_PER_SECOND = 120 # how often collisions are checked 
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND # in seconds
    nextLogicTick = TIME_PER_TICK
    lastFrameTime = time.time()

    def pause():
        message = Text(Point(window.width/2.0, window.height/2.0 - 50.0), 'Paused')
        message.setSize(24)
        message.draw(window)
        while window.checkKey() != "space": # pause until user hits space again
            pass
        message.undraw()

    # Main Simulation Loop
    while simTime < limit:
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        lastFrameTime = currentTime

        simTime = simTime + elapsed

        if simTime > nextLogicTick:
            CollisionSystem.processCompletedWork(work_completed_q, pq)
            CollisionSystem.processCollisionEvents(particles, pq, nextLogicTick, work_requested_q, work_completed_q)

            for particle in particles:
                particle.move(TIME_PER_TICK)  # moves each particle in linear line
                # assert(particle.x >= 0 - 100 and particle.x <= window.width + 100)  
                # assert(particle.y >= 0 - 100 and particle.y <= window.height + 100)
            
            nextLogicTick = nextLogicTick + TIME_PER_TICK
           
        else:
            # render updates to window
            for particle_shape in particle_shapes:
                particle_shape.x = particles[particle_shape.index].x
                particle_shape.y = particles[particle_shape.index].y
                particle_shape.render()  

        # check if user wants to end simulation
        if window.checkMouse() is not None:
            pass
            # window.close()

        if window.checkKey() == "space":
            pause()
            lastFrameTime = time.time()
    window.close

if __name__ == '__main__':
    window = GraphWin('Particle Simulation', 1024, 768, autoflush=False)
    main_menu = MainMenu(window, main)
    
    main()