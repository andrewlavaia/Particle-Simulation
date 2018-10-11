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
        self.group_data_dict = {}
        self.group_cntr = 0
        
        custom_sim_header = HeaderText(self.window, Point(350, 30), 'Custom Simulation')

        self.input_n = InputBox(self.window, Point(100.0, 100.0), 'unsigned_int', '# of particles: ', 4, 40)
        self.input_color = InputBox(self.window, self.input_n.getPointWithOffset(), 'color', 'color: ', 10, 'black')
        self.input_r = InputBox(self.window, self.input_color.getPointWithOffset(), 'unsigned_float', 'radius: ', 4,  5.0) 
        self.input_m = InputBox(self.window, self.input_r.getPointWithOffset(), 'unsigned_float', 'mass: ', 4,  1.0) 
        self.add_group_btn = Button(self.window, Point(self.input_m.point.x + 30, self.input_m.point.y + 60), 200, 30, 'Add Group')
        self.table = Table(self.window, Point(350, 100))
        self.table.addRow("id", "quantity", "color", "radius", "mass")
        self.group_data_dict = self.getConfigData()['particles']

        for group in self.group_data_dict.values():
            self.group_cntr += 1
            self.table.addRow(self.group_cntr, group['n'], group['color'], group['radius'], group['mass'])

        ln_1 = Line(Point(700, 0), Point(700, self.window.height))
        ln_1.draw(self.window)

        scenario_header = HeaderText(self.window, Point(850, 30), 'Scenarios')
        self.scenario_1_btn = Button(self.window, Point(850, 100), 100, 50, 'Default')

        self.simulation_btn = Button(self.window, Point(350, 500.0), 150, 75, 'Run Simulation')

    def run(self):
        self.loadMenu()
        while True:    
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None:
                if self.simulation_btn.clicked(last_clicked_pt) and self.validInputs():
                    self.setConfigData()
                    return self.callback()

                elif self.add_group_btn.clicked(last_clicked_pt) and self.validInputs():
                    self.addGroupToDict()

                elif self.scenario_1_btn.clicked(last_clicked_pt):
                    self.config_flag = 1
                    return self.callback()

                else:
                    for row in self.table.rows:
                        if row.button and row.button.clicked(last_clicked_pt):
                            self.deleteGroupFromDict(row.values[0]) 
                        
    def getConfigData(self):
        config_data = {}
        if self.config_flag == 1:
            config_data = file_utils.load_config('config_default.yml')
        elif self.config_flag == 0:
            config_data = file_utils.load_config('config.yml')
        return config_data
    
    def setConfigData(self):
        data = self.create_particle_data(**self.group_data_dict)
        file_utils.set_config(data) 
        self.config_flag = 0

    def addGroupToDict(self):
        d = self.group_data_dict
        n = self.input_n.getInput()
        color = self.input_color.getInput()
        r = self.input_r.getInput()
        m = self.input_m.getInput()

        self.group_cntr += 1
        group_name = 'group' + str(self.group_cntr)
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
        self.group_data_dict = d
        self.table.addRow(self.group_cntr, n, color, r, m)

    def deleteGroupFromDict(self, index):
        key = "group" + str(index)
        del self.group_data_dict[key]
        self.table.deleteRow(index) 

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

    def validInputs(self):
       return self.input_n.validateInput() and \
                self.input_color.validateInput() and \
                self.input_r.validateInput() and \
                self.input_m.validateInput()
