from PyQt4.QtCore import *
from PyQt4.QtGui import *

class TransformHandler(QObject):

    DataSignal = pyqtSignal(object) 

    def __init__(self,transform_classes, parent=None):
        super(self.__class__, self).__init__(parent)
 
        self.transform_classes = transform_classes
        
        self.transforms = []
    
    def getClassList(self):
        return self.transform_classes

    def getClassNames(self):
        return [t.getClassName() for t in self.transform_classes]
                     
    @pyqtSlot(object)
    def processData(self,frame):
        # APPLY TRANSFORMATIONS HERE
        for t in self.transforms:
            old_data = frame.getLastImage()
            data = t.transform(old_data)
            name = t.getName()

            frame.addData(data,name)

        # SEND THE UPDATED FRAME
        self.DataSignal.emit(frame)

        
    def addTransform(self,cls_name):
        transform = self.createTransform(cls_name)
        self.transforms.append(transform)   
        
    def createTransform(self,cls_name):
        for trf_cls in self.transform_classes:
            if trf_cls.getClassName() == cls_name:
                return trf_cls(cls_name)        
    
    def removeTransform(self,index):
        self.transforms.pop(index)
        
    def getTransforms(self):
        return [t.getName() for t in self.transform_classes]
    
    def quitTransforms(self):
        self.transforms = []
        
    def doCommand(self,cls_name,par_dict):
        for t in self.transforms:
            if t.getClassName() == cls_name:
                t.setParams(par_dict)

        
        
        