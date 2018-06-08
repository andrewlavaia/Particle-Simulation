'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import yaml
import time
from graphics import GraphWin
from collision import CollisionSystem 
from particles import Particle, Immovable

# load particle options
with open('config.yaml') as f:
    # use safe_load instead load
    dataMap = yaml.safe_load(f)

def main():
    window = GraphWin('Particle Simulation', 800, 600)
    window.setBackground('white')

    particles = []

    # create particles from config file
    for key in dataMap['particles']:
        curr = dataMap['particles'][key]
        n = int(curr['n'])
        for i in range(0, n):
            particles.append(Particle(window, 
                    radius = float(curr['radius']),
                    color = curr['color'],
                    m = float(curr['mass'])
            ))


    #particles.append(Immovable(window, radius = 100, x = 400, y = 400, color = 'red'))
    
    # create additional walls
    # for i in range(0, 50):  
    #     particles.append(Immovable(window, radius = 5, x = 400, y = i*10, color = 'red'))

    # draw all particles
    for particle in particles:
        particle.draw()

    # initialize collision system
    cs = CollisionSystem(particles)

    # initialize simulation variables
    simTime = 0.0
    limit = 10000

    TICKS_PER_SECOND = 20 # how often collisions are checked
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND # in seconds
    lastLogicTick = 0.0
    nextLogicTick = TIME_PER_TICK

    lastFrameTime = time.time()

    # Main Simulation Loop
    while simTime < limit:
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        simTime = simTime + elapsed
        lastFrameTime = currentTime
        
        while simTime > nextLogicTick:
            cs.processEvents(lastLogicTick)

            for particle in particles:
                particle.move(TIME_PER_TICK)  # moves each particle in linear line  
            
            lastLogicTick = nextLogicTick
            nextLogicTick = nextLogicTick + TIME_PER_TICK
        
        # render updates to window
        for particle in particles:
            particle.render()  

        # check if user wants to end simulation
        if window.checkMouse() is not None:
            break
  
    window.close

main()