# Python standard libraries
from stat import *             # for storage
from abc import abstractmethod # defining abstract methods

# Second party libraries
import numpy as np             # numerical C power library
import cv2                     #  OpenCV library

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import time
import subprocess
import re
import os
import struct

import pprint

class VideoRecord(QObject):
    
    __NAME__ = "Video"
    __ICON__ = "video.svg"
    __DIR__ = "/recordings/"
    
    finished = pyqtSignal()
    
    def __init__(self,filename,filepath,display_queue,record_queue,
                 mutex,wait,parent=None):
        super(self.__class__, self).__init__(parent)        
        
        self.display_queue = display_queue
        self.record_queue = record_queue     

        self.mutex = mutex
        self.wait = wait
        
        self.name = filename
        self.path = filepath
        self.reader = cv2.VideoCapture(filepath+filename)  
        
        nr = 20
        self.fps = np.zeros((2,nr))
        

    @classmethod
    def getPaths(cls):
        path = os.path.dirname(os.path.realpath(__file__))+cls.__DIR__
        files = os.listdir(path)
        return [[file,path] for file in files]

    @classmethod
    def getClassName(self):
        return self.__NAME__

    @classmethod        
    def getClassIcon(self):
        return self.__ICON__
    
    def getGuiSpecs(self):
        c = [["Start Device",self.START,"A",0,0,1,1,"play.svg"],
             ["Stop Device",self.STOP,"A",0,1,1,1,"stop.svg"],
             ]

        return c
        
    def START(self,state):
        if not self.run:
            self.wait.wakeOne()
            while not self.run:
                time.sleep(0.01)
        
    def STOP(self,state):
        if self.run:
            self.stop = True
            while self.run:
                time.sleep(0.01)

    def QUIT(self):
        self.quit = True
        self.START(0)
        self.STOP(0)
   
    def loop(self):
        self.clear()
        self.quit = False
        self.run = False
        while not self.quit:
            self.mutex.lock()
            self.wait.wait(self.mutex)
            self.mutex.unlock()
            self.run = True
            self.stop = False
            while not self.stop:
                tb = time.time()
                retval,image = self.reader.read()  
                ta = time.time()
                if retval:   
                    print(struct.unpack("d",image[:8,0,0].tobytes()))
                    fps_str = self.updateFPS(self.__NAME__,self.fps,tb,ta)
                    
                    if not self.display_queue.full():
                        self.display_queue.put([fps_str,image])  

                else:
                    self.reader.release()
                    self.reader = cv2.VideoCapture(self.path+self.name)  
                        
            self.run = False

        self.reader.release()

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
        
        
class CameraDevice(QObject):
    
    __NAME__ = "Camera"
    __ICON__ = "camera.svg"
    
    finished = pyqtSignal()
    
    def __init__(self,dev_name, dev_path,display_queue, record_queue,
                 mutex,wait,parent=None):
        super(self.__class__, self).__init__(parent)        
        
        self.display_queue = display_queue
        self.record_queue = record_queue     

        self.mutex = mutex
        self.wait = wait

        self.dev_name = dev_name
        self.dev_path = dev_path
        self.reader = cv2.VideoCapture(dev_path)         
        self.cap_fmts = self.getFFF(dev_path)
        self.list_fmts = sorted(list(self.cap_fmts.keys()))
        self.setReader(0)
        nr = 20
        self.fps = np.zeros((2,nr))
        

    @classmethod
    def getPaths(cls):
        paths = []
        command = "v4l2-ctl --list-devices"
        df = subprocess.check_output(command,shell=True).decode()
        for device in df.split("\n\n")[:-1]:
            spl = re.split("\(|\n\t|\n\n",device)
            name = spl[0].strip()
            path = spl[2].strip()
            paths.append([name,path])

        return paths

    @classmethod
    def getClassName(self):
        return self.__NAME__

    @classmethod        
    def getClassIcon(self):
        return self.__ICON__
    
    def getGuiSpecs(self):
        c = [["Start Device",self.START,"A",0,0,1,1,"play.svg"],
             ["Stop Device",self.STOP,"A",0,1,1,1,"stop.svg"],
             ["Format - Size - FPS",self.setFFF,"C",0,3,1,1,self.list_fmts],

             ]

        if self.dev_name == "Dino-Lite Edge":
            self.led = True
            c.append(["LED Off/On",self.toggleLED,"A",0,0,1,1,"semibreve.svg"])
        
        return c
        
    def toggleLED(self,state):
        if self.led:
            subprocess.call(["uvcdynctrl", "-d", self.dev_path, "-S", "4:2", "f2000000000000"])
            self.led = False
        else:
            subprocess.call(["uvcdynctrl", "-d", self.dev_path, "-S", "4:2", "f2010000000000"])
            self.led = True
            
    def START(self,state):
        if not self.run:
            self.wait.wakeOne()
            while not self.run:
                time.sleep(0.01)
        
    def STOP(self,state):
        if self.run:
            self.stop = True
            while self.run:
                time.sleep(0.01)

    def QUIT(self):
        self.quit = True
        self.START(0)
        self.STOP(0)
        
    def setReader(self,index):
        key = self.list_fmts[index]
        fourcc,width,height,fps = self.cap_fmts[key]
        self.reader.set(3,width) 
        self.reader.set(4,height) 
        fourcc = cv2.VideoWriter.fourcc(*fourcc)
        self.reader.set(cv2.CAP_PROP_FOURCC,fourcc) 
        self.reader.set(cv2.CAP_PROP_FPS,fps)
        self.FPS = fps        
        
    def setFFF(self,index):   
        self.STOP(0)
        # change settings           
        self.setReader(index)
        # start again
        self.START(0)
        
    def getFFF(self,path):
        FFFS = {}
        
        formats = self.getFormats(path)
        
        for fourcc in formats:
            sizes = self.getFramesizes(path,fourcc)
            
            for width,height in sizes:
                fpss = self.getFPS(width,height,path,fourcc)
                
                for fps in fpss:
                    string = "%4s - %4s x %4s - %4s" % (fourcc,width,height,fps)
                    FFFS[string] = [fourcc,int(width),int(height),int(fps)]
                    
        return FFFS

    def getFormats(self, path):
        command = "v4l2-ctl --device="+path+" --list-formats"
        fs = subprocess.check_output(command,shell=True).decode()     
        return [f for f in fs.split("'") if len(f) == 4]

    def getFramesizes(self, path, fourcc):
        command = "v4l2-ctl --device="+path+" --list-framesizes="+fourcc
        fs = subprocess.check_output(command,shell=True).decode()
        sizes = [x.split("\n")[0] for x in fs.split("\tSize: Discrete ")[1:]]
        return [x.split("x") for x in sizes]

    def getFPS(self, width, height, path, fourcc):
        command1 = "v4l2-ctl --device="+path+" --list-frameintervals="
        command2 = "width="+width+",height="+height+",pixelformat="+fourcc         
        fs = subprocess.check_output(command1+command2,shell=True).decode()
        return [x.split(".")[0] for x in fs.split("(")[1:]]
   
    def loop(self):
        self.clear()
        self.quit = False
        self.run = False
        while not self.quit:
            self.mutex.lock()
            self.wait.wait(self.mutex)
            self.mutex.unlock()
            self.run = True
            self.stop = False
            while not self.stop:
                tb = time.time()
                retval,image = self.reader.read()  
                ta = time.time()
                if retval:   
                    fps_str = self.updateFPS(self.__NAME__,self.fps,tb,ta)
                    
                    if not self.display_queue.full():
                        self.display_queue.put([fps_str,image])  
                        
                    if not self.record_queue.full():
                        self.record_queue.put([ta,image,self.FPS])
                        
            self.run = False

        self.reader.release()

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
        
