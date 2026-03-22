from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import numpy as np


class Algorithms:

    def pointOnVertex(self, q: QPointF, p: QPointF):
        # Check if x coordinates are identical for points q and p
        xMatch = False
        if q.x() == p.x():
            xMatch = True

        # Check if y coordinates are identical for points q and p
        yMatch = False
        if q.y() == p.y():
            yMatch = True

        # Check if coordinates are equal
        if xMatch == True:
            if yMatch == True:
                return True
        # Point is not on the vertex
        return False

    def rayCrossing(self, q: QPointF, pol: QPolygonF):
        # Initialize position of intersetions (left and right)
        kl = 0
        kr = 0
        
        # Number of vertices of a polygon
        n = len(pol)
        
        # Process all points of a polygon
        for i in range(n):
            
            # Obtain i-th point
            p1X = pol[i].x() - q.x()
            p1Y = pol[i].y() - q.y()
            
            # Obtain the (i+1)th point
            p2X = pol[(i + 1) % n].x() - q.x()
            p2Y = pol[(i + 1) % n].y() - q.y()
            
          # Point lies on vertex
            if p1X  == 0 and p1Y == 0:
                return -1
            
            # Horizontal edge
            if p1Y == p2Y:
                if p1Y == 0:
                    if (p1X <= 0 and p2X >= 0) or (p2X <= 0 and p1X >= 0):
                        return -1
                continue
            
            # Compute x coordinate with intersection of the ray
            xm = (p2X * p1Y - p1X * p2Y) / (p2Y - p1Y)
            
            # Check if point lies exactly on the edge
            if xm == 0:
                if (p1Y <= 0 and p2Y >= 0) or (p2Y <= 0 and p1Y >= 0):
                    return -1
            
            # Check for intersection with lower segmet
            if (p2Y < 0) != (p1Y < 0):
                if xm < 0:
                    kl += 1
                    
            # Check for intersection with upper segment
            if (p2Y > 0) != (p1Y > 0):
                if xm > 0:
                    kr += 1

        # Point lies on the edge of the polygon
        if (kl % 2) != (kr % 2):
            return -1

        # Point is inside of the polygon
        if kr % 2 == 1:
            return 1
        
        # Point is outside of the polygon
        return 0

    def calculateAngle(self, q: QPointF, p1: QPointF, p2: QPointF):
        # Compute first vector from q to p1
        v1X = p1.x() - q.x()
        v1Y = p1.y() - q.y()

        # Compute second vector from q to p2
        v2X = p2.x() - q.x()
        v2Y = p2.y() - q.y()

        # Compute length of vectors
        lenV1 = np.sqrt(v1X * v1X + v1Y * v1Y)
        lenV2 = np.sqrt(v2X * v2X + v2Y * v2Y)

        # Division by zero
        if lenV1 == 0 or lenV2 == 0:
            return 0

        # Calculate the cosine value
        cosValue = (v1X * v2X + v1Y * v2Y) / (lenV1 * lenV2)

        # Range for arccos
        if cosValue > 1:
            cosValue = 1
        if cosValue < -1:
            cosValue = -1
            
        # Calculate angle using arccos
        angle = np.arccos(cosValue)
        return angle

    def getPointLocation(self, q: QPointF, p1: QPointF, p2: QPointF):
        # Calculate determinant to check which side of the line q is on
        eX = p2.x() - p1.x()
        eY = p2.y() - p1.y()
        pX = q.x() - p1.x()
        pY = q.y() - p1.y()

        det = eX * pY - eY * pX
        return det

    def windingNumber(self, q: QPointF, pol: QPolygonF):
        # Initialize total swept angle
        sum_angle = 0.0
        
        # Define tolerance for floating point comparisons
        tolerance = 1e-9

        # Number of vertices of a polygon
        n = len(pol)
        
        # Starting index for processing vertices
        i = 0

        while i < n:
            # Return -1 if q is sitting on a vertex
            onVertex = self.pointOnVertex(q, pol[i])
            if onVertex == True:
                return -1
            
            # New vertex index
            if (i + 1) == n:
                ni = 0
            else:
                ni = i + 1

            # Compute determinant
            det = self.getPointLocation(q, pol[i], pol[ni])
            # Compute angle defined by q and two vertices of the edge of the polygon
            angle = self.calculateAngle(q, pol[i], pol[ni])
            
            # If determinant is equal to zero the point might lie on the edge
            if det == 0:
                # Setting upper and lower bounds
                upperBound = np.pi + tolerance
                lowerBound = np.pi - tolerance

                # Check if angle is lying between upper and lower bounds
                onEdge = False
                if angle <= upperBound:
                    if angle >= lowerBound:
                        onEdge = True
                # Point lies on the edge of the polygon
                if onEdge == True:
                    return -1

                # Point does not lie on the edge, skip
                i = i + 1
                continue

            # If determinant is positive, point is to the left of the edge, add angle
            if det > 0:
                sum_angle = sum_angle + angle
            # If determinant is negative, point is to the right of the edge, subtract angle
            else:
                sum_angle = sum_angle - angle
            # Move to the next vertex
            i = i + 1

        # Check if total swept angle is close to 2*pi
        absTotal = abs(sum_angle)
        # Setting upper and lower bounds
        upperLimit = 2 * np.pi + tolerance
        lowerLimit = 2 * np.pi - tolerance

        # If total swept angle is close to 2*pi, point is inside the polygon
        if absTotal <= upperLimit:
            if absTotal >= lowerLimit:
                return 1
        # Point is outside the polygon
        return 0

    def inMinMaxBox(self, q: QPointF, pol: QPolygonF):
        # Start with the first vertex as the initial min/max
        minX = pol[0].x()
        maxX = pol[0].x()
        minY = pol[0].y()
        maxY = pol[0].y()

        # Starting index for processing vertices
        i = 1
        
        while i < len(pol):
            vX = pol[i].x()
            vY = pol[i].y()

            # Update min and max x coordinates
            if vX < minX:
                minX = vX
            if vX > maxX:
                maxX = vX
                
            # Update min and max y coordinates   
            if vY < minY:
                minY = vY
            if vY > maxY:
                maxY = vY

            # Move to the next vertex
            i = i + 1

        # Check x coordinate range
        insideX = False
        if q.x() >= minX:
            if q.x() <= maxX:
                insideX = True

        # Check y coordinate range
        insideY = False
        if q.y() >= minY:
            if q.y() <= maxY:
                insideY = True

        # Point is inside the bounding box
        if insideX == True:
            if insideY == True:
                return 1
        # Point is outside the bounding box
        return 0