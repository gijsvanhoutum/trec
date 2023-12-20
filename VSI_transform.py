from abc import ABCMeta,abstractmethod
import cv2
import numpy as np

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from VSI_metaclass import MetaClass

import sys

class Transformation:
    __metaclass__ = ABCMeta
    
    """ 
    This class is a Abstract Base Class (Interface) for a transformation.
    
    It should be reimplemented with the methods below.
    """ 
    
    @classmethod
    def getName(self):
        return self.__NAME__
    
    @abstractmethod    
    def transform(self,image):
        """
        This method takes a image and applies
        the transformation to the image
        """
        
class ColorTransform(Transformation):
    
    __INST__ = 0
    __NAME__ = "Color Threshold"
    
    def __init__(self,name):
        self.__class__.__INST__  +=1
        
        self.name = name
        
        self.low = np.array([160,100,100])
        self.high = np.array([10,255,255])
        self.return_mask = False
        
    def getName(self):
        return self.name
        
    @classmethod        
    def getClassName(self):
        return self.__NAME__
        
    def transform(self,old_image):
        hsv_image = cv2.cvtColor(old_image,cv2.COLOR_RGB2HSV)
        mask = self.maskImage(hsv_image)

        if self.return_mask:
            res = mask
        else:
            res = cv2.bitwise_and(old_image,old_image, mask=mask)
            
        pass_data = res
        show_data = res
        
        return [show_data,pass_data]
    
    def maskImage(self,image):
        if self.low[0] > self.high[0]:
            high = np.array([179,self.high[1],self.high[2]])
            low = np.array([0,self.low[1],self.low[2]])

            mask1 = cv2.inRange(image,self.low,high)                    
            mask2 = cv2.inRange(image,low,self.high)  
            mask = cv2.addWeighted(mask1,1.0,mask2,1.0,0.0)    
        else:
            mask = cv2.inRange(image,self.low,self.high) 
            
        return mask
            
    def setParams(self,par_dict):
        name = par_dict.keys()[0]
        value = par_dict.values()[0]
        print name,value
        if name == "hmin":
            self.low[0] = value
        elif name == "hmax":
            self.high[0] = value
        elif name == "smin":
            self.low[1] = value
        elif name == "smax":
            self.high[1] = value
        elif name == "vmin":
            self.low[2] = value
        elif name == "vmax":
            self.high[2] = value
        elif name == "check":
            self.return_mask = value
            print self.return_mask
            
          
class PixelDensity(Transformation):
    
    __INST__ = 0
    __NAME__ = "Pixel Density"
    
    def __init__(self,name):
        self.__class__.__INST__  +=1
        
        self.name = name        
        
    def getName(self):
        return self.name
        
    @classmethod        
    def getClassName(self):
        return self.__NAME__
        
    def transform(self,old_image):
        shape = old_image.shape
        ones = np.ones((shape[1],1))
    
        rown = np.dot(old_image,ones)/(float(shape[1])*255)

        row = self.diff(rown,periods=[100])

        mx = np.argmax(row)
        mn = np.argmin(row)
        if mx > mn:
            new_array = old_image[mn:mx,:]
        elif mn > mx:
            new_array = old_image[mx:mn,:]            

        blur = cv2.medianBlur(new_array,9)
        coln = np.dot(np.transpose(new_array),ones[:new_array.shape[0]])
        col = self.diff(coln,periods=[25])
        return [row,col]
    
    def diff(self,ts,periods=[1]):
        diffed = ts
        for period in periods:
            diffed = (diffed - np.roll(diffed,period))[period:]
        
        return diffed       
        
    def setParams(self,par_dict):
        pass

class MaxValue(Transformation):
    
    __INST__ = 0
    __NAME__ = "Max Value"
    
    def __init__(self,name):
        self.__class__.__INST__  +=1
        
        self.name = name        
        
    def getName(self):
        return self.name
        
    @classmethod        
    def getClassName(self):
        return self.__NAME__
        
    def transform(self,width_height):            
        return [width_height,width_height]
           
    def setParams(self,par_dict):
        pass
    
class JoshAlgorithm(Transformation):
    
    __INST__ = 0
    __NAME__ = "Josh Algorithm"
    
    def __init__(self,name):
        self.__class__.__INST__  +=1
        
        self.name = name
        
        self.low = np.array([160,100,100])
        self.high = np.array([10,255,255])
        self.hor_ped = 1
        self.ver_ped = 1
        
    def getName(self):
        return self.name
        
    @classmethod        
    def getClassName(self):
        return self.__NAME__
        
    def transform(self,old_image):
        if len(old_image.shape) > 2:
            gray = cv2.cvtColor(old_image,cv2.COLOR_RGB2GRAY)
        else:
            gray = np.copy(old_image)

        out1 = self.detLine(gray,[self.hor_ped])
        wdt1 = out1[1] - out1[0]
        ctr1 = out1[0] + wdt1/2
        wdt_set1 = 100
        adj1 = [ctr1-wdt_set1,ctr1+wdt_set1]
        new1 = np.transpose(gray[adj1[0]:adj1[1],:])
        
        out2 = self.detLine(new1,[self.ver_ped]) 
        wdt2 = out2[1] - out2[0]
        ctr2 = out2[0] + wdt2/2
        wdt_set2 = 100
        adj2 = [ctr2-wdt_set2,ctr2+wdt_set2]
        new2 = gray[:,adj2[0]:adj2[1]]
        
        out3 = self.detLine(new2,0)         
        new_image = np.copy(old_image)
        
        if len(old_image.shape) > 2:
            blue = np.array([0,0,255])
            green = np.array([0,255,0])
        else:
            blue = 0
            green = blue
            
        new_image[out1[0]-10:out1[0],:] = blue
        new_image[out1[1]:out1[1]+10,:] = blue
        
        new_image[adj1[0]-10:adj1[0],:] = green
        new_image[adj1[1]:adj1[1]+10,:] = green
        
        new_image[:,out2[0]-10:out2[0]] = blue
        new_image[:,out2[1]:out2[1]+10] = blue          
        
        new_image[:,adj2[0]-10:adj2[0]] = green
        new_image[:,adj2[1]:adj2[1]+10] = green
        
        new_image[out3[0]:out3[0]+10,:] = blue  
             
        
        width = out2[1]-out2[0]
        height = out3[0] #- (out1[1]-out1[0])
        
        pass_data = [width,height]
        show_data = new_image
        
        return [show_data,pass_data]
    
    def detLine(self,image,period):
        rown = self.white_number(image)
        
        if period:
            row = self.central_diff(rown,periods=period)
        else:
            row = rown
            
        max_min = self.max_min(row,period)
        return max_min
    
    def max_min(self,row,period):
        mx = np.argmax(row)+period
        mn = np.argmin(row)+period

        if mx > mn:
            return [mn,mx]
        elif mn > mx:
            return [mx,mn]        
                
    def white_number(self,image):
        shape = image.shape
        ones = np.ones((shape[1],1))  
        rown = np.dot(image,ones)/(float(shape[1])*255)
        return rown        
    
    def central_diff(self,ts,periods=[1]):
        diffed = ts
        for period in periods:
            diffed = (np.roll(diffed,-period) - np.roll(diffed,period))[period:-period]
        
        return diffed 
            
    def setParams(self,par_dict):
        name = par_dict.keys()[0]
        value = par_dict.values()[0]
        print name,value
        if name == "dhor":
            self.hor_ped = value
        elif name == "dver":
            self.ver_ped = value