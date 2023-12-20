import os
import struct

import cv2

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time
import numpy as np

class Recorder(QObject):
    
    def __init__(self,device_name, record_queue,display_queue,
                 mutex,wait):
        super(self.__class__, self).__init__()

        self.device_name = device_name
        self.record_queue= record_queue
        self.display_queue = display_queue
        
        self.mutex = mutex
        self.wait = wait
        
        self.codec = "Y800"
        self.ext = '.avi'
        self.save_dir = "/recordings/"
        self.file_dir = os.path.dirname(os.path.realpath(__file__))
        self.dir = self.file_dir+self.save_dir
        self.name = "Recorder"
        self.dev_name = device_name 
            
        nr = 50        
        
        self.fps = np.zeros((2,nr))
        self.save_name = ""

    def getGuiSpecs(self):
        r = [["Start Recording",self.START,"A",0,6,1,1,"rec.svg"],
             ["Stop Recording",self.STOP,"A",0,7,1,1,"stop-2.svg"],
             ["Save String",self.setString,"T",0,8,1,1,"Record Filename Add-on"]
             ]   

        return r           
          
    def setString(self,text):
        self.save_name = "_"+text

    def START(self,state):
        if not self.run:
            self.wait.wakeOne()
            while not self.run:
                time.sleep(0.01)
        
    def STOP(self,state):
        if self.run:
            self.record_queue.put([0,None,0])
            while self.run:
                time.sleep(0.01)
        
    def QUIT(self):
        self.quit = True
        self.START(0)
        self.STOP(0)  
        
    def setupWriter(self,source_name):
        with self.record_queue.mutex:
            self.record_queue.queue.clear()
               
        ta,image,fps = self.record_queue.get() 
        if image is None:
            return None
        
        channel = self.makeChannel(image,ta)
        shape = channel.shape
        fourcc = cv2.VideoWriter_fourcc(*self.codec)
        t = time.strftime("_D%Y-%m-%d_T%H%M%S%z")
        s = "_R"+str(shape[1])+"x"+str(shape[0])
        f = "_F"+str(fps)
        filename = self.dir+source_name+t+s+f+self.save_name+self.ext
        
        if shape[2] == 1:
            mode = False
        else:
            mode = True
            
        writer = cv2.VideoWriter(filename,fourcc,fps,(shape[1],shape[0]),mode)
        
        if writer.isOpened():
            return writer
        else:
            return None
        
    def loop(self):   
        self.clear()
        self.quit = False
        self.run = False
        while not self.quit:
            self.mutex.lock()
            self.wait.wait(self.mutex)
            self.mutex.unlock()  
            self.run = True  
            writer = self.setupWriter(self.dev_name)
            if writer:       
                nr = 1
                while True:
                    tb = time.time()
                    tia, image,fps = self.record_queue.get()  
                    if image is None:
                        break
                    
                    ta = time.time()           
                    s = self.record_queue.qsize()
                    
                    channel = self.makeChannel(image,tia)

                    writer.write(channel)
                    fps_str = self.updateFPS(self.name,self.fps,tb,ta)
                        
                    if not self.display_queue.full():
                        self.display_queue.put([fps_str,s,nr])  
                        
                    nr+=1
                    
                writer.release()
            
            self.run = False

    def makeChannel(self,image,epoch):
        s = image.shape
        channel = np.zeros((s[0],s[1]*s[2],1),dtype=np.uint8)
        channel[:,:,0] = np.hstack((image[:,:,0],image[:,:,1],image[:,:,2]))  
        channel[:8,0,0] = np.frombuffer(struct.pack("d",epoch),dtype=np.uint8)
 
        return channel
    
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
    
    def clear(self):
        l = len(self.fps[0,:])
        self.fps[0,:] = range(l)
        self.fps[1,:].fill(0)


class RecordHandler:
    def __init__(self,record_queue,display_queue):
        
        self.record_queue = record_queue
        self.display_queue = display_queue
        self.recorder = None
        
        self.mutex = QMutex()
        self.wait = QWaitCondition()

    def setRecorder(self,dev_name):
        self.recorder = Recorder(dev_name,
                                 self.record_queue,
                                 self.display_queue,
                                 self.mutex,
                                 self.wait)        
        
        self.thread = QThread()
        self.recorder.moveToThread(self.thread)       
        self.thread.started.connect(self.recorder.loop)
        self.thread.start()
        
    def quitRecorder(self):
        if self.recorder and self.thread.isRunning():
            self.recorder.QUIT()
            self.thread.quit()
            self.thread.wait()
        
    def getGuiSpecs(self):
        if self.recorder:
            return self.recorder.getGuiSpecs()
        else:
            return None
              