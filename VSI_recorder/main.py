import sys
import queue

from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5.QtWidgets import QApplication

from gui import Gui
from record import RecordHandler
from device import DeviceHandler,CameraDevice,VideoRecord
from display import DisplayHandler

MAX_Q = 5

class Model(QObject):    
    def __init__(self):                             
        super(self.__class__,self).__init__()        

        self.display_queue = queue.Queue(maxsize=MAX_Q)
        self.record_queue = queue.Queue(maxsize=MAX_Q)
        
        self.devices = [CameraDevice, VideoRecord]  

        self.gui = Gui(
            self.display_queue, 
            self.devices
        )
        self.display_h = DisplayHandler(
            self.gui,
            self.display_queue,
        )
        self.device_h = DeviceHandler(
            self.display_queue,
            self.record_queue,
            self.devices
        )
        self.record_h = RecordHandler(
            self.record_queue,
            self.display_queue
        )
        
        self.gui.opendevice.connect(self._openDevice)
        self.gui.quitdevice.connect(self._quitDevice)
        self.gui.quitapp.connect(self._quitapp)
        
    @pyqtSlot(object,str,str)
    def _openDevice(self,dev_cls,name,path):
        self.gui.quitDevice()
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

    @pyqtSlot()
    def _quitapp(self):
        self._quitDevice()
        self.display_h.quitDisplay()

if __name__ == '__main__':
    app = QApplication(sys.argv)   
    gui = Model()
    sys.exit(app.exec_())
    