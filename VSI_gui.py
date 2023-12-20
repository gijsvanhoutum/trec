
import platform
import sys
import time

import cv2
import numpy as np
import functools

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# ICONS at: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html#names

class Display(QObject):
    
    updateImage = pyqtSignal(QPixmap)
    updateStat = pyqtSignal(list)
    
    def __init__(self,data_queue):
        super(self.__class__, self).__init__()
        
        self.name = "Display"
        self.queue = data_queue
        self.clear()

    def clear(self):
        nr = 50
        self.disp_fps = np.zeros((2,nr))
        self.var = np.zeros(nr)
        
        l = len(self.disp_fps[0,:])
        self.disp_fps[0,:] = range(l)
        self.disp_fps[1,:].fill(0)
        self.var.fill(0)
        
    def QUIT(self):
        self.queue.put(None)
        
    def loop(self):
        while True:
            dtb = time.time()
            data = self.queue.get()   
            dta = time.time()
            
            if data is None:
                break
            
            if type(data[1]) == int:     
                rec_fps = data[0]
                que_s = str(data[1])
                rec_nr = str(data[2])
                stat = [[4,rec_fps],[5,rec_nr],[6,que_s]]
            else:
                disp_fps = self.updateFPS(self.name, self.disp_fps, dtb, dta)  
                q_image = self.toQImage(data[1]) 
                pixmap = QPixmap.fromImage(q_image.rgbSwapped())
                self.updateImage.emit(pixmap)
                var = self.updateVAR(data[1])
                cam_fps = data[0]
                stat = [[1,var],[2,cam_fps],[3,disp_fps]]
                
            self.updateStat.emit(stat)  
        
    def updateFPS(self,name,avg_list, time_before, time_after):
        mean_total = np.mean(np.diff(avg_list[0,:]))
        mean_max = np.mean(avg_list[0,1:]-avg_list[1,:-1])
        cur_fps = 1.0 / mean_total
        max_fps = 1.0 / mean_max
        percent = cur_fps / max_fps * 100
        avg_list[:,:-1] = avg_list[:,1:]
        avg_list[1,-1] = time_after
        avg_list[0,-1] = time_before

        return "%s: %05.1f fps (%05.1f %%)" % (name,cur_fps,percent)
    
    def updateVAR(self,np_image):
        s = np_image.shape
        cols = np.linspace(0,s[1],num=20,endpoint=False,dtype=int)
        mean_var = np.mean(self.var)           
        self.var[:-1] = self.var[1:]
        self.var[-1] = np.mean(np.var(np.diff(np_image[:,cols,:],axis=1),axis=1))
        
        return "VAR: %.0f" % (mean_var)
      
    def toQImage(self,im, copy=False):
        
        if isinstance(im,np.ndarray) is False:
            raise TypeError("Unsupported image data type %r" % (type(im)))

        shape = im.shape
        lng = len(shape)
        
        if lng not in (2, 3):
            raise NotImplementedError("Unsupported array shape %r" % lng)
        
        if im.dtype != np.uint8:
            im = im.astype(np.float64)
            im = (im - np.amin(im) ) / (np.amax(im) - np.amin(im) )*255
            im = im.astype(np.uint8)
            
        strides = im.strides[0]

        data = im.data
        
        if lng == 2:         
            fmt = QImage.Format_Indexed8
            qim = QImage(data, shape[1],shape[0],strides,fmt)
            qim.setColorTable(self.color_table)

        elif lng == 3:
            if shape[2] == 3:
                fmt =  QImage.Format_RGB888
                qim = QImage(data,shape[1],shape[0],strides,fmt)
                
            elif shape[2] == 4:
                fmt =  QImage.Format_ARGB32
                qim = QImage(data,shape[1],shape[0],strides,fmt)
                
        if copy:
            return qim.copy()
            
        return qim      
    
        
