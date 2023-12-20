from PyQt4.QtCore import *
from PyQt4.QtGui import *

class SettingHandler(QWidget):
    
    command = pyqtSignal(str,dict)
    
    def __init__(self, setting_classes, parent=None):
        super(self.__class__, self).__init__(parent)
         
        self.setting_classes = setting_classes
        
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignTop)
        self.setLayout(self.vbox) 
        
    def createSetting(self,cls_name):
        for setting_cls in self.setting_classes:
            if setting_cls.getClassName() == cls_name:
                return setting_cls(cls_name)        
        
    def addSetting(self,cls_name):
        setting = self.createSetting(cls_name)
        setting.command.connect(self.command.emit)
        self.vbox.addWidget(setting)

    
    def removeSetting(self,index):        
        item = self.vbox.takeAt(index)
        widget = item.widget()
        widget.hide()
        widget.deleteLater()
        
    def quitSettings(self):
        for box in self.findChildren(QGroupBox):
            box.hide()
            box.deleteLater()