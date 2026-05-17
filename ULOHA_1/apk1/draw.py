from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtGui import QPaintEvent
from PyQt6.QtWidgets import *
import geopandas

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pol = QPolygonF()
        self.__q = QPointF(100, 100)
        self.__add_vertex = True
        self.__polygonList = []
        self.__highlightPol = []
        

    def mousePressEvent(self, e):
        # Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        # Create polygon vertex
        if self.__add_vertex == True:
            
            # Create new point
            p = QPointF(x,y)
            
            # Add P to polygon
            self.__pol.append(p)
            
        # Set new q coordinates
        else: 
            self.__q.setX(x)
            self.__q.setY(y)
                    
        # Repaint
        self.repaint()

    def paintEvent(self, e):
        # Draw situation
        qp = QPainter(self)
        
        # Start draw
        qp.begin(self)
        
        # Set attributes, polygon
        qp.setPen(Qt.GlobalColor.black)
        
        # Draw polygons loaded from file, AI 51 - 66
        i = 0
        while i < len(self.__polygonList):
            highlight = False
            j = 0
            while j < len(self.__highlightPol):
                if self.__highlightPol[j] == self.__polygonList[i]:
                    highlight = True
                j = j + 1

            if highlight == True:
                qp.setBrush(Qt.GlobalColor.yellow)
            else:
                qp.setBrush(Qt.GlobalColor.white)

            qp.drawPolygon(self.__polygonList[i])
            i = i + 1

        # Draw manually added polygon
        qp.setBrush(Qt.GlobalColor.yellow)
        qp.drawPolygon(self.__pol)
        
        # Set attributes, point
        qp.setBrush(Qt.GlobalColor.green)
        
        # Draw point
        r = 10
        qp.drawEllipse(int(self.__q.x()-r), int(self.__q.y()-r), 2*r, 2*r)
        
        # End draw
        qp.end()
        
    def changeStatus(self):
        # Change input source, point or polygon
        self.__add_vertex = not (self.__add_vertex)
        
    def clearData(self):
        # Clear data
        self.__pol.clear()
        self.__polygonList = []
        self.__highlightPol = []
        self.repaint()
        self.__q.setX(-25)
        self.__q.setY(-25)
    
    def getQ(self):
        # Return point
        return self.__q
    
    def getPol(self):
        # Return polygon
        return self.__pol

    def getPolygons(self):
        # Return list of loaded polygons
        return self.__polygonList

    def setHighlightedPolygons(self, indexList):
        self.__highlightPol = indexList
        self.repaint()
    
    def paintRes(self, pol):
        self.__highlightPol.append(pol)
        self.update()

    def clearRes(self):
        self.__highlightPol = []
        self.update()

    def openFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)")
        if filePath:
            self.loadSHP(filePath)

    def loadSHP(self, filePath):
        shapeData = geopandas.read_file(filePath)

        # Create bounding box
        boundary = shapeData.total_bounds
        minX = boundary[0]
        minY = boundary[1]
        maxX = boundary[2]
        maxY = boundary[3]

        # Set canvas size
        width = self.width()
        height = self.height()

        self.__polygonList = []
        self.__highlightPol = []
        self.__pol.clear()

        # AI 143 - 160
        for shape in shapeData.geometry:
            if shape is None:
                continue

            def create_qpoly(geom):
                poly = QPolygonF()
                for point in geom.exterior.coords:
                    screenX = (point[0] - minX) / (maxX - minX) * width
                    screenY = (1.0 - (point[1] - minY) / (maxY - minY)) * height
                    poly.append(QPointF(screenX, screenY))
                return poly

            if shape.geom_type == "Polygon":
                self.__polygonList.append(create_qpoly(shape))

            elif shape.geom_type == "MultiPolygon":
                for part in shape.geoms:
                    self.__polygonList.append(create_qpoly(part))

        self.repaint()