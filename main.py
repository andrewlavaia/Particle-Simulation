'''
Program: main.py
Runs a particle simulation that draws 
different types of particles colliding 
with one another
'''
import yaml
import time
from graphics import GraphWin, Text, Point, Entry, Line
from collision import CollisionSystem 
from particles import Particle, Immovable, RectParticle, Wall
from ui import *
import multiprocessing as mp
import os
import worker
import pdb

window = GraphWin('Particle Simulation', 800, 600, autoflush=False)
dataMap = {}
config_flag = 1

def load_config(file_string):
    with open(file_string) as f:
        dataMap = yaml.safe_load(f)
    return dataMap

def set_config(data):
    with open('config.yml', 'w') as outfile:
        yaml.safe_dump(data, outfile, default_flow_style=False)
    global config_flag 
    config_flag = 0

def create_particle_data(**kwargs):
    data = {'particles': { } }
    data.update( {'particles': kwargs} )
    return data

def main_menu():
    window.clear()
    window.setBackground('white')
    
    custom_sim_header = Text(Point(225, 30), 'Custom Simulation')
    custom_sim_header.setSize(24)
    custom_sim_header.setStyle('bold')
    custom_sim_header.draw(window)

    input_n = InputBox(Point(window.width/2.0 - 250.0, window.height/2.0 - 200.0), 
            'unsigned_int', '# of particles: ', 4, 40)
    input_n.draw(window)

    input_color = InputBox(input_n.getPointWithOffset(), 'color', 'color: ', 20, 'black')
    input_color.draw(window)

    input_r = InputBox(input_color.getPointWithOffset(), 'unsigned_float', 'radius: ', 4,  5.0) 
    input_r.draw(window)

    input_m = InputBox(input_r.getPointWithOffset(), 'unsigned_float', 'mass: ', 4,  1.0) 
    input_m.draw(window)

    # scenarios
    scenario_header = Text(Point(650, 30), 'Scenarios')
    scenario_header.setSize(22)
    scenario_header.setStyle('bold')
    scenario_header.draw(window)

    ln_1 = Line(Point(500, 0), Point(500, window.height))
    ln_1.draw(window)

    scenario_1_btn = Button(window, Point(650, 100), 
            100, 50, 'Default')
    scenario_1_btn.activate() 

    add_group_btn = Button(window, Point(125, window.height/2.0 + 150), 
            150, 75, 'Add Group')
    add_group_btn.activate()    

    simulation_btn = Button(window, Point(375, window.height/2.0 + 150.0), 
            150, 75, 'Run Simulation')
    simulation_btn.activate()

    group_data_dict = {}
    group_data_text = Text(Point(100, 520), 'Extra Groups Added: ' + str(len(group_data_dict)))
    group_data_text.setSize(12)
    group_data_text.setStyle('italic')
    group_data_text.draw(window)

    def addGroupToDict(d, n, color, r, m):
        group_name = 'group' + str(len(d) + 1)
        group = { 
            group_name: {
                'n': n,
                'color': color,
                'radius': r,
                'mass': m,
                'shape': 'Circle',
                'width': float(input_r.getInput()) * 2,
                'height': float(input_r.getInput()) * 2
            }
        }
        d.update(group)
        return d

    while True:    
        last_clicked_pt = window.getMouse()
        if last_clicked_pt is not None:
            if simulation_btn.clicked(last_clicked_pt):
                if (input_n.validateInput() and 
                        input_color.validateInput() and 
                        input_r.validateInput() and 
                        input_m.validateInput()):
                    
                    group_data_dict = addGroupToDict(group_data_dict, 
                            input_n.getInput(), input_color.getInput(), 
                            input_r.getInput(), input_m.getInput())

                    data = create_particle_data(**group_data_dict)
                    set_config(data)
                    main()
                else:
                    print('invalid inputs')
            elif add_group_btn.clicked(last_clicked_pt):
                if (input_n.validateInput() and 
                        input_color.validateInput() and 
                        input_r.validateInput() and 
                        input_m.validateInput()):
                    group_data_dict = addGroupToDict(group_data_dict, 
                            input_n.getInput(), input_color.getInput(), 
                            input_r.getInput(), input_m.getInput())
                    group_data_text.setText('Extra Groups Added: ' + str(len(group_data_dict))) 
            elif scenario_1_btn.clicked(last_clicked_pt):
                global config_flag
                config_flag = 1
                main()

def main():
    if config_flag == 1:
        dataMap = load_config('config_default.yml')
    elif config_flag == 0:
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

    # initialize multithreading variables
    lock = mp.Lock()
    # cond = mp.Event()
    worker1 = mp.Process(target=worker.processQueue, args=(worker.work_queue, cs))
    worker2 = mp.Process(target=worker.processQueue, args=(worker.work_queue, cs))
    worker1.daemon = True # let boss process terminate worker automatically
    worker2.daemon = True
    worker1.start()
    worker2.start()

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
            cs.queueCollisionEvents(nextLogicTick)

            for particle in particles:
                particle.move(TIME_PER_TICK)  # moves each particle in linear line
                # assert(particle.x >= 0 - 100 and particle.x <= window.width + 100)  
                # assert(particle.y >= 0 - 100 and particle.y <= window.height + 100)
            
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

if __name__ == '__main__':
    main()