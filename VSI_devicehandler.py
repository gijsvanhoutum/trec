from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class DeviceHandler(QObject):
    def __init__(self,display_queue, record_queue, device_classes,parent=None):
        super(self.__class__, self).__init__(parent)
    
        self.display_queue = display_queue
        self.record_queue = record_queue        
        self.device_classes = device_classes        
        self.device = None 
        self.mutex = QMutex()
        self.wait = QWaitCondition()

    def getClassList(self):
        return self.device_classes

    def setDevice(self,dev_cls,name,path):
        self.device = dev_cls(name,path,
                               self.display_queue,
                               self.record_queue,
                               self.mutex,
                               self.wait)
        
        self.thread = QThread()
        self.device.moveToThread(self.thread)  
        self.thread.started.connect(self.device.loop)
        self.thread.start()
        
    def quitDevice(self):
        if self.thread.isRunning():
            self.device.QUIT()
            self.thread.quit()
            self.thread.wait()
        
        
    def getGuiSpecs(self):
        if self.device:
            return self.device.getGuiSpecs()
        else:
            return None

            