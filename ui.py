import re
from abc import ABCMeta, abstractmethod
from graphics import *
from colors import available_colors

class UIBase(metaclass = ABCMeta):
    @abstractmethod
    def draw(self):
        """Draws object on self.canvas"""

    @abstractmethod
    def undraw(self):
        """Removes object from self.canvas"""

    def redraw(self):
        self.undraw()
        self.draw()


class Button(UIBase):
    def __init__(self, canvas, center, width, height, label):
        """ Creates a rectangular button """
        self.canvas = canvas
        w,h = width/2.0, height/2.0
        x,y = center.getX(), center.getY()
        self.xmax, self.xmin = x+w, x-w
        self.ymax, self.ymin = y+h, y-h
        p1 = Point(self.xmin, self.ymin)
        p2 = Point(self.xmax, self.ymax)
        self.rect = Rectangle(p1,p2)
        self.rect.setFill('lightgray')
        self.label = Text(center, label)
        self.draw()
        self.activate()

    def clicked(self, p):
        """ RETURNS true if button active and p is inside"""
        return self.active and \
               self.xmin <= p.getX() <= self.xmax and \
               self.ymin <= p.getY() <= self.ymax

    def getLabel(self):
        return self.label.getText()

    def activate(self):
        self.label.setFill('black')
        self.rect.setWidth(2)
        self.active = 1

    def deactivate(self):
        self.label.setFill('darkgrey')
        self.rect.setWidth(1)
        self.active = 0

    def draw(self):
        self.rect.draw(self.canvas)
        self.label.draw(self.canvas)

    def undraw(self):
        self.rect.undraw()
        self.label.undraw()


class InputBox(UIBase):
    def __init__(self, canvas, point, input_type, label_text, char_max = 10, default_val = None):
        allowed_types = ['unsigned_int', 'unsigned_float', 'color', 'float', 'shape']
        if input_type not in allowed_types:
            raise Exception('InputBox: type given is not an allowed type')
        
        self.canvas = canvas
        self.point = point
        self.type = input_type
        self.label = Text(point, label_text)
        x_offset = 100 + ((char_max - 10)/2.0 * 9) # difference between default char_max and font size / 2
        self.entry = Entry(Point(point.x + x_offset, point.y), char_max)
        if default_val is not None:
            self.setInput(default_val)
        
        self.draw()

    def getInput(self):
        return self.entry.getText()

    def validateInput(self):
        flag = True
        if self.type == 'unsigned_int':
            flag = isinstance(int(self.getInput()), int) and int(self.getInput()) > 0
        elif self.type == 'unsigned_float':
            flag = isinstance(float(self.getInput()), float) and float(self.getInput()) > 0 
        elif self.type == 'color':
            flag = (self.getInput() in available_colors or 
                    re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', self.getInput()))
        elif self.type == 'float':
            flag = isinstance(float(self.getInput()), float) 
        elif self.type == 'shape':
            flag = self.getInput() in ['Circle', 'circle', 'Square', 'square']

        if not flag:
            self.label.setTextColor('red')
        else:
            self.label.setTextColor('black')
        
        return flag
                
    def setInput(self, val):
        self.entry.setText(val)
        if self.validateInput() is not True:
            self.entry.setText('')

    def draw(self):
        self.label.draw(self.canvas)
        self.entry.draw(self.canvas)
    
    def undraw(self):
        self.label.undraw()
        self.entry.undraw()        

    def getPointWithOffset(self):
        return Point(self.point.x, self.point.y + 30)

class Table(UIBase):
    def __init__(self, canvas, point, row_height=30, col_width=70):
        self.canvas = canvas
        self.point = point
        self.rows = []
        self.row_height = row_height
        self.col_width = col_width

    def addRow(self, *args):
        row = TableRow(self.canvas, args)
        self.rows.append(row)
        self.redraw()

    def deleteRow(self, row_id):
        for row in self.rows:
            if row.values[0] == row_id:
                row.undraw()
                self.rows.remove(row)
        self.redraw()
    
    def deleteAllRows(self):
        for row in self.rows:
            row.undraw()
        self.rows = []

    def draw(self):
        offset = Point(0, 0)
        for i in range(len(self.rows)):
            row = self.rows[i]
            offset.y = self.point.y + (i * self.row_height)
            for j in range(len(row.values)):
                offset.x = self.point.x + (j * self.col_width)
                row.labels.append(Text(offset, row.values[j]))
            if i > 0: 
                offset.x = self.point.x + (len(row.values) * self.col_width) - 30            
                row.button = Button(self.canvas, offset, 15, 15, '-')
            row.draw()

    def undraw(self):
        for row in self.rows:
            row.undraw()


class TableRow(UIBase):
    def __init__(self, canvas, *args):
        self.canvas = canvas
        self.values = list(*args)
        self.labels = []
        self.button = None

    def draw(self):
        for label in self.labels:
            label.draw(self.canvas)
        
    def undraw(self):
        for label in self.labels:
            label.undraw()
        if self.button:
            self.button.deactivate()
            self.button.undraw()
        self.labels.clear()
        self.button = None

class HeaderText(UIBase):
    def __init__(self, canvas, point, text):
        self.canvas = canvas
        self.text = Text(point, text)
        self.text.setSize(24)
        self.text.setStyle('bold')
        
        self.draw()

    def draw(self):
        self.text.draw(self.canvas)

    def undraw(self):
        self.text.undraw()
