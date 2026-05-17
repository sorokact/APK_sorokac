import math

from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from numpy import pi
from qpoint3df import *
from random import *
from edge import *
from triangle import *
import pandas as pd

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.__points =[]
        self.__DT = []
        self.__view_DT = True
        self.__contours = []
        self.__view_contours = True
        self.__triangles_slope = []
        self.__view_slope = True
        self.__triangles_aspect = []
        self.__view_aspect = True
        self.__cloud_loaded = False
        
    def loadPoints(self, data):
        #Load points from data list
        if not data:
            return

        self.__points.clear()
        
        #Find boundaries to fit data to screen
        xs = [p[0] for p in data]
        ys = [p[1] for p in data]
        
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        #Avoid division by zero
        dx = max_x - min_x if max_x != min_x else 1
        dy = max_y - min_y if max_y != min_y else 1
        
        #Determine scaling factors
        width = self.width() - 40
        height = self.height() - 40
        
        for x, y, z in data:
            #Normalize coordinates
            nx = 20 + (x - min_x) / dx * width
            ny = self.height() - 20 - (y - min_y) / dy * height
            
            self.__points.append(QPoint3DF(nx, ny, z))
        
        #Repaint screen with new points
        self.repaint()
        
    def openFile(self):
        #Open point cloud file
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Text Files (*.txt)")
        
        if file_name:
            #Create table from file
            data = pd.read_csv(file_name, sep=r"\s+", header=None, names=["X", "Y", "Z"], comment="#", na_values=["X", "Y", "Z"])
            
            #Convert table to list of tuples and load points
            points_list = [tuple(row) for row in data.values]
            self.loadPoints(points_list)
            
            #Check cloud point loading
            self.__cloud_loaded = True

    def createSlope(self, qp: QPainter):

        for t in self.__triangles_slope:
            #Get triangle vertices
            p1, p2, p3 = t.getP1(), t.getP2(), t.getP3()
            
            #Get slope
            slope = t.getSlope()
            
            #Convert slope to color
            color = int(255 * (1 - (2 * slope / pi)))
            color = max(0, min(255, color))
            
            #Set brush color
            qp.setBrush(QColor(color, color, color))
            qp.setPen(Qt.PenStyle.NoPen)
            
            #Create and draw polygon
            pol = QPolygonF([p1, p2, p3])
            qp.drawPolygon(pol)
            
    def createAspect(self, qp: QPainter):
        
        for t in self.__triangles_aspect:
            #Get triangle vertices
            p1, p2, p3 = t.getP1(), t.getP2(), t.getP3()
            
            #Get aspect
            asp = t.getAspect()
            
            #Define colors for aspect categories
            colors = [
                #East
                QColor(0, 104, 192),
                
                #Southeast
                QColor(108, 0, 163),
                
                #South
                QColor(202, 0, 156),
                
                #Southwest
                QColor(255, 85, 104),
                
                #West
                QColor(255, 171, 71),
                
                #Northwest
                QColor(244, 250, 0),
                
                #North
                QColor(132, 214, 0),
                
                #Northeast
                QColor(0, 171, 68)
            ]
            
            #Compute color index based on aspect angle
            idx = int(((asp + pi/8) % (2*pi)) / (pi/4))
            qp.setBrush(colors[min(idx, 7)])
            qp.drawPolygon(QPolygonF([p1, p2, p3]))
        
        
    def mousePressEvent(self, e):
        
        if self.__cloud_loaded:
            return
        
        #Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        #Get random z
        z_min = 200
        z_max = 600
        z = random() * (z_max - z_min) + z_min

        #Create new point
        p = QPoint3DF(x, y, z)
        
        #Add P to polygon
        self.__points.append(p)
        
        #Repaint canvas
        self.repaint()
        

    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
       
        if self.__view_slope:
            self.createSlope(qp)
            
        if self.__view_aspect:
            self.createAspect(qp)
            
        pen = QPen()

        #Draw delaunay triangulation
        if self.__view_DT:
            #Set properties for delaunay triangulation
            qp.setPen(Qt.GlobalColor.gray)

            for e in self.__DT:
                qp.drawLine(e.getStart(), e.getEnd())
        
        #Draw contour lines
        if self.__view_contours:
            #Draw contour lines
            qp.setPen(Qt.GlobalColor.yellow)
            
            for c in self.__contours:
                qp.drawLine(c.getStart(), c.getEnd())
        
        #Draw points
        pen.setColor(Qt.GlobalColor.black)
        qp.setBrush(Qt.GlobalColor.red)
        qp.setPen(pen)
        
        #Point radius
        r = 5
            
        for p in self.__points:
            #Draw point
            qp.drawEllipse(int(p.x()-r), int(p.y()-r), 2*r, 2*r)
        qp.drawPoints(self.__points)
        
        #End draw
        qp.end()
        
    def clearRes(self):
        #Clear results of analyses
        self.__DT.clear()
        self.__triangles_slope.clear()
        self.__triangles_aspect.clear()
        self.__contours.clear()
           
        #Repaint canvas
        self.repaint()
        
    def clearAll(self):
        #Clear all data and results
        self.__points.clear()
        self.__cloud_loaded = False
        self.__DT.clear()
        self.__contours.clear()
        self.__triangles_slope.clear()
        self.__triangles_aspect.clear()
        
        #Repaint canvas
        self.repaint()
    
    def exit(self):
        QApplication.instance().quit()
        
    def getDT(self):
        return self.__DT
    
    def getPoints(self):
        return self.__points
    
    def getTrianglesSlope(self):
        return self.__triangles_slope

    def getTrianglesAspect(self):
        return self.__triangles_aspect
    
    def setDT(self, DT):
        self.__DT = DT
        self.update()
           
    def setContours(self, contours):
        self.__contours = contours
        self.update()
        
    def setTrianglesSlope(self, tri_):
        self.__triangles_slope = tri_
        self.update()

    def setTrianglesAspect(self, tri_):
        self.__triangles_aspect = tri_
        self.update()

    def setViewDT(self, view):
        self.__view_DT = view
        self.update()

    def setViewContours(self, view):
        self.__view_contours = view
        self.update()

    def setViewSlope(self, view):
        self.__view_slope = view
        self.update()

    def setViewAspect(self, view):
        self.__view_aspect = view
        self.update()
        