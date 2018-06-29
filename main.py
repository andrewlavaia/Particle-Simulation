'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import yaml
import time
from graphics import GraphWin, Text, Point, Entry
from collision import CollisionSystem 
from particles import Particle, Immovable, RectParticle, Wall
from ui import *

window = GraphWin('Particle Simulation', 800, 600, autoflush=False)
dataMap = {}
config_flag = 0

def load_config(file_string):
    with open(file_string) as f:
        dataMap = yaml.safe_load(f)
    return dataMap

def set_config(data):
    with open('config.yml', 'w') as outfile:
        yaml.safe_dump(data, outfile, default_flow_style=False)
    global config_flag 
    config_flag = 1

def create_particle_data(**kwargs):
    data = {'particles': { } }
    data.update( {'particles': kwargs} )
    return data

def main_menu():
    window.clear()
    window.setBackground('white')
    
    p = Point(100, 100)
    p2 = Point(100, 150)
    p3 = Point(100, 200)
    ib = InputBox(p, 'color', 'color: ')
    ib2 = InputBox(p2, 'unsigned_int', 'hello', 20)
    ib3 = InputBox(p3, 'unsigned_int', 'check this out', 40)
    ib.draw(window)
    ib2.draw(window)
    ib3.draw(window)

    # TODO 
    # move all labels and input boxes into their own class that can
    # be cloned, moved, and inserted anywhere on window
    t1_n = Text(Point(window.width/2.0 - 200.0, window.height/2.0 - 200.0), 
            '# of particles: ')
    g1_n = Entry(Point(window.width/2.0 + 100.0, window.height/2.0 - 200.0), 4)
    g1_n.setText(40)

    t1_color = t1_n.clone()
    t1_color.setText('color: ')
    t1_color.move(0, 50)
    g1_color = g1_n.clone()
    g1_color.setText('black')
    g1_color.width = 10
    g1_color.move(0, 50)

    t1_r = t1_n.clone()
    t1_r.setText('radius: ')
    t1_r.move(0, 100)
    g1_r = g1_n.clone()
    g1_r.setText(5.0)
    g1_r.width = 4
    g1_r.move(0, 100)

    t1_m = t1_n.clone()
    t1_m.setText('mass: ')
    t1_m.move(0, 150)
    g1_m = g1_n.clone()
    g1_m.setText(1.0)
    g1_m.width = 4
    g1_m.move(0, 150)
    
    t1_n.draw(window)
    t1_color.draw(window)
    t1_r.draw(window)
    t1_m.draw(window)

    g1_n.draw(window)
    g1_color.draw(window)
    g1_r.draw(window)
    g1_m.draw(window)

    # TODO 
    # validate inputs

    btn = Button(window, Point(window.width/2.0, window.height/2.0 + 100.0), 
            200, 100, 'Run Simulation')
    btn.activate()

    while True:
        last_clicked_pt = window.getMouse()
        if last_clicked_pt is not None:
            if btn.clicked(last_clicked_pt):
                ib.validateInput()
                kwargs = {
                    'group1': {
                        'n': g1_n.getText(),
                        'color': ib.getInput(),
                        'radius': g1_r.getText(),
                        'mass': g1_m.getText(),
                        'shape': 'Circle',
                        'width': float(g1_r.getText()) * 2,
                        'height': float(g1_r.getText()) * 2
                    }
                }
                
                # group2 = {
                #     'n': 2,
                #     'color': 'green',
                #     'radius': 30.0,
                #     'mass': 10.0,
                #     'shape': 'Circle',
                #     'width': 10.0,
                #     'height': 10.0
                # }

                # kwargs = {'group1': group1}
                data = create_particle_data(**kwargs)
                set_config(data)
                main()
            # else:
                # print('not in button')

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