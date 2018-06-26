'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import yaml
import time
from graphics import GraphWin, Text, Point, Button
from collision import CollisionSystem 
from particles import Particle, Immovable, RectParticle, Wall

# load particle options
with open('config.yaml') as f:
    # use safe_load instead load
    dataMap = yaml.safe_load(f)

window = GraphWin('Particle Simulation', 800, 600, autoflush=False)

# TODO
# start with a new main menu screen that allows the user to 
# specify the parameters (how many balls, etc) for a random
# simulation or pick specific pre-defined scenarios

# how to implement? Pop-up menu, or just initial screen is 
# blank with buttons and then those are undrawn when simulation 
# starts?

def main_menu():
    window.clear()
    window.setBackground('white')
    txt_1_particles = Text(Point(window.width/2.0 - 200.0, window.height/2.0 - 50.0), 
            '# of particles: ')
    txt_1_particles.setSize(24)
    txt_1_particles.draw(window)
    btn = Button(window, Point(window.width/2.0 - 100.0, window.height/2.0 + 100.0), 
            200, 100, 'Run Simulation')
    btn.activate()

    while True:
        last_clicked_pt = window.getMouse()
        if last_clicked_pt is not None:
            if btn.clicked(last_clicked_pt):
                print('in button')
            else:
                print('not in button')

def main():
    menu_options = {"New": main_menu, "Restart": main, "Exit": window.close}
    window.addMenu(menu_options)
    window.setBackground('white')
    window.clear()

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
            pass
            # window.close()

        if window.checkKey() == "space":
            pause()
            lastFrameTime = time.time()
    window.close

main()