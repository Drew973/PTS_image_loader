from osgeo import gdal,ogr
import os
from qgis.core import QgsGeometry,QgsPointXY


#{x,y}
def toMapCoordsDict(pixel,line,gt):
    return {'x':gt[0] + pixel * gt[1] + line * gt[2], 'y': gt[3] + pixel * gt[4] + line * gt[5]}


def toMapCoords(pixel,line,gt):
    return QgsPointXY(gt[0] + pixel * gt[1] + line * gt[2], gt[3] + pixel * gt[4] + line * gt[5])

#extents of raster as ogr.Geometry
#can get wkt with ExportToWkt()
#wkb with ExportToWkb()
def rasterExtents_ogr(file):
    data = gdal.Open(file, gdal.gdalconst.GA_ReadOnly)
    if not data is None:
        gt = data.GetGeoTransform()
        
        r = ogr.Geometry(ogr.wkbLinearRing)

        p = toMapCoordsDict(0,0,gt)
        r.AddPoint_2D (p['x'],p['y'])
        p = toMapCoordsDict(0,data.RasterYSize,gt)
        r.AddPoint_2D (p['x'],p['y'])
        p = toMapCoordsDict(data.RasterXSize,data.RasterYSize,gt)
        r.AddPoint_2D (p['x'],p['y'])
        p = toMapCoordsDict(data.RasterXSize,0,gt)
        r.AddPoint_2D (p['x'],p['y'])

        
        data = None
        #return r
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(r)
        return poly


#slow but simpler. useful for testing.
def rasterExtents_info(file):
    if os.path.exists(file):
        d = gdal.Info(file, format='json')['cornerCoordinates']
        r = ogr.Geometry(ogr.wkbLinearRing)
        for c in ['upperLeft','lowerLeft','lowerRight','lowerRight']:
            r.AddPoint(d[c][0],d[c][1])
            
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(r)
        return poly
            


#extents of raster as QgsPolygon
def rasterExtents(file):
    data = gdal.Open(file, gdal.gdalconst.GA_ReadOnly)
    if not data is None:
        gt = data.GetGeoTransform()
        
        return QgsGeometry.fromPolygonXY([[toMapCoords(0,0,gt),
                                          toMapCoords(0,data.RasterYSize,gt),
                                         toMapCoords(data.RasterXSize,data.RasterYSize,gt),
                                         toMapCoords(data.RasterXSize,0,gt)]])
       

   



'''
    extents of non 0 pixels:
    corners each touch edge of full image.
    handle where multiple non 0 values along edge:
        find furthest non 0 point in clockwise direction.
    
    0,0 at top left.
        left : 0,min(row where non 0)
        top: max(col where non 0) ,0
        rignt : width,max(row where non 0)
        top: nim(col where non 0) ,height

    
    
    

'''


