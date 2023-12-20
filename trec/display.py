import numpy as np       
import cv2                     
import time
import subprocess
import re
import os

from PyQt5.QtCore import QObject,QMutex,QWaitCondition,QThread,pyqtSignal
from PyQt5.QtGui import QPixmap,QIcon,QImage

class DisplayHandler(QObject):
    def __init__(self,gui,display_queue):
        super(self.__class__, self).__init__()
    
        self.display = Display(display_queue)
        self.display.updateImage.connect(gui.updateImage)
        self.display.updateStat.connect(gui.updateStat)
        self.display_thread = QThread()
        self.display.moveToThread(self.display_thread)
        
        self.display_thread.started.connect(self.display.loop)
        self.display_thread.start()

    def quitDisplay(self):
        self.display.QUIT()
        self.display_thread.quit()
        self.display_thread.wait()

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