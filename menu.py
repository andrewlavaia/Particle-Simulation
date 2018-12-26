import file_utils
from ui import *

class MainMenu:
    def __init__(self, window, callback):
        self.window = window
        self.callback = callback
        self.config_flag = 1
        config_data = self.getConfigData()
        self.particle_table = ParticleTable(Table(self.window, Point(350, 100)), config_data)
        self.wall_table = WallTable(Table(self.window, Point(710, 150), 20, 110), config_data)
        
    def loadMenu(self):
        self.window.clear()
        self.window.setBackground('white')
        self.group_data_dict = {}
        self.group_cntr = 0
        self.wall_cntr = 0
        
        custom_sim_header = HeaderText(self.window, Point(350, 30), 'Custom Simulation')

        self.input_n = InputBox(self.window, Point(100.0, 100.0), 'unsigned_int', '# of particles: ', 4, 40)
        self.input_color = InputBox(self.window, self.input_n.getPointWithOffset(), 'color', 'color: ', 10, 'black')
        self.input_r = InputBox(self.window, self.input_color.getPointWithOffset(), 'unsigned_float', 'radius: ', 4,  5.0) 
        self.input_m = InputBox(self.window, self.input_r.getPointWithOffset(), 'unsigned_float', 'mass: ', 4,  1.0) 
        self.add_group_btn = Button(self.window, Point(self.input_m.point.x + 30, self.input_m.point.y + 60), 200, 30, 'Add Group')

        environment_header = HeaderText(self.window, Point(850, 30), 'Environment')

        ln_1 = Line(Point(700, 0), Point(700, self.window.height))
        ln_1.draw(self.window)

        ln_2 = Line(Point(700, 500), Point(self.window.width, 500))
        ln_2.draw(self.window)

        scenario_header = HeaderText(self.window, Point(850, 525), 'Scenarios')
        self.scenario_1_btn = Button(self.window, Point(775, 600), 100, 50, 'Default')

        self.simulation_btn = Button(self.window, Point(350, 600.0), 150, 75, 'Run Simulation')

    def run(self):
        self.loadMenu()
        self.particle_table.table.redraw()
        self.wall_table.table.redraw()
        while True:    
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None:
                if self.simulation_btn.clicked(last_clicked_pt) and self.validInputs():
                    self.setConfigData()
                    return self.callback()

                elif self.add_group_btn.clicked(last_clicked_pt) and self.validInputs():
                    n = self.input_n.getInput()
                    color = self.input_color.getInput()
                    r = self.input_r.getInput()
                    m = self.input_m.getInput()
                    self.particle_table.insertFromInputs(n, color, r, m)

                elif self.scenario_1_btn.clicked(last_clicked_pt):
                    self.config_flag = 1
                    return self.callback()

                else:
                    for row in self.particle_table.table.rows:
                        if row.button and row.button.clicked(last_clicked_pt):
                            self.particle_table.remove(row.values[0]) 
                    for row in self.wall_table.table.rows:
                        if row.button and row.button.clicked(last_clicked_pt):
                            self.wall_table.remove(row.values[0]) 
                        
    def getConfigData(self):
        config_data = {}
        if self.config_flag == 1:
            config_data = file_utils.load_config('config_default.yml')
        elif self.config_flag == 0:
            config_data = file_utils.load_config('config.yml')
        return config_data
    
    def setConfigData(self):
        data = {
            'particles': self.particle_table.data_dict, 
            'walls': self.wall_table.data_dict
        }
        file_utils.set_config(data) 
        self.config_flag = 0

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


class ParticleTable:
    def __init__(self, table, config_data):
        self.name = "particles"
        self.row_cntr = 0
        self.data_dict = config_data.get(self.name, {})
        self.table = table
        self.table.addRow("id", "quantity", "color", "radius", "mass")
        self.loadRowsFromConfig()

    def loadRowsFromConfig(self):
        for name, data in self.data_dict.items():
            key = int(name)
            self.row_cntr = key if key > self.row_cntr else self.row_cntr
            self.table.addRow(key, data['n'], data['color'], data['radius'], data['mass'])

    def insertFromInputs(self, n, color, r, m):
        self.row_cntr += 1
        group_name = str(self.row_cntr)
        group = { 
            group_name: {
                'n': int(n),
                'color': color,
                'radius': float(r),
                'mass': float(m),
                'shape': 'Circle',
                'width': float(r) * 2,
                'height': float(r) * 2
            }
        }
        self.data_dict.update(group)
        self.table.addRow(self.row_cntr, n, color, r, m)
    
    def remove(self, index):
        self.data_dict.pop(str(index))
        self.table.deleteRow(int(index))


class WallTable:
    def __init__(self, table, config_data):
        self.name = "walls"
        self.row_cntr = 0
        self.data_dict = config_data.get(self.name, {})
        self.table = table
        self.table.addRow("id", "Point 0", "Point 1")
        self.loadRowsFromConfig()

    def loadRowsFromConfig(self):
        for name, data in self.data_dict.items():
            key = int(name)
            self.row_cntr = key if key > self.row_cntr else self.row_cntr
            self.table.addRow(
                    key, 
                    str('(' + str(data['p0x']) + ', ' + str(data['p0y']) + ')'), 
                    str('(' + str(data['p1x']) + ', ' + str(data['p1y']) + ')')
            )

    def insertFromInputs(self, p0x, p0y, p1x, p1y):
        self.row_cntr += 1
        group_name = str(self.row_cntr)
        group = { 
            group_name: {
                'p0x': float(p0x),
                'p0y': float(p0y),
                'p1x': float(p1x),
                'p1y': float(p1y),
            }
        }
        self.data_dict.update(group)
        self.table.addRow(self.row_cntr, p0x, p0y, p1x, p1y)
    
    def remove(self, index):
        self.data_dict.pop(str(index))
        self.table.deleteRow(int(index))