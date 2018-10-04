import file_utils
from ui import *

class MainMenu:
    def __init__(self, window, callback):
        self.window = window
        self.callback = callback
        self.config_flag = 1
        
    def loadMenu(self):
        self.window.clear()
        self.window.setBackground('white')
        
        custom_sim_header = Text(Point(225, 30), 'Custom Simulation')
        custom_sim_header.setSize(24)
        custom_sim_header.setStyle('bold')
        custom_sim_header.draw(self.window)

        self.input_n = InputBox(Point(self.window.width/2.0 - 250.0, self.window.height/2.0 - 200.0), 
                'unsigned_int', '# of particles: ', 4, 40)
        self.input_n.draw(self.window)

        self.input_color = InputBox(self.input_n.getPointWithOffset(), 'color', 'color: ', 20, 'black')
        self.input_color.draw(self.window)

        self.input_r = InputBox(self.input_color.getPointWithOffset(), 'unsigned_float', 'radius: ', 4,  5.0) 
        self.input_r.draw(self.window)

        self.input_m = InputBox(self.input_r.getPointWithOffset(), 'unsigned_float', 'mass: ', 4,  1.0) 
        self.input_m.draw(self.window)

        # scenarios
        scenario_header = Text(Point(650, 30), 'Scenarios')
        scenario_header.setSize(22)
        scenario_header.setStyle('bold')
        scenario_header.draw(self.window)

        ln_1 = Line(Point(500, 0), Point(500, self.window.height))
        ln_1.draw(self.window)

        self.scenario_1_btn = Button(self.window, Point(650, 100), 
                100, 50, 'Default')
        self.scenario_1_btn.activate() 

        self.add_group_btn = Button(self.window, Point(125, self.window.height/2.0 + 150), 
                150, 75, 'Add Group')
        self.add_group_btn.activate()    

        self.simulation_btn = Button(self.window, Point(375, self.window.height/2.0 + 150.0), 
                150, 75, 'Run Simulation')
        self.simulation_btn.activate()

        self.group_data_dict = {}

        self.group_data_text = Text(Point(100, 620), 'Extra Groups Added: ' + str(len(self.group_data_dict)))
        self.group_data_text.setSize(12)
        self.group_data_text.setStyle('italic')
        self.group_data_text.draw(self.window)

    def run(self):
        self.loadMenu()
        while True:    
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None:
                if self.simulation_btn.clicked(last_clicked_pt):
                    if (self.input_n.validateInput() and 
                            self.input_color.validateInput() and 
                            self.input_r.validateInput() and 
                            self.input_m.validateInput()):
                        
                        self.group_data_dict = self.addGroupToDict(self.group_data_dict, 
                                self.input_n.getInput(), self.input_color.getInput(), 
                                self.input_r.getInput(), self.input_m.getInput())

                        data = self.create_particle_data(**self.group_data_dict)
                        file_utils.set_config(data) 
                        self.config_flag = 0

                        return self.callback()
                    else:
                        print('invalid inputs')
                elif self.add_group_btn.clicked(last_clicked_pt):
                    if (self.input_n.validateInput() and 
                            self.input_color.validateInput() and 
                            self.input_r.validateInput() and 
                            self.input_m.validateInput()):
                        self.group_data_dict = self.addGroupToDict(self.group_data_dict, 
                                self.input_n.getInput(), self.input_color.getInput(), 
                                self.input_r.getInput(), self.input_m.getInput())
                        self.group_data_text.setText('Extra Groups Added: ' + str(len(self.group_data_dict))) 
                elif self.scenario_1_btn.clicked(last_clicked_pt):
                    self.config_flag = 1
                    return self.callback()
    
    def getConfigData(self):
        config_data = {}
        if self.config_flag == 1:
            config_data = file_utils.load_config('config_default.yml')
        elif self.config_flag == 0:
            config_data = file_utils.load_config('config.yml')
        return config_data

    def addGroupToDict(self, d, n, color, r, m):
        group_name = 'group' + str(len(d) + 1)
        group = { 
            group_name: {
                'n': int(n),
                'color': color,
                'radius': float(r),
                'mass': float(m),
                'shape': 'Circle',
                'width': float(self.input_r.getInput()) * 2,
                'height': float(self.input_r.getInput()) * 2
            }
        }
        d.update(group)
        return d

    def create_particle_data(self, **kwargs):
        data = {'particles': { } }
        data.update( {'particles': kwargs} )
        return data

    def pause(self):
        message = Text(Point(self.window.width/2.0, self.window.height/2.0 - 50.0), 'Paused')
        message.setSize(24)
        message.draw(self.window)
        while self.window.checkKey() != "space": # pause until user hits space again
            pass
        message.undraw()
    