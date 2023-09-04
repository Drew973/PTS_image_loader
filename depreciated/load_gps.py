
import csv
from qgis.core import QgsCoordinateTransform,QgsCoordinateReferenceSystem,QgsProject,QgsFeature,QgsGeometry,edit
from qgis.utils import iface


def loadGpsLines(file,name='gps'):
    uri = "Linestring?crs=epsg:27700&field=startM:double&field=endM:double&index=yes"
    layer = iface.addVectorLayer(uri, name, "memory")
    fields = layer.fields()
    
    transform = QgsCoordinateTransform(QgsCoordinateReferenceSystem('EPSG:4326'),
        QgsCoordinateReferenceSystem('EPSG:27700'),
        QgsProject.instance())    
    
    
    def features(file):
        with open(file,'r') as f:
            reader = csv.DictReader(f)
            lastPt = None
            lastM = None
            for i,d in enumerate(reader):
                m = float(d['Chainage (km)'])*1000
                x = float(d['Longitude (deg)'])
                y = float(d['Latitude (deg)'])
                pt = transform.transform(x,y)
            
                if lastM is not None and lastPt is not None:
                    f = QgsFeature(fields)
                    f['startM'] = lastM
                    f['endM'] = m
                    f.setGeometry(QgsGeometry.fromPolylineXY([lastPt,pt]))
                    yield f                    
                lastPt = pt
                lastM = m
            
    with edit(layer):
         layer.addFeatures(features(file))
    
    
def testLoadGps():
    f =r'D:\RAF Shawbury\Hawkeye Exported Data\MFV1_013-rutacd-1.csv'
    loadGpsLines(f)
    
if __name__ == '__console__':
    testLoadGps()
