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
from particles import Particle, Immovable, RectParticle, Wall

# load particle options
with open('config.yaml') as f:
    # use safe_load instead load
    dataMap = yaml.safe_load(f)

window = GraphWin('Particle Simulation', 800, 600, autoflush=False)

def main():
    menu_options = { "New": main, "Exit": window.close}
    window.addMenu(menu_options)
    window.setBackground('white')

    # clear window of any previously drawn items
    for item in window.items[:]:
        item.undraw()
    window.update

    particles = []

    # create particles from config file
    for key in dataMap['particles']:
        curr = dataMap['particles'][key]
        n = int(curr['n'])
        for i in range(0, n):
            particles.append(Particle(window, 
                    radius = float(curr['radius']),
                    color = curr['color'],
                    mass = float(curr['mass']),
                    shape = curr['shape'],
                    width = float(curr['width']),
                    height = float(curr['height'])
            ))

    # particles.append(SquareParticle(window, color = 'green'))
    # particles.append(Immovable(window, radius = 100, x = 400, y = 400, color = 'red'))
    
    # # create walls
    # for i in range(0, 30):  
    #     particles.append(Wall(window, x = 400, y = i*4, color = 'red'))
    #     particles.append(Wall(window, x = 400, y = window.height - i*4, color = 'red'))

    # draw all particles
    for particle in particles:
        particle.draw()

    # initialize collision system
    cs = CollisionSystem(particles)

    # initialize simulation variables
    simTime = 0.0
    limit = 10000

    TICKS_PER_SECOND = 120 # how often collisions are checked 
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND # in seconds
    nextLogicTick = TIME_PER_TICK

    lastFrameTime = time.time()

    def pause():
        while window.checkKey() != "space": # pause until user hits space again
            pass

    # Main Simulation Loop
    while simTime < limit:
        currentTime = time.time()
        elapsed = currentTime - lastFrameTime
        lastFrameTime = currentTime

        simTime = simTime + elapsed
        
        if simTime > nextLogicTick:
            cs.processEvents(nextLogicTick)

            for particle in particles:
                particle.move(TIME_PER_TICK)  # moves each particle in linear line
                assert(particle.x >= 0 - 100 and particle.x <= window.width + 100)  
                assert(particle.y >= 0 - 100 and particle.y <= window.height + 100)
            
            nextLogicTick = nextLogicTick + TIME_PER_TICK
        
        else:
            # render updates to window
            for particle in particles:
                particle.render()  

        # check if user wants to end simulation
        if window.checkMouse() is not None:
            window.close()

        if window.checkKey() == "space":
            pause()
            lastFrameTime = time.time()
    window.close

main()