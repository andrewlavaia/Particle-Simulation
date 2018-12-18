'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import time
import sys
import multiprocessing as mp

from graphics import GraphWin, Point, Line
from collision import CollisionSystem 
from particles import Particle, ParticleShape, ParticleFactory
from walls import *
from menu import MainMenu

# import os
# import pdb

def main():
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
    walls = []

    menu_height = 20.0
    walls.append(VWall(0.0))
    walls.append(VWall(window.width - 1))
    walls.append(HWall(0.0))
    walls.append(HWall(window.height - menu_height - 1))

    # create particles and walls from config file
    dataMap = main_menu.getConfigData()
    for key in dataMap['particles']:
        curr = dataMap['particles'][key]
        n = curr.pop('n')
        for i in range(0, n):
            pf.create(**curr)

    for key in dataMap.get('walls', {}):
        curr = dataMap['walls'][key]
        line = LineSegment(Point(curr['p0x'], curr['p0y']), Point(curr['p1x'], curr['p1y']))
        walls.append(line)

    # draw particles and walls
    for particle_shape in particle_shapes:
        particle_shape.draw()

    for wall in walls:
        if wall.wall_type == "VWall":
            ln = Line(Point(wall.x, 0), Point(wall.x, window.height))
        elif wall.wall_type == "HWall":
            ln = Line(Point(0, wall.y), Point(window.width, wall.y))
        else:
            ln = Line(wall.p0, wall.p1)   
        ln.draw(window)

    for particle in particles:
        CollisionSystem.predict(particle, 0.0, 10000, particles, walls, work_completed_q)
    while not work_requested_q.empty():
        pass

    # initialize simulation variables
    simTime = 0.0
    limit = 10000
    TICKS_PER_SECOND = 120 # how often collisions are checked 
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND # in seconds
    nextLogicTick = TIME_PER_TICK
    lastFrameTime = time.time()
    lag = 0.0

    # Main Simulation Loop
    while simTime < limit:
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        lastFrameTime = currentTime
        lag += elapsed
        simTime += elapsed

        if window.checkKey() == "space":
            main_menu.pause()
            lastFrameTime = time.time()

        while lag > TIME_PER_TICK:
            CollisionSystem.processCompletedWork(work_completed_q, pq)
            CollisionSystem.processCollisionEvents(particles, walls, pq, nextLogicTick, work_requested_q, work_completed_q)

            for particle in particles:
                particle.move(TIME_PER_TICK)  # moves each particle in linear line
                # assert(particle.x >= 0 - 100 and particle.x <= window.width + 100)  
                # assert(particle.y >= 0 - 100 and particle.y <= window.height + 100)
            
            for particle_shape in particle_shapes:
                particle_shape.x = particles[particle_shape.index].x
                particle_shape.y = particles[particle_shape.index].y
            
            nextLogicTick += TIME_PER_TICK
            lag -= TIME_PER_TICK

        # render updates to window
        for particle_shape in particle_shapes:
            particle_shape.render()  

    window.close

def cleanup():
    window.close()
    while not work_requested_q.empty():
        work_requested_q.get_nowait()
    while not work_completed_q.empty():
        work_completed_q.get_nowait() 
    sys.exit()   

if __name__ == '__main__':
    window = GraphWin('Particle Simulation', 1024, 768, autoflush=False)
    main_menu = MainMenu(window, main)
    menu_options = {"New": main_menu.run, "Restart": main, "Exit": cleanup}
    window.addMenu(menu_options)

    # initialize multi-threading variables
    work_completed_q = mp.Queue()
    work_requested_q = mp.Queue()

    # initialize workers
    num_workers = 8
    workers = []
    for n in range(0, num_workers):
        workers.append(mp.Process(target=CollisionSystem.processWorkRequests, args=(work_requested_q, work_completed_q)))
        workers[n].daemon = True
        workers[n].start()

    main()