from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ColorSetting(QGroupBox):
        
    __NAME__ = "Color Threshold"
    
    command = pyqtSignal(str,dict)
                
    def __init__(self,name,parent=None):
        super(self.__class__, self).__init__(parent)        

        self.setTitle(name)
        policy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)                           
        self.setSizePolicy(policy)
        
        self.label1 = QLabel("Hue")
        self.label2 = QLabel("Saturation")
        self.label3 = QLabel("Value")       
        self.label7 = QLabel("Min")
        self.label8 = QLabel("Max")
        
        self.sbox = {}
        self.sbox["hmin"] = QSpinBox()
        self.sbox["hmin"].setMaximum(179)
        self.sbox["hmin"].setValue(160)
        self.sbox["hmax"] = QSpinBox()
        self.sbox["hmax"].setMaximum(179)
        self.sbox["hmax"].setValue(10)
        
        self.sbox["smin"] = QSpinBox()
        self.sbox["smin"].setMaximum(255)
        self.sbox["smin"].setValue(100)
        self.sbox["smax"] = QSpinBox()
        self.sbox["smax"].setMaximum(255)
        self.sbox["smax"].setValue(255)
        
        self.sbox["vmin"] = QSpinBox()
        self.sbox["vmin"].setMaximum(255)
        self.sbox["vmin"].setValue(100)
        self.sbox["vmax"] = QSpinBox()
        self.sbox["vmax"].setMaximum(255)
        self.sbox["vmax"].setValue(255)
        
        self.label9 = QLabel("Use Mask")
        self.cbox = QCheckBox()
                
        self.grid1 = QGridLayout()

        self.grid1.addWidget(self.label7,0,1)
        self.grid1.addWidget(self.label8,0,2)
        self.grid1.addWidget(self.label1,1,0)
        self.grid1.addWidget(self.label2,2,0)
        self.grid1.addWidget(self.label3,3,0)
        
        self.grid1.addWidget(self.sbox["hmin"],1,1)
        self.grid1.addWidget(self.sbox["hmax"],1,2)
        self.grid1.addWidget(self.sbox["smin"],2,1)
        self.grid1.addWidget(self.sbox["smax"],2,2)
        self.grid1.addWidget(self.sbox["vmin"],3,1)
        self.grid1.addWidget(self.sbox["vmax"],3,2)
        
        self.grid1.addWidget(self.label9,4,0)
        self.grid1.addWidget(self.cbox,4,1)
        
        self.setLayout(self.grid1)
        
        self._connectSignals()

    def masked(self,value):
        if value == Qt.Checked:
            self.sendCommand(1,"check")
        elif value == Qt.Unchecked:
            self.sendCommand(0,"check")
        
    def _connectSignals(self):
        for box_key in self.sbox:
            l = lambda value,b=box_key : self.sendCommand(value,b)
            self.sbox[box_key].valueChanged.connect(l)
        
        self.cbox.stateChanged.connect(self.masked)                    

    @pyqtSlot(int,str)
    def sendCommand(self,value,box_key):
        d = {box_key : value}      
        self.command.emit(self.__NAME__,d)
        
    @classmethod
    def getClassName(self):
        return self.__NAME__
        
class CameraSetting(QGroupBox):
    
    __NAME__ = "Camera"
    
    command = pyqtSignal(str,dict)
    
    def __init__(self, name,parent=None):
        super(self.__class__, self).__init__(parent)

        self.setTitle(name)
        policy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)                           
        self.setSizePolicy(policy)
        
        self.label1 = QLabel("FPS")
        self.sbox = QSpinBox()
        self.sbox.setValue(10)        
        self.grid = QGridLayout()
        self.grid.addWidget(self.label1,0,0)
        self.grid.addWidget(self.sbox,0,1)
        self.setLayout(self.grid)  
        
        self.connectSignals()
            
    def connectSignals(self):
        self.sbox.valueChanged.connect(self.sendCommand)
        
    def sendCommand(self,fps):
        interval = 1000/fps       
        d = {"FPS": interval}
        self.command.emit(self.__NAME__,d)

    @classmethod
    def getClassName(self):
        return self.__NAME__
        
