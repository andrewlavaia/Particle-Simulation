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
from particles import Particle, Immovable, RectParticle, Wall, ParticleShape
from queue import PriorityQueue
import heapq
from ui import *
import multiprocessing as mp
import multiprocessing.managers as mp_mgr
import os
import pdb

class ProcessManager(mp_mgr.SyncManager):
    pass

ProcessManager.register("PriorityQueue", PriorityQueue)

def Manager():
    m = ProcessManager()
    m.start()
    return m

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

    # initialize multithreading variables
    # lock = mp.Lock()
    # cond = mp.Event()    
    manager = Manager()
    # particles = manager.list()
    work_completed_q = mp.Queue()
    work_requested_q = mp.Queue()
    pq = []
    particles = []
    particle_shapes = []
    nextLogicTick = mp.Value('d', 0.0)

    # create particles from config file
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

    # draw all particles
    for particle_shape in particle_shapes:
        particle_shape.draw()
    
    for particle in particles:
        CollisionSystem.predict(particle, 0.0, 10000, particles, work_completed_q)

    # initialize workers
    num_workers = 4
    workers = []
    for n in range(0, num_workers):
        workers.append(mp.Process(target=CollisionSystem.processWorkRequests, args=(work_requested_q, work_completed_q)))
        workers[n].daemon = True
        workers[n].start()

    # initialize simulation variables
    simTime = 0.0
    limit = 10000

    TICKS_PER_SECOND = 120 # how often collisions are checked 
    TIME_PER_TICK = 1.0/TICKS_PER_SECOND # in seconds
    nextLogicTick.value = TIME_PER_TICK

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

        if simTime > nextLogicTick.value:
            # CollisionSystem.processWorkRequests(work_requested_q, work_completed_q)
            CollisionSystem.processCompletedWork(work_completed_q, pq)
            CollisionSystem.processCollisionEvents(particles, pq, nextLogicTick.value, work_requested_q, work_completed_q)

            for particle in particles:
                particle.move(TIME_PER_TICK)  # moves each particle in linear line
                # assert(particle.x >= 0 - 100 and particle.x <= window.width + 100)  
                # assert(particle.y >= 0 - 100 and particle.y <= window.height + 100)
            
            nextLogicTick.value = nextLogicTick.value + TIME_PER_TICK
           
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
    window = GraphWin('Particle Simulation', 800, 600, autoflush=False)
    dataMap = {}
    config_flag = 1
    
    main()