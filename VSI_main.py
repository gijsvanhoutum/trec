# To access shell arguments given at application startup
import sys
import queue

# Gui library components
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# Home made modules
from VSI_gui import Gui
from VSI_recordhandler import RecordHandler
from VSI_devicehandler import DeviceHandler
from VSI_device import CameraDevice,VideoRecord


class Model(QObject):    
    def __init__(self,gui,recordhandler,devicehandler,devices):                             
        super(self.__class__,self).__init__()        

        self.display_queue = queue.Queue(maxsize=5)
        self.record_queue = queue.Queue(maxsize=5)
        
        self.device_h = devicehandler(self.display_queue,
                                      self.record_queue,
                                      devices)

        self.gui = gui(self.display_queue, devices)
        
        self.record_h = recordhandler(self.record_queue,
                                      self.display_queue)

        self.gui.opendevice.connect(self._openDevice)
        self.gui.quitdevice.connect(self._quitDevice)
 
    @pyqtSlot(object,str,str)
    def _openDevice(self,dev_cls,name,path):
        self.device_h.setDevice(dev_cls,name,path)
        dev_specs = self.device_h.getGuiSpecs()
        self.gui.addActions(dev_specs)     
        
        if dev_cls == CameraDevice:
            self.record_h.setRecorder(name)  
            rec_specs = self.record_h.getGuiSpecs()
            self.gui.addActions(rec_specs)
        
    @pyqtSlot()
    def _quitDevice(self):
        self.record_h.quitRecorder()
        self.device_h.quitDevice()

   
if __name__ == '__main__':
    a = QApplication(sys.argv)   
    Devices = [CameraDevice, VideoRecord]
    p = Model(Gui,RecordHandler,DeviceHandler,Devices)
    a.exec_()
    