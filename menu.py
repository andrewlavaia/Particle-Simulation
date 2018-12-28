from abc import ABCMeta, abstractmethod
import file_utils
from ui import *

class MainMenu:
    def __init__(self, window, callback):
        self.window = window
        self.callback = callback
        self.config_data = file_utils.load_config('config.yml')
        
        self.particle_table = ParticleTable(Table(self.window, Point(350, 350)), self.config_data)
        self.wall_table = WallTable(Table(self.window, Point(710, 175), 20, 110), self.config_data)
        self.scenarios = []

    def drawMenu(self):
        self.window.clear()
        self.window.setBackground('white')

        self.particle_table.table.redraw()
        self.wall_table.table.redraw()
        
        custom_sim_header = HeaderText(self.window, Point(350, 30), 'Custom Simulation')
        self.simulation_btn = Button(self.window, Point(350, 135), 200, 100, 'Run Simulation')

        particle_header = HeaderText(self.window, Point(350, 290), 'Particles')
        self.input_n = InputBox(self.window, Point(100.0, 350.0), 'unsigned_int', '# of particles: ', 4, 40)
        self.input_color = InputBox(self.window, self.input_n.getPointWithOffset(), 'color', 'color: ', 10, 'black')
        self.input_r = InputBox(self.window, self.input_color.getPointWithOffset(), 'unsigned_float', 'radius: ', 4,  5.0) 
        self.input_m = InputBox(self.window, self.input_r.getPointWithOffset(), 'unsigned_float', 'mass: ', 4,  1.0) 
        self.add_group_btn = Button(self.window, Point(self.input_m.point.x + 30, self.input_m.point.y + 60), 150, 30, 'Add Group')

        environment_header = HeaderText(self.window, Point(850, 30), 'Environment')

        self.input_p0x = InputBox(self.window, Point(750.0, 100.0), 'unsigned_float', 'Point 0:', 4, 10)
        self.input_p0y = InputBox(self.window, Point(800.0, 100.0), 'unsigned_float', '', 4, 10)
        self.input_p1x = InputBox(self.window, Point(750.0, 130.0), 'unsigned_float', 'Point 1:', 4,  50) 
        self.input_p1y = InputBox(self.window, Point(800.0, 130.0), 'unsigned_float', '', 4, 50) 
        self.add_wall_btn = Button(self.window, Point(950.0, 115.0), 75, 30, 'Add Wall')

        ln_0 = Line(Point(0, 250), Point(700, 250))
        ln_0.draw(self.window)

        ln_1 = Line(Point(700, 0), Point(700, self.window.height))
        ln_1.draw(self.window)

        ln_2 = Line(Point(700, 500), Point(self.window.width, 500))
        ln_2.draw(self.window)

        scenario_header = HeaderText(self.window, Point(850, 525), 'Scenarios')
        scenario_1_btn = Button(self.window, Point(780, 575), 120, 30, 'Standard')
        self.scenarios.append({'btn': scenario_1_btn, 'file': 'scenarios/standard.yml'})
        scenario_2_btn = Button(self.window, Point(780, 625), 120, 30, '200 Hundred')
        self.scenarios.append({'btn': scenario_2_btn, 'file': 'scenarios/200hundred.yml'})
        scenario_3_btn = Button(self.window, Point(780, 675), 120, 30, 'Big + Small')
        self.scenarios.append({'btn': scenario_3_btn, 'file': 'scenarios/bigsmall.yml'})
        scenario_4_btn = Button(self.window, Point(780, 725), 120, 30, 'Crazy')
        self.scenarios.append({'btn': scenario_4_btn, 'file': 'scenarios/crazy.yml'})
        scenario_5_btn = Button(self.window, Point(940, 575), 120, 30, 'Walls a plenty')
        self.scenarios.append({'btn': scenario_5_btn, 'file': 'scenarios/wallsaplenty.yml'})
        scenario_6_btn = Button(self.window, Point(940, 625), 120, 30, 'Diffusion')
        self.scenarios.append({'btn': scenario_6_btn, 'file': 'scenarios/diffusion.yml'})
        scenario_7_btn = Button(self.window, Point(940, 675), 120, 30, 'Volcano')
        self.scenarios.append({'btn': scenario_7_btn, 'file': 'scenarios/volcano.yml'})
        scenario_8_btn = Button(self.window, Point(940, 725), 120, 30, 'Triangle Split')
        self.scenarios.append({'btn': scenario_8_btn, 'file': 'scenarios/trianglesplit.yml'})

    def run(self):
        self.drawMenu()

        while True:    
            last_clicked_pt = self.window.getMouse()
            if last_clicked_pt is not None:
                if self.simulation_btn.clicked(last_clicked_pt):
                    self.setConfigData()
                    return self.callback()

                elif self.add_group_btn.clicked(last_clicked_pt) and self.validInputs():
                    n = self.input_n.getInput()
                    color = self.input_color.getInput()
                    r = self.input_r.getInput()
                    m = self.input_m.getInput()
                    self.particle_table.insertFromInputs(n, color, r, m)
                
                elif self.add_wall_btn.clicked(last_clicked_pt) and self.validInputs():
                    p0x = self.input_p0x.getInput()
                    p0y = self.input_p0y.getInput()
                    p1x = self.input_p1x.getInput()
                    p1y = self.input_p1y.getInput()
                    self.wall_table.insertFromInputs(p0x, p0y, p1x, p1y)

                else:
                    self.particle_table.checkRemoveBtnClicked(last_clicked_pt)
                    self.wall_table.checkRemoveBtnClicked(last_clicked_pt)

                    for scen in self.scenarios:
                        if scen['btn'].clicked(last_clicked_pt):
                            self.config_data = file_utils.load_config(scen['file'])
                            self.particle_table.setData(self.config_data)
                            self.wall_table.setData(self.config_data)     
    
    def setConfigData(self):
        data = {
            'particles': self.particle_table.data_dict, 
            'walls': self.wall_table.data_dict
        }
        file_utils.set_config(data) 

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
                self.input_m.validateInput() and \
                self.input_p0x.validateInput() and \
                self.input_p0y.validateInput() and \
                self.input_p1x.validateInput() and \
                self.input_p1y.validateInput()


