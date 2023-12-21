import sys
import queue

from PyQt5.QtCore import QObject,pyqtSlot
from PyQt5.QtWidgets import QApplication

from gui import Gui
from record import RecordHandler
from device import DeviceHandler,CameraDevice,VideoRecord
from display import DisplayHandler

MAX_Q = 5

class TREC(QObject):    
    """
    TREC: Video playing and recording.

    This GUI application enables camera capturing and recording of all devices 
    supported by Video4Linux (V4L2) device drivers. Multiple resolutions and 
    codecs can be chosen for capturing. Multiple threads enable a responsive GUI
    and minimizes latency for capturing, recording and displaying.
    """
    def __init__(self):                             
        super(self.__class__,self).__init__()        
        """
        Creates queues, thread handlers and connects them.
        """
        # Queue pushed by Device, popped by Display
        self.display_queue = queue.Queue(maxsize=MAX_Q)
        # Queue pushed by Device, popped by Recorder
        self.record_queue = queue.Queue(maxsize=MAX_Q)
        # Devices. Can be expanded by adding new device created in device.py
        self.devices = [CameraDevice, VideoRecord]  
        # Thread handlers for GUI,display,device,record
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
        # Connect GUI signals with slots. 
        self.gui.opendevice.connect(self._openDevice)
        self.gui.quitdevice.connect(self._quitDevice)
        self.gui.quitapp.connect(self._quitApp)
        
    @pyqtSlot(object,str,str)
    def _openDevice(self,dev_cls,name,path):
        """
        Slot initiated by GUI to open a new device.
        
        Args:
            dev_cls: (QObject) The device class to be initiated.
            name: (str) The name of the device.
            path: (str) Path to device
        """
        # Close device that is opened first, if any
        self.gui.quitDevice()
        # Start new device in new thread 
        self.device_h.setDevice(dev_cls,name,path)
        # Get/Set all widget specs for creating device specific GUI widgets
        self.gui.addActions(self.device_h.getGuiSpecs())     
        # Camera devices can be recorded, VideoDevices cannot
        if dev_cls == CameraDevice:
            self.record_h.setRecorder(name)  
            self.gui.addActions(self.record_h.getGuiSpecs())
        
    @pyqtSlot()
    def _quitDevice(self):

        """
        Creates queues, thread handlers and connects them.

        Args:
            big_table: An open Bigtable Table instance.
            keys: A sequence of strings representing the key of each table row
                to fetch.
            other_silly_variable: Another optional variable, that has a much
                longer name than the other args, and which does nothing.

        Returns:
            A dict mapping keys to the corresponding table row data
            fetched. Each row is represented as a tuple of strings. For
            example:

            {'Serak': ('Rigel VII', 'Preparer'),
             'Zim': ('Irk', 'Invader'),
             'Lrrr': ('Omicron Persei 8', 'Emperor')}

            If a key from the keys argument is missing from the dictionary,
            then that row was not found in the table.

        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        self.record_h.quitRecorder()
        self.device_h.quitDevice()

    @pyqtSlot()
    def _quitApp(self):

        """
        Creates queues, thread handlers and connects them.

        Args:
            big_table: An open Bigtable Table instance.
            keys: A sequence of strings representing the key of each table row
                to fetch.
            other_silly_variable: Another optional variable, that has a much
                longer name than the other args, and which does nothing.

        Returns:
            A dict mapping keys to the corresponding table row data
            fetched. Each row is represented as a tuple of strings. For
            example:

            {'Serak': ('Rigel VII', 'Preparer'),
             'Zim': ('Irk', 'Invader'),
             'Lrrr': ('Omicron Persei 8', 'Emperor')}

            If a key from the keys argument is missing from the dictionary,
            then that row was not found in the table.

        Raises:
            IOError: An error occurred accessing the bigtable.Table object.
        """
        self._quitDevice()
        self.display_h.quitDisplay()

if __name__ == '__main__':
    app = QApplication(sys.argv)   
    gui = TREC()
    sys.exit(app.exec_())
    