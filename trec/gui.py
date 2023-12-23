from PyQt5.QtCore import QObject,Qt,QEvent,QSize,pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QMainWindow,
    QDockWidget,
    QLabel,
    QSizePolicy,
    QAction,
    QFrame,
    QComboBox,
    QLineEdit,
    QMenu
)

    
class Gui(QMainWindow):    
    """
    The GUI window
    """
    opendevice = pyqtSignal(object,str,str)
    quitdevice = pyqtSignal()
    quitapp = pyqtSignal()
    
    __ICON_DIR__ = "../icons/"
        
    def __init__(self,dev_clss):
        super(self.__class__, self).__init__()
        """
        Constructor
        
        Args:
            dev_clss: (QObject) Available device classes to be initiated.
        """
        # Create the main docking widget
        self._createDockWidgets()
        # Create and populate menu with all available device classes
        self._createMenu(dev_clss)
        # Status bar to display system state info
        self._createStatusBar()       
        
        self.show()

    def _createDockWidgets(self):
        """
        Create DockingWidget with Label, Toolbar for buttons etc. and hide them
        """
        # Create Dockwidget holding the device image and widgets
        self.dock2 = DockWidget()
        self.dock2.close.connect(self.quitDevice)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dock2)            
        self.setDockNestingEnabled(True)
        # Create toolbar that will hold all widgets related to each device
        self.toolbar = self.addToolBar("Device")
        # Hide the dock and toolbar widget since there is no device initially
        self.dock2.hide()
        self.toolbar.hide()
        
    def _createMenu(self,dev_clss):
        """
        Creates the Menubar and all available devices
        
        TODO: 
        - Dynamically update menubar. Just recorded videos are not seen and
        the applications needs be restarted to see them.
        """
        self.menu = self.menuBar().addMenu("&Select Source")
        
        for dev_cls in dev_clss:
            # add classname to menu
            icon = QIcon(self.__ICON_DIR__+"%s" % dev_cls.getClassIcon())
            menu = self.menu.addMenu(icon,dev_cls.getClassName())      
            
            # for every available device in each class add action
            for name,path in dev_cls.getPaths():
                action = self.createAction(name)
                action.my_data = [dev_cls,name,path]
                action.triggered.connect(self.openDevice)  
                menu.addAction(action)
        
    def _createStatusBar(self):
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)
        self.status.addPermanentWidget(self.sizeLabel)
        self.status.showMessage("Ready", 5000)
        
    def createAction(self, text, icon=None,tip=None,shortcut=None):                         
        action = QAction(text, self)
        if icon is not None:
            if icon[-4:] == ".svg":
                ic = QIcon(self.__ICON_DIR__+"%s" % icon)
                
            action.setIcon(ic)
            
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        else:
            action.setToolTip(text)
            action.setStatusTip(text)

        return action
    
    def openDevice(self):
        data = self.sender().my_data
        self.opendevice.emit(*data)     
        self.dock2.setTitle(0,data[1])
        self.dock2.show()
        
    def quitDevice(self):
        self.quitdevice.emit()
        self.toolbar.clear()
        self.toolbar.hide()
        self.dock2.clear()

    def addActions(self,specs):
        self.toolbar.show()
        
        if specs is not None:
            for spec in specs:
                title = spec[0]
                func = spec[1]
                sort = spec[2]
                
                if sort == "A":
                    icon = spec[-1]
                    action = self.createAction(title,icon=icon)
                    action.my_data = func
                    action.triggered.connect(self.doCommand)
                    self.toolbar.addAction(action) 
                elif sort == "C":
                    items = spec[-1]
                    widget = QComboBox()
                    widget.addItems(items)
                    widget.my_data = func
                    widget.currentIndexChanged.connect(self.doCommand)
                    self.toolbar.addWidget(widget)
                elif sort == "T":
                    widget = QLineEdit()
                    widget.setText(spec[-1])
                    widget.my_data = func
                    l = lambda: self.doCommand(widget.text())
                    widget.textChanged.connect(l)
                    self.toolbar.addWidget(widget)
            
    def doCommand(self,data):
        self.sender().my_data(data)

    def updateStat(self,stats):
        self.dock2.updateStat(stats)
        
    def updateImage(self,pixmap):
        self.dock2.updateImage(pixmap)
        
    def sizeHint(self):
        return QSize(640,480)                      
                    
    def closeEvent(self,event):
        self.quitapp.emit()
        event.accept()

class DockWidget(QDockWidget):
    
    close = pyqtSignal()
    
    def __init__(self):
        super(self.__class__, self).__init__()   
        
        self.label = QLabel()
        self.label.setMinimumSize(1,1)
        self.setWidget(self.label) 
        
        self.setFloating(False)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)

        self.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        self.default_title = None
        
        self.title_list = []
        self.s = " || "
        
    def setTitle(self,index,title):
        if len(self.title_list) <= index:
            self.title_list+=[" - "] * (index+1)
        
        self.title_list[index] = title            
        self.setWindowTitle(self.s.join(self.title_list))
        
    def closeEvent(self,event):
        self.close.emit()
        event.accept()
        
    def updateStat(self,stats):
        for s in stats:
            self.setTitle(*s)   
        
    def updateImage(self,pixmap):
        pixmap = pixmap.scaled(
            self.label.size(),
            Qt.KeepAspectRatio,Qt.SmoothTransformation
        )
        self.label.setPixmap(pixmap)
        
    def clear(self):
        self.label.clear()
        