class ConfigTableBase(metaclass=ABCMeta):
    def __init__(self, name, table, config_data):
        self.name = name
        self.row_cntr = 0
        self.data_dict = config_data.get(self.name, {})
        self.table = table

    @abstractmethod
    def loadRowsFromConfig(self):
        pass

    @abstractmethod
    def insertFromInputs(self):
        pass 

    def checkRemoveBtnClicked(self, last_clicked_pt):
        for row in self.table.rows:
            if row.button and row.button.clicked(last_clicked_pt):
                self.remove(row.values[0]) 

    def remove(self, index):
        self.data_dict.pop(str(index))
        self.table.deleteRow(int(index))

    def setData(self, config_data):
        self.data_dict = config_data.get(self.name, {})
        self.loadRowsFromConfig()
        self.table.redraw()


class ParticleTable(ConfigTableBase):
    def __init__(self, table, config_data):
        super().__init__("particles", table, config_data)
        self.loadRowsFromConfig()

    def loadRowsFromConfig(self):
        self.table.deleteAllRows()
        self.table.addRow("id", "quantity", "color", "radius", "mass")
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


class WallTable(ConfigTableBase):
    def __init__(self, table, config_data):
        super().__init__("walls", table, config_data)
        self.loadRowsFromConfig()

    def loadRowsFromConfig(self):
        self.table.deleteAllRows()
        self.table.addRow("id", "Point 0", "Point 1")
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
        p0 = "(" + str(p0x) + ", " + str(p0y) + ")" 
        p1 = "(" + str(p1x) + ", " + str(p1y) + ")" 
        self.table.addRow(self.row_cntr, p0, p1)