class Gui(QMainWindow):    
    
    opendevice = pyqtSignal(object,str,str)
    quitdevice = pyqtSignal()
    
    def __init__(self,data_queue,dev_clss,parent=None):
        super(self.__class__, self).__init__(parent)
        
        self.queue = data_queue
        
        self._createDockWidgets()
        self._createMenu(dev_clss)
        self._createStatusBar()       
        self.runDisplayThread()
        self.pixmap = None
        self.show()

    def _createDockWidgets(self):
        self.label = QLabel()
        self.label.setMinimumSize(1,1)
        self.label.installEventFilter(self)
        self.dock2 = DockWidget(self.label)
        self.dock2.close.connect(self.quitDevice)
        self.addDockWidget(Qt.RightDockWidgetArea,self.dock2)            
        self.setDockNestingEnabled(True)
        self.dock2.hide()
        
        self.toolbar = self.addToolBar("Device")
        self.toolbar.hide()

    def eventFilter(self,source,event):
        if source == self.label and event.type() == QEvent.Resize:
    
            if self.pixmap:
                self.pixmap = self.pixmap.scaled(self.label.size(),
                                                 Qt.KeepAspectRatio,
                                                 Qt.SmoothTransformation)
            
                self.label.setPixmap(self.pixmap)

        return super(QMainWindow,self).eventFilter(source,event)
        
    def _createMenu(self,dev_clss):
        self.menu = self.menuBar().addMenu("&Select Source")
        
        for dev_cls in dev_clss:
            name = dev_cls.getClassName()
            icon_str = dev_cls.getClassIcon()     
            name_paths = dev_cls.getPaths()
            
            if type(icon_str) == str and icon_str[-4:] == ".svg":
                icon = QIcon("./icons/%s" % icon_str)
                menu = self.menu.addMenu(icon,name)
            else:
                menu = self.menu.addMenu(name)           

            for name,path in name_paths:
                action = self.createAction(name)
                action.my_data = [dev_cls,name,path]
                action.triggered.connect(self.openDevice)  
                menu.addAction(action)
        
    def openDevice(self):
        data = self.sender().my_data
        self.opendevice.emit(*data)     
        self.dock2.setTitle(0,data[1])
        self.dock2.show()
        
    def quitDevice(self):
        self.quitdevice.emit()
        self.toolbar.clear()
        self.toolbar.hide()
        self.label.clear()

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

    def runDisplayThread(self):
        self.display = Display(self.queue)
        self.display.updateImage.connect(self.updateImage)
        self.display.updateStat.connect(self.updateStat)
        self.display_thread = QThread()
        self.display.moveToThread(self.display_thread)
        
        self.display_thread.started.connect(self.display.loop)
        self.display_thread.start()
        
    def quitDisplayThread(self):
        self.display.QUIT()
        self.display_thread.quit()
        self.display_thread.wait()
     
    def updateStat(self,stats):
        for s in stats:
            self.dock2.setTitle(*s)   
        
    def updateImage(self,pixmap):
        self.pixmap = pixmap.scaled(self.label.size(),
                                    Qt.KeepAspectRatio,
                                    Qt.SmoothTransformation)
        
        self.label.setPixmap(self.pixmap)
        
    def sizeHint(self):
        return QSize(640,480)
        
    def updateDevices(self):
        target = self.sender()
        data = target.my_data
        dev_cls = data[0]
        dev_menu = data[1]

        dev_menu.clear()

        for name_path in dev_cls.getPaths():
            action = self.createAction(name_path[0]) 
            dev_menu.addAction(action)      
            action.my_data = [*name_path,dev_cls]
            action.triggered.connect(self.openDevice)                        
            
    def createAction(self, text, icon=None,tip=None,shortcut=None):                         
        action = QAction(text, self)
        if icon is not None:
            if icon[-4:] == ".svg":
                ic = QIcon("./icons/%s" % icon)
                
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
                                  
    def _createStatusBar(self):
        self.sizeLabel = QLabel()
        self.sizeLabel.setFrameStyle(QFrame.StyledPanel|QFrame.Sunken)
        
        self.status = self.statusBar()
        self.status.setSizeGripEnabled(False)
        self.status.addPermanentWidget(self.sizeLabel)
        self.status.showMessage("Ready", 5000)

    def closeEvent(self,event):
        self.quitDisplayThread()
        self.quitdevice.emit()
        event.accept()

class DockWidget(QDockWidget):
    
    close = pyqtSignal()
    
    def __init__(self,widget):
        super(self.__class__, self).__init__()   
        self.setFloating(False)
        self.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.setWidget(widget) 
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