class VideoSetting(QGroupBox):
    
    __NAME__ = "Video"
    
    command = pyqtSignal(str,dict)
    
    def __init__(self, name,parent=None):
        super(self.__class__, self).__init__(parent)

        self.setTitle(name)
        policy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)                           
        self.setSizePolicy(policy)
        
        self.label1 = QLabel("Speed (FPS)")
        self.label2 = QLabel("Use Original")
        self.sbox = QSpinBox()
        self.cbox = QCheckBox()
        self.sbox.setValue(10)
        self.grid = QGridLayout()
        self.grid.addWidget(self.label1,0,0)
        self.grid.addWidget(self.sbox,0,1)
        self.grid.addWidget(self.label2,1,0)
        self.grid.addWidget(self.cbox,1,1)
        self.setLayout(self.grid)  
              
        self.connectSignals()
    
    def hideFPS(self,value):
        if value == Qt.Checked:
            check = False
            self.sendCommand("original")
        elif value == Qt.Unchecked:
            check = True
            self.sendCommand(self.sbox.value())
            
        self.label1.setEnabled(check)
        self.sbox.setEnabled(check)
        
    def connectSignals(self):
        self.sendCommand(self.sbox.value())
        self.cbox.stateChanged.connect(self.hideFPS)
        self.sbox.valueChanged.connect(self.sendCommand)
        
    def sendCommand(self,fps):
        d = {"FPS": fps}
        self.command.emit(self.__NAME__,d)

    @classmethod
    def getClassName(self):
        return self.__NAME__
        
class PixelSetting(QGroupBox):
    
    __NAME__ = "Pixel Density"
    
    command = pyqtSignal(str,dict)
    
    def __init__(self, name,parent=None):
        super(self.__class__, self).__init__(parent)

        self.setTitle(name)
        policy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)                           
        self.setSizePolicy(policy)
        
        self.label1 = QLabel("No Settings")

        self.grid = QGridLayout()
        self.grid.addWidget(self.label1,0,0)
        self.setLayout(self.grid)  
        
    def sendCommand(self):
        pass

    @classmethod
    def getClassName(self):
        return self.__NAME__
        
class ValueSetting(QGroupBox):
    
    __NAME__ = "Max Value"
    
    command = pyqtSignal(str,dict)
    
    def __init__(self, name,parent=None):
        super(self.__class__, self).__init__(parent)

        self.setTitle(name)
        policy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)                           
        self.setSizePolicy(policy)
        
        self.label1 = QLabel("No Settings")

        self.grid = QGridLayout()
        self.grid.addWidget(self.label1,0,0)
        self.setLayout(self.grid)  
        
    def sendCommand(self):
        pass

    @classmethod
    def getClassName(self):
        return self.__NAME__
        
class JoshSetting(QGroupBox):
        
    __NAME__ = "Josh Algorithm"
    
    command = pyqtSignal(str,dict)
                
    def __init__(self,name,parent=None):
        super(self.__class__, self).__init__(parent)        

        self.setTitle(name)
        policy = QSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)                           
        self.setSizePolicy(policy)
        
        self.label1 = QLabel("Diff Period")
        self.label2 = QLabel("Hori")
        self.label3 = QLabel("Vert")       
        
        self.sbox = {}
        self.sbox["dhor"] = QSpinBox()
        self.sbox["dhor"].setMaximum(200)
        self.sbox["dver"] = QSpinBox()
        self.sbox["dver"].setMaximum(200)

        self.grid1 = QGridLayout()

        self.grid1.addWidget(self.label2,0,1)
        self.grid1.addWidget(self.label3,0,2)
        self.grid1.addWidget(self.label1,1,0)
        
        self.grid1.addWidget(self.sbox["dhor"],1,1)
        self.grid1.addWidget(self.sbox["dver"],1,2)
        
        self.setLayout(self.grid1)
        
        self._connectSignals()

    def masked(self,value):
        if value == Qt.Checked:
            self.sendCommand(1,"check")
        elif value == Qt.Unchecked:
            self.sendCommand(0,"check")
        
    def _connectSignals(self):
        for box_key in self.sbox:
            l = lambda value,b=box_key : self.sendCommand(value,b)
            self.sbox[box_key].valueChanged.connect(l)                 

    @pyqtSlot(int,str)
    def sendCommand(self,value,box_key):
        d = {box_key : value}      
        self.command.emit(self.__NAME__,d)
        
    @classmethod
    def getClassName(self):
        return self.__NAME__