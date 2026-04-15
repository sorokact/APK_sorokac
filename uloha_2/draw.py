from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import geopandas as gpd

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__building = QPolygonF()
        self.__mbr = QPolygonF()
        self.__ch = QPolygonF()
        self.__shp_loaded = False
        self.__shp_buildings = []
        self.__buildings_simp = []

        
    def mousePressEvent(self, e:QMouseEvent):
        #Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        #Create new point
        p = QPointF(x,y)
        
        #Add P to polygon
        self.__building.append(p)
        
        #Repaint
        self.repaint()
        

    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
        
        #If SHP loaded, draw buildings from SHP
        if self.__shp_loaded:
            qp.setPen(Qt.GlobalColor.black)
            qp.setBrush(Qt.GlobalColor.darkGray)
            for b in self.__shp_buildings:
                qp.drawPolygon(b)
        else:
            #Set attributes, building
            qp.setPen(Qt.GlobalColor.black)
            qp.setBrush(Qt.GlobalColor.yellow)
            #Draw building
            qp.drawPolygon(self.__building)
        
        #Set attributes, convex hull
        qp.setPen(Qt.GlobalColor.blue)
        qp.setBrush(Qt.GlobalColor.transparent)
        #Draw convex hull
        qp.drawPolygon(self.__ch)
        
        #Set attributes, MBR
        qp.setPen(Qt.GlobalColor.red)
        qp.setBrush(QColor(255, 0, 0, 50))
        
        #Draw simplified buildings
        for simp in self.__buildings_simp:
            qp.drawPolygon(simp)
            
        #Draw MBR
        qp.drawPolygon(self.__mbr)
        
        #End draw
        qp.end()
        
        
    def setMBR(self, mbr:QPolygonF):
        #Set MBR
        self.__mbr = mbr
        

    def setCH(self, ch:QPolygonF):
        #Set CH
        self.__ch = ch  
        
        
    def getBuilding(self):
        #Return building or  list of buildings from SHP
        if self.__shp_loaded:
            return self.__shp_buildings
        else:
            return [self.__building]
    
    
    def clearResult(self):
        #Clear data structures for results
        self.__ch.clear()
        self.__mbr.clear()
        self.__buildings_simp.clear()
        
        #Repaint screen
        self.repaint()

    def openFile(self):
        #Open file dialog and read SHP file (AI + own from 102 to 133)
        file_name, _ = QFileDialog.getOpenFileName(None, "Open File", "", "Shapefile (*.shp)")

        if file_name:
            try:
                self.shp = gpd.read_file(file_name)
                self.geomShapefile()
            except Exception as e:
                QMessageBox.critical(None, "Error", f"Could not open file: {str(e)}")

    def geomShapefile(self):
        #Normalize geometries and convert to QPolygonF
        self.__shp_buildings.clear()
        
        if self.shp is None or self.shp.empty:
            return

        min_x, min_y, max_x, max_y = self.shp.total_bounds
        width = self.width()
        height = self.height()
        
        for geom in self.shp.geometry:
            if geom.geom_type == "Polygon":                
                pol = QPolygonF([QPointF((float(x) - min_x) / (max_x - min_x) * width,
                    height - (float(y) - min_y) / (max_y - min_y) * height
                    )
                    for x, y in geom.exterior.coords
                ])
                self.__shp_buildings.append(pol)

        self.__shp_loaded = True
        self.repaint()

    def clearAll(self):
        #Clear all data structures and reset state
        self.__shp_buildings.clear()
        self.__building.clear()
        self.__buildings_simp.clear()
        self.__ch.clear()
        self.__mbr.clear()
        self.__shp_loaded = False
        self.repaint()

    def setSimplifBuilding(self, buildings_simp_):
        #Save simplified buildings and repaint
        self.__buildings_simp = buildings_simp_
        self.repaint()