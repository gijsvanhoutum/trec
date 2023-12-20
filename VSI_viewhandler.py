from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import numpy as np

class ViewHandler(QSplitter):
    
    command = pyqtSignal(int)
    
    def __init__(self, view_cls, parent=None):
        super(self.__class__, self).__init__(parent)
    
        self.view_cls = view_cls
        self.paused = False

    def _createView(self,cls_name):
        for view_cls in self.view_classes:
            for name in view_cls.getClassNameList():
                if name == cls_name:
                    return view_cls(cls_name)
    
    def _createTabWidget(self):
        tabwidget = QTabWidget()      
        tabwidget.setTabsClosable(True)  
        tabwidget.tabCloseRequested.connect(self._removeView)    
        self.addWidget(tabwidget) 
        return tabwidget
    
    def _removeTabWidget(self,index):
        widget = self.widget(index)
        widget.hide()
        widget.deleteLater()
                       
    def _removeView(self,index):  
        nr_vw = self.widget(0).count()
        if nr_vw > 1:
            for idx in np.arange(self.count()):
                old = self.widget(idx)
                wg = old.widget(index)
                wg.hide()
                wg.deleteLater()
 
            self.command.emit(index)
        else:
            self.quitViews()
            self.command.emit(-1)
        
    def addView(self,cls_name):
        cnt = self.count()
        if cnt == 0:
            self._createTabWidget()        
            cnt+=1
            
        for idx in np.arange(cnt):
            view = self.view_cls(cls_name)
            tabw = self.widget(idx)
            tabw.addTab(view,cls_name) 
            
    def startViews(self):         
        self.paused = False
                
    def pauseViews(self):
        self.paused = True

    def quitViews(self):
        for i in np.arange(self.count()):
            self._removeTabWidget(i)

    def splitViews(self):
        tabwidget = self._createTabWidget()  
        
        tw = self.widget(0)
        for idx in np.arange(tw.count()):            
            name = tw.widget(idx).getName()
            copy_view = self._createView(name)
            tabwidget.addTab(copy_view,name)
     
        self.addWidget(tabwidget)
            
    def mergeViews(self):
        c = self.count()
        if c > 1:
            self._removeTabWidget(c-1)        
        
    def updateViews(self,frame):
        if not self.paused:
            image_dict = frame.getImages()
            for tw_idx in xrange(self.count()):
                tabwidget = self.widget(tw_idx)
                for vw_idx in xrange(tabwidget.count()):
                    view = tabwidget.widget(vw_idx)
                    name = view.getName()
                    data = image_dict[str(name)]
                    view.updateData(data)