from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from math import *
from edge import *
from triangle import *
import numpy as np

class Algorithms:
    
    def __init__(self):
        pass
    
    def getPointLinePosition(self, a, b, p):
        #Analyze point and aline position (half plane test)
        tolerance = 1.0e-6
        
        #Components of vectors
        ux = b.x() - a.x()
        uy = b.y() - a.y()
        vx = p.x() - a.x()
        vy = p.y() - a.y()
        
        #Test criterion
        t = ux*vy - vx*uy
        
        #Point in the left half plane
        if t > tolerance:
            return 1
        
        #Point in the right half plane
        if t < -tolerance:
            return 0
    
        #Point on the line
        return -1
        
    
    def getNearestPoint(self, p, points):
        #Find point nearest to p in points
        p_nearest = None
        d_min = inf
        
        #Process all points
        for p_i in points:
            
            #Point p different from p_i
            if p != p_i:            
                #Coordinate differences
                dx = p.x() - p_i.x()
                dy = p.y() - p_i.y()
                      
                #Compute distance          
                dist = sqrt(dx**2 + dy**2)
                
                #Update minimum
                if dist < d_min:
                    d_min = dist
                    p_nearest = p_i
                    
        return p_nearest
    
    
    def get2LinesAngle(self, p1:QPointF, p2:QPointF, p3:QPointF, p4:QPointF):
        #Angle between two lines
        ux = p2.x() - p1.x()    
        uy = p2.y() - p1.y()
        
        vx = p4.x() - p3.x()
        vy = p4.y() - p3.y()    
        
        #Dot product
        dot = ux*vx + uy*vy
        
        #Norms
        nu = (ux**2 + uy**2)**0.5
        nv = (vx**2 + vy**2)**0.5
        
        #Correct interval
        arg = dot/(nu*nv)
        arg = max(-1, min(1,arg)) 
        
        return acos(arg)
    
    
    def findDelaunayPoint(self, p1, p2, points):
        #Find Delaunay point to the edge
        p_dt = None
        phi_max = 0

        #Process all points
        for p_i in points:
            
            #Point pi different from p1 and p2
            if p_i != p1 and p_i != p2:
                
                #Point in the left halfplane
                if self.getPointLinePosition (p_i, p1, p2) == 1:
                    
                    #Compute phi
                    phi = self.get2LinesAngle(p_i, p2, p_i, p1)
                    
                    #Update maximum
                    if phi > phi_max:
                        phi_max = phi
                        p_dt = p_i
        return p_dt
                    
    def createDT(self, points):
        #Create Delaunay triangulation                 
        DT = []
        AEL = [] 
        
        #Find pivot
        q = min(points, key = lambda k: k.y())   
        
        #Find point nearest to q
        qn = self.getNearestPoint(q, points)       
        
        #Create new edges
        e = Edge(q, qn)
        es = Edge(qn, q)  
        
        #Edges to AEL
        AEL.append (e)
        AEL.append (es) 
        
        #Repeat until AEL is empty             
        while AEL:
            #Take first edge
            e1 = AEL.pop()
            
            #Switch orientation
            e1s = e1.switchOrientation()
            
            #Find Delaunay point
            p_dt = self.findDelaunayPoint(e1s.getStart(), e1s.getEnd(), points)
            
            #Jump to the next iteration
            if p_dt == None:
                continue
            
            #Create new edges
            e2 = Edge(e1s.getEnd(), p_dt)
            e3 = Edge(p_dt, e1s.getStart())
            
            #Add new edges to DT
            DT.append(e1s)
            DT.append(e2)
            DT.append(e3)
                 
            #Update AEL
            self.updateAEL(e2,AEL)
            self.updateAEL(e3,AEL)
            
        return DT
    
    
    def updateAEL(self, e, AEL):
        #Verify if e in AEL with diffferent orientation
        es = e.switchOrientation()
        
        #Edge e in AEL, remove
        if es in AEL:
            AEL.remove(es)
            
        #Add e to AEL
        else:
            AEL.append(e) 
            
            
    def getContourPoint(self, p1, p2, z):
        #Compute intersection line and plane
        xb = (p2.x() - p1.x())/(p2.z() - p1.z()) * (z - p1.z()) + p1.x()
        yb = (p2.y() - p1.y())/(p2.z() - p1.z()) * (z - p1.z()) + p1.y()
        
        return QPoint3DF(xb, yb, z)
    
    
    def createContourLines(self, DT, z_min, z_max, dz):
        #Create contour lines using linear interpolation
        contour_lines = []
        
        #Process all contour lines
        for z in np.arange(z_min, z_max, dz):
            
            #Traverse dt triangles one by one
            for i in range(0, len(DT), 3):
                
                #Triangle vertices
                p1 = DT[i].getStart()
                p2 = DT[i+1].getStart()
                p3 = DT[i+1].getEnd()
                
                #Height differences
                dz1 = z - p1.z()
                dz2 = z - p2.z()
                dz3 = z - p3.z()
                
                #Skip triangle
                if dz1 == 0 and dz2 == 0 and dz3 == 0:
                    continue
                
                #Edge (p1, p2) is colinear
                elif dz1 == 0 and dz2 == 0:
                    contour_lines.append(DT[i])
                    
                #Edge (p2, p3) is colinear
                elif dz2 == 0 and dz3 == 0:
                    contour_lines.append(DT[i+1])
                
                #Edge (p3, p1) is colinear
                elif dz3 == 0 and dz1 == 0:
                    contour_lines.append(DT[i+2])
                    
                #Edges (p1, p2) and (p2, p3) intersected by plane
                elif (dz1*dz2 <= 0) and (dz2*dz3 <= 0):
                    self.createContourLineSegment(p1, p2, p3, z, contour_lines)   
                  
                #Edges (p3, p1) and (p1, p2) intersected by plane      
                elif (dz2*dz3 <= 0) and (dz3*dz1 <= 0):
                    self.createContourLineSegment(p2, p3, p1, z, contour_lines)
                
                #Edges (p3, p1) and (p1, p2) intersected by plane
                elif (dz3*dz1 <= 0) and (dz1*dz2 <= 0):
                    self.createContourLineSegment(p3, p1, p2, z, contour_lines)
                    
        return contour_lines
    
    
    def createContourLineSegment(self, p1, p2, p3, z, contour_lines):
        #Create contour line segment
        
        #Line and plane intersection
        a = self.getContourPoint(p1, p2, z)
        b = self.getContourPoint(p2, p3, z)
        
        #Create edge, contour
        e = Edge(a, b)
    
        #Add contour to the list
        contour_lines.append(e)

    def transformDTToTriangles(self, dt:list[Edge], triangles:list[Triangle]):
        for i in range(0, len(dt), 3):
            
            #Get triangle vertices
            p1 = dt[i].getStart()
            p2 = dt[i+1].getStart()
            p3 = dt[i+2].getStart()
            
            #Create new triangle
            triangle = Triangle(p1, p2, p3, 0, 0)
            
            #Retrieve triangle and add it to the list
            triangles.append(triangle)
        
    def calculateSlope(self, p1: QPoint3DF, p2: QPoint3DF, p3: QPoint3DF):
        #Calculate triangle slope using the normal vector of the triangle
        
        nx = (p2.y() - p1.y()) * (p3.z() - p1.z()) - (p2.z() - p1.z()) * (p3.y() - p1.y())
        ny = (p2.z() - p1.z()) * (p3.x() - p1.x()) - (p2.x() - p1.x()) * (p3.z() - p1.z())
        nz = (p2.x() - p1.x()) * (p3.y() - p1.y()) - (p2.y() - p1.y()) * (p3.x() - p1.x())

        #Magnitude of the normal vector
        norm_sq = nx**2 + ny**2 + nz**2
        
        if norm_sq > 0:
            #Check if the normal vector is not vertical and calculate slope
            return acos(nz / sqrt(norm_sq))
            
        return 0.0
    
    def calculateAspect(self, p1: QPoint3DF, p2: QPoint3DF, p3: QPoint3DF):
        #Calculate triangle aspect using the normal vector of the triangle
        
        nx = (p2.y() - p1.y()) * (p3.z() - p1.z()) - (p2.z() - p1.z()) * (p3.y() - p1.y())
        ny = -((p2.x() - p1.x()) * (p3.z() - p1.z()) - (p2.z() - p1.z()) * (p3.x() - p1.x()))
        
        #Calculate aspect
        aspect = atan2(nx, ny)
        
        #Return corrected aspect
        if aspect < 0:
            return aspect + 2 * pi
            
        return aspect
    
    def DTMaspect(self, dt, triangles):
        #Compute aspect for each triangle in the DTM
        
        if len(triangles) == 0:
            self.transformDTToTriangles(dt, triangles)

        #Process each triangle
        for t in triangles:
            #Get vertices
            p1, p2, p3 = t.getP1(), t.getP2(), t.getP3()

            #Compute orientation
            aspect_v = self.calculateAspect(p1, p2, p3)
            
            # Store result
            t.setAspect(aspect_v)
        return triangles
            
    def DTMslope(self, dt, triangles):
        #Compute slope for each triangle in the DTM
        
        if len(triangles) == 0:
            self.transformDTToTriangles(dt, triangles)

        #Process each triangle
        for t in triangles:
            #Get vertices
            p1, p2, p3 = t.getP1(), t.getP2(), t.getP3()

            #Compute slope
            slope_v = self.calculateSlope(p1, p2, p3)
            
            #Store result
            t.setSlope(slope_v)
        return triangles