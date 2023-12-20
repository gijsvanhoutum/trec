from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from qwt import *

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from matplotlib import cm

import random

class View(QWidget): 
    
    def __init__(self,name,specs, parent=None):
        super(self.__class__, self).__init__(parent)

        self.name = name      
        self.specs = specs
        self.colors = self._setColors()
        self.grid = self._setGrid()
        self.plots = self._setPlots(self.grid)  
        
        self._setAxesWidth(QwtPlot.yLeft,70)
     
    def _getMaxAxesWidth(self,axes):
        max_extent = 0
        
        for p in self.plots:
            sw = p.axisWidget(axes)
            sd = sw.scaleDraw()
            sd.setMinimumExtent(0)
            extent = sd.extent(sw.font())

            if extent > max_extent:
                max_extent = extent
            
        return max_extent
        
    def _setAxesWidthAuto(self,axes):
        max_width = self._getMaxAxesWidth(axes)
        self._setAxesWidth(axes,max_width)
        
    def _setAxesWidth(self,axes,width):
            
        for p in self.plots:
            sw = p.axisWidget(axes)
            sd = sw.scaleDraw()
            sd.setMinimumExtent(width)
            p.replot()

            
    def _setColors(self):
        keys = []
        for spec in self.specs:
            items = spec[7]
            
            for key in items:
                if key not in keys:
                    keys.append(key)
                    
        number = len(keys) 
        
        hue = np.linspace(start=0, stop=359, num=number+1,dtype=int)[1:]
        
        if number > 1:
            random.shuffle(hue)

        sat = 255
        val = 255
        
        colors = {}
        for i,key in enumerate(keys):
            colors[key] = QColor.fromHsv(hue[i],sat,val)

        return colors
        
    def _setGrid(self):
        grid = QGridLayout()
        grid.setContentsMargins(0,0,0,0)
        grid.setSpacing(0)
        self.setLayout(grid)   
        return grid
        
    def _setPlots(self,grid):
        plots = []
        for spec in self.specs:
                
            plot = Plot(spec[0])
            plot.setLabel("title", spec[0], size=10, bold=True)
            plot.setLabel("xlabel", spec[1], size=10, bold=False)
            plot.setLabel("ylabel", spec[2], size=10, bold=False)
            plot.setPosition(spec[3],spec[4])
            plot.setSpan(spec[5],spec[6])

            for key,item_type in spec[7].items():
                
                if item_type == "image":
                    item = ImageItem(key)
                elif item_type == "curve":
                    item = CurveItem(key)
                elif item_type == "point":
                    item = PointItem(key)
                elif item_type == "vline":
                    item = LineItem(key)
                    item.setType("vline")
                elif item_type == "hline":
                    item = LineItem(key)
                    item.setType("hline")
                else:
                    raise ValueError("Wrong Item Type (%r)" % item_type)

                item.setColor(self.colors[key])
                plot.addItem(item)
                
            self.grid.addWidget(plot,spec[3],spec[4],spec[5],spec[6])
            plots.append(plot)
            
        return plots
    
    def getName(self):
        return self.name
    
    def getSpecs(self):
        return self.specs
        
    def setData(self,data):
        for plot in self.plots: 
            for item in plot.getItems():
                name = item.getName()
                item.updateData(data[name])
 
            plot.replot()

    def _getAxesMargins(self):
        width_margin = 0
        height_margin = 0
        
        size = self.size()        
        self.resize(1000,1000)
        self._setAxesWidthAuto(QwtPlot.yLeft)  
        self.update()
        for plot in self.plots:            
            ph,pw = plot.getSize()
            ch,cw = plot.getCanvasSize()
            
            width_margin += pw - cw
            height_margin += ph - ch
            
        self.resize(size)

        return height_margin, width_margin

    def _getRatio(self,pixmap):
        widthPX = pixmap.width()
        widthMM = pixmap.widthMM()
        heightPX = pixmap.height()
        heightMM = pixmap.heightMM()        
            
        # mm per pixel
        width_ratio = widthMM /widthPX
        height_ratio = heightMM /heightPX       
        
        return height_ratio, width_ratio
        
    def save(self):
        letterW = 215.9
        letterH = 279.4
        margin = 25.4
            
        row_count = self.grid.rowCount()
        col_count = self.grid.columnCount()
        # height for width ratio
        ratio = row_count / col_count
        
        hm,wm = self._getAxesMargins()
 
        size = self.size()
        pix = QPixmap(size)

        hr,wr = self._getRatio(pix)
   
        # mm = pixels * mm per pixel
        Wmargin = wm * wr
        Hmargin = hm * hr

        # wanted TOTAL image REAL width in mm minus paper margins
        wantW = letterW - 2*margin
        
        # wanted REAL width and height only considering plotting canvases
        Wmm = wantW- Wmargin
        Hmm = Wmm * ratio

        # wanted TOTAL image REAL height + margins
        wantH = Hmm + Hmargin
        
        # image wanted sizes in pixels
        wPX = wantW / wr
        hPX = wantH / hr

        pixs = pix.scaled(wPX,hPX)
        self.resize(wPX,hPX)
               
        for p in self.plots:
            p.setAutoFillBackground(True)
            pl = p.palette()
            pl.setColor(p.backgroundRole(),Qt.white)
            p.setPalette(pl)
            p.replot()
        
        self.render(pixs)      
        self.resize(size)
        pixs.save('save.png')
        

class Plot(QwtPlot):

    def __init__(self,name):
        QwtPlot.__init__(self)

        self.name = name
        self.title = None
        self.xlabel = None
        self.ylabel = None
        self.row_pos = None
        self.col_pos = None
        self.row_span = None
        self.col_span = None
        
        self.items = []
        #self._setGrid()
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setSizePolicy(policy)
        
        self.canvas().setFrameStyle(QFrame.Plain)
        
        self.setCanvasBackground(Qt.white)      
        self.plotLayout().setAlignCanvasToScales(True)
        for ax in range(QwtPlot.axisCnt):
            self.axisWidget(ax).setMargin( 0 )
            self.axisScaleDraw(ax).enableComponent(QwtAbstractScaleDraw.Backbone,True)
            
        
    def _setGrid(self):
        grid = QwtPlotGrid()
        pen = QPen(Qt.DotLine)
        pen.setColor(Qt.white)
        pen.setWidth(0)
        grid.setPen(pen)
        grid.attach(self)

    def getCanvasSize(self):
        rect = self.canvas().contentsRect()
        height = rect.height()
        width = rect.width()
        return height,width
        
    def setLabel(self,label_type,label,size=10,bold=False):
        
        font = QFont()
        font.setPointSize(size)
        font.setBold(bold)
        
        lbl = QwtText(label)   
        lbl.setFont(font)
        
        if label_type == "title":
            self.title = label
            self.setTitle(lbl)
        elif label_type == "xlabel":
            self.xlabel = label
            self.setAxisTitle(QwtPlot.xBottom,lbl)    
            self.setAxisFont(QwtPlot.xBottom,font)
        elif label_type == "ylabel":
            self.ylabel = label
            self.setAxisTitle(QwtPlot.yLeft,lbl)
            self.setAxisFont(QwtPlot.yLeft,font)
        else:
            raise ValueError("Wrong Label Type (%r)" % label_type)   
 
    def addItem(self,item):
        item.attach(self)
        self.items.append(item)
        
    def getItems(self):
        return self.items
        
    def attach(self,grid):
        grid.addWidget(self,
                       self.row_pos,self.col_pos,
                       self.row_span,self.col_span) 
                       
    def setPosition(self,row_pos,col_pos):
        self.row_pos = row_pos
        self.col_pos = col_pos
        
    def setSpan(self,row_span,col_span):
        self.row_span = row_span
        self.col_span = col_span
        
    def getPosition(self):
        return self.row_pos, self.col_pos

    def getSpan(self):
        return self.row_span, self.col_span
    
    def getSize(self):
        size = self.size()
        return size.height(), size.width()        
        
    def getLabels(self):
        return self.xlabel, self.ylabel, self.title
        
class ImageItem(QwtPlotItem):

    def __init__(self, name):
        QwtPlotItem.__init__(self)

        self.name = name
        self.type = "image"
        self.color = None
        
        self.np_image = None  
        self.q_image = None
        self.height = 1
        self.width  = 1
        
        cmap = cm.ScalarMappable(cmap="jet")
        im = range(256)
        rgba = cmap.to_rgba(im,bytes=True)
        self.color_table = [qRgb(c[0],c[1],c[2]) for c in rgba]
        #self.color_table = [qRgb(i, i, i) for i in range(256)]
  
    def getName(self):
        return self.name
        
    def getData(self):
        return self.np_image
        
    def setColor(self,color):
        self.color = color
        
    def getRGB(self):
        r,g,b,a = self.color.getRgb()
        return r,g,b
        
    def getType(self):
        return self.type
        
    def updateData(self, np_image):
        self.np_image = np_image
        #self.q_image = qwt.toqimage.array_to_qimage(np_image)
        self.q_image = self.toQImage(np_image)  
        
    def toQImage(self,im, copy=False):
        
        if isinstance(im,np.ndarray) is False:
            raise TypeError("Unsupported image data type %r" % type(im))

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
                    
    def draw(self, painter, xMap, yMap, rect):
        if self.q_image is not None:
            self.plot().setAxisScale(QwtPlot.xBottom, 0,self.q_image.width())
            self.plot().setAxisScale(QwtPlot.yLeft, self.q_image.height(),0)
            
            xp1 = xMap.p1()
            xp2 = xMap.p2()
            yp1 = yMap.p1()
            yp2 = yMap.p2()
            # zoom
            image = self.q_image.scaled(xp2-xp1+1, yp1-yp2+1)
            # draw
            painter.drawImage(xp1, yp2, image)
        
        
class CurveItem(QwtPlotCurve):

    def __init__(self, name):
        QwtPlotCurve.__init__(self)
        
        self.name = name 
        self.type = "curve"
        self.color = None
        self.curve_data = None            
        
    def getName(self):
        return self.name
        
    def getData(self):
        return self.curve_data
        
    def getType(self):
        return self.type

    def setColor(self,color):
        self.color = color
        self.setPen(QPen(color, 2))
        
    def getRGB(self):
        r,g,b,a = self.color.getRgb()
        return r,g,b
        
    def updateData(self,data):
        self.curve_data = data
        self.setData(data[0],data[1])

        
class PointItem(QwtPlotCurve):
    
    def __init__(self, name):
        QwtPlotCurve.__init__(self)    

        self.name = name
        self.type = "point"
        self.color = None
        
        self.nr_points = 150
        self.x = np.zeros(self.nr_points)
        self.y = np.zeros(self.nr_points)
        self.count = 0
        
        self.setZero()

    def getName(self):
        return self.name
        
    def getType(self):
        return self.type
        
    def getData(self):
        return [self.x,self.y]
        
    def setColor(self,color):
        self.color = color
        self.setPen(QPen(color, 2))
        
    def getRGB(self):
        r,g,b,a = self.color.getRgb()
        return r,g,b

    # PUBLIC METHODS
    def setZero(self):
        self.x = np.arange(self.nr_points)
        self.y = np.zeros(self.nr_points) 
        self.setData(self.x,self.y)
        
    def updateCurve(self,point):
        # update y 
        y = self.y
        y[:-1] = y[1:]
        y[-1] = point
        self.y = y
        
        # update x
        if self.count == self.nr_points:
            self.x[:-1] = self.x[1:]
            self.x[-1] +=1
        else:
            self.count +=1          
        
    def updateData(self,data):
        self.updateCurve(data)                             
        self.setData(self.x,self.y)
        
        
class LineItem(QwtPlotMarker):

    def __init__(self, name):
        QwtPlotMarker.__init__(self)

        self.name = name
        self.type = "line"
        self.color = None
        self.data = None

    def setType(self,line_type):
        if line_type == "vline":
            self.type = line_type
            style = QwtPlotMarker.VLine
        elif line_type == "hline":
            self.type = line_type
            style = QwtPlotMarker.HLine
        else:
            raise ValueError("Wrong Line Type (%r)" % line_type)
            
        self.setLineStyle(style)
        
    def getName(self):
        return self.name
        
    def getData(self):
        return self.data
        
    def getType(self):
        return self.type

    def setColor(self,color):
        self.color = color
        self.setLinePen(QPen(color, 2, Qt.DashLine))
        
    def getRGB(self):
        r,g,b,a = self.color.getRgb()
        return r,g,b
        
    def updateData(self,data):
        self.data = data

        if self.type == "vline":
            self.setValue(data,0)
        elif self.type == "hline":
            self.setValue(0,data)
        



        

        