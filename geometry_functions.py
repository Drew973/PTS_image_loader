#make rectangle from bottom left corner, top right corner,width
#QgsPointXY
import numpy


from qgis.core import QgsGeometry,QgsPointXY,QgsPoint

#numpy array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5

#right
def perpendicular(vector):
    return numpy.array([vector[1],-vector[0]])


#angle in radians. negative for clockwise rotation.
#https://en.wikipedia.org/wiki/Rotation_matrix
def rotateVector(vector,angle):
    return numpy.matmul(vector,numpy.array([[numpy.cos(angle),-numpy.sin(angle)],[numpy.sin(angle),numpy.cos(angle)]]))


def pointToVector(p):
    return numpy.array([p.x(),p.y()])


def vectorToPointXY(v):
    return QgsPointXY(v[0],v[1])



def startPoint(geom):
    return geom.vertexAt(0)
    
    
def endPoint(geom):
    return geom.interpolate(geom.length()).vertexAt(0)
    


#QgsPoint
def interpolateBetweenPoints(s,e,fraction):
    sv = numpy.array([s.x(),s.y(),s.z(),s.m()])
    ev = numpy.array([e.x(),e.y(),e.z(),e.m()])
    v = sv + fraction * (ev-sv)
    return QgsPoint(v[0],v[1],v[2],v[3])
    

#linestringM.
#supports z dimension
#offset in crs units. negative for left
#returns QgsPoint
def measureToPoint(geometry,measure,offset=0):
    p = None
    n = None
    for v in geometry.vertices():
        if p is None or v.m()< measure:
            p = v
        
        if v.m()>measure:
            n = v
            break
            
    if n is None:
        n = v
        
    #vector notation
    #p = previous vertex or startPoint.
    #n = next vertex or end.
    #o = origin
    
    op =  numpy.array([p.x(),p.y(),p.z()]) 
    on =  numpy.array([n.x(),n.y(),p.z()]) 
    pn = on-op
    
    if n.m()-p.m()==0:
      #  print('next point',n)
      #  print('previous point',p)
  #      print(geometry)
        return QgsPoint()
    
    frac = (measure-p.m())/(n.m()-p.m())
   # print(pn[0:2])
    
    left = numpy.array([ pn[1],-pn[0]]) #(x,y) -> (y,-x)
    leftUnitVector = left/numpy.sqrt(numpy.sum(left**2))

   # print(leftUnitVector)

    v = op + frac * pn + numpy.append(leftUnitVector,0) * offset
    return QgsPoint(x=v[0],y=v[1],z=v[2],m=measure)
    

#only works if measure increases linearly with distance
#empty if measure not between start and end
def interpolatePoint(linestringM,measure):
    startM = startPoint(linestringM).m()
    endM = endPoint(linestringM).m()
    return linestringM.interpolate((measure - startM) * linestringM.length()/(endM-startM)).vertexAt(0)



def pointsAroundMeasure(line,measure):
    p = None
    n = None
    for v in line.vertices():
        if p is None or v.m()< measure:
            p = v
        
        if v.m()>measure:
            n = v
            break
            
    if n is None:
        n = v
    
    return p,n
        
#shift by chainage and offset
#->QgsPoint
def addChainage(point,linestringM,measure,offset):
    m = pointToMeasure(point,linestringM)
    return measureToPoint(geometry = linestringM , measure = m['measure']+measure, offset = m['offset']+offset)
    


#QgsPointXY->{'measure':float,'offset':float}
def pointToMeasure(point,line):
    d = line.lineLocatePoint(QgsGeometry.fromPointXY(QgsPointXY(point.x(),point.y())))
    nearest = line.interpolate(d).vertexAt(0)#QgsPoint
    prev,nex = pointsAroundMeasure(line,nearest.m())
    pn = pointToVector(nex)-pointToVector(prev)
    pp = pointToVector(point)-pointToVector(prev)
    
    offset = numpy.cross(pp,pn)/numpy.linalg.norm(pn)
    #https://www.nagwa.com/en/explainers/939127418581/#:~:text=The%20perpendicular%20distance%2C%20%F0%9D%90%B7%20%2C%20between,any%20point%20on%20the%20line.
    
    return {'measure':nearest.m(),'offset':offset} 


#LRS section
'''    
class section:
    
    def __init__(self,lineString):
        self.line = lineString
        
        
    #[QgsPointXY]->[{'measure','offset'}]
    def toMeasureOffset(self,points):
        r = []
        for p in points:
            self.line.nearestPoint(p).vertexAt(0)#QgsGeometry
            
            
    
    
    #[{'chainage','offset'}]->[QgsPointXY]
    def fromMeasureOffsets(self,values):
        points = []
        for v in values:
            points.append(interpolatePoint(self.line,v['measure'],v['offset']))
        return points
    
'''

    
if __name__=='__console__':
    g = QgsGeometry.fromWkt('LinestringM(10 10 0, 1000 1000 100)')
   # s = section(g)
    
    #r = s.fromMeasureOffsets([{'measure':0,'offset':5}])
    #print(r)
    print(pointToMeasure(QgsPointXY(10,0),g))
    print(pointToMeasure(QgsPointXY(0,0),g))
    print(pointToMeasure(QgsPointXY(0,10),g))

    