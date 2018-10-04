'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import time
import multiprocessing as mp

from graphics import GraphWin
from collision import CollisionSystem 
from particles import Particle, Immovable, RectParticle, Wall, ParticleShape, ParticleFactory
from menu import MainMenu

# import os
# import sys
# import pdb

def main():
    menu_options = {"New": main_menu.run, "Restart": main, "Exit": window.close}
    window.addMenu(menu_options)
    window.setBackground('white')
    window.clear()

    # clear work queues
    while not work_requested_q.empty():
        work_requested_q.get_nowait()
    while not work_completed_q.empty():
        work_completed_q.get_nowait()

    # globals
    pq = []
    particles = []
    particle_shapes = []
    pf = ParticleFactory(window, particles, particle_shapes)

    # create particles from config file
    dataMap = main_menu.getConfigData()
    for key in dataMap['particles']:
        curr = dataMap['particles'][key]
        n = curr.pop('n')
        for i in range(0, n):
            pf.create(**curr)

    for particle_shape in particle_shapes:
        particle_shape.draw()
    
    for particle in particles:
        CollisionSystem.predict(particle, 0.0, 10000, particles, work_completed_q)
    while not work_requested_q.empty():
        pass

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    TICKS_PER_SECOND = 120 # how often collisions are checked 
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND # in seconds
    nextLogicTick = TIME_PER_TICK
    lastFrameTime = time.time()

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
            main_menu.pause()
            lastFrameTime = time.time()
    window.close

if __name__ == '__main__':
    window = GraphWin('Particle Simulation', 1024, 768, autoflush=False)
    main_menu = MainMenu(window, main)

    # initialize multi-threading variables
    work_completed_q = mp.Queue()
    work_requested_q = mp.Queue()

    # initialize workers
    num_workers = 4
    workers = []
    for n in range(0, num_workers):
        workers.append(mp.Process(target=CollisionSystem.processWorkRequests, args=(work_requested_q, work_completed_q)))
        workers[n].daemon = True
        workers[n].start()

    main()