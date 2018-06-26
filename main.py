'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import yaml
import time
from graphics import GraphWin, Text, Point, Button, Entry
from collision import CollisionSystem 
from particles import Particle, Immovable, RectParticle, Wall

window = GraphWin('Particle Simulation', 800, 600, autoflush=False)
dataMap = {}
config_flag = 0

def load_config(file_string):
    # load particle options
    with open(file_string) as f:
        # use safe_load instead load
        dataMap = yaml.safe_load(f)
    return dataMap

def set_config(input_1):
    data = dict(
        particles = dict(
            group1 = dict(
                n = 10,
                color = 'black',
                radius = 5.0,
                mass = 1.0,
                shape = "Circle",
                width = 10.0,
                height = 10.0 
            ),
            group2 = dict(                
                n = 1,
                color = 'green',
                radius = 50.0,
                mass = 20.0,
                shape = "Circle",
                width = 10.0,
                height = 10.0
            )
        )
    )

    with open('config.yml', 'w') as outfile:
        yaml.safe_dump(data, outfile, default_flow_style=False)
    
    global config_flag 
    config_flag = 1

def main_menu():
    window.clear()
    window.setBackground('white')
    txt_1_particles = Text(Point(window.width/2.0 - 200.0, window.height/2.0 - 50.0), 
            '# of particles: ')
    txt_1_particles.setSize(24)
    txt_1_particles.draw(window)
    input_1_particles = Entry(Point(window.width/2.0 + 200.0, window.height/2.0 - 50.0), 4)
    input_1_particles.setSize(24)
    input_1_particles.setText(40)
    input_1_particles.draw(window)

    btn = Button(window, Point(window.width/2.0, window.height/2.0 + 100.0), 
            200, 100, 'Run Simulation')
    btn.activate()

    while True:
        last_clicked_pt = window.getMouse()
        if last_clicked_pt is not None:
            if btn.clicked(last_clicked_pt):
                set_config('x')
                main()
            else:
                print('not in button')

def main():
    if not config_flag:
        dataMap = load_config('config_default.yml')
    else:
        dataMap = load_config('config.yml')

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