from osgeo import gdal,ogr
import os

#from qgis.core import QgsGeometry

#extents of raster as ogr.Geometry
#can get wkt with ExportToWkt()
#wkb with ExportToWkb()
def rasterExtents(file):
    data = gdal.Open(file, gdal.gdalconst.GA_ReadOnly)
    if not data is None:
        geoTransform = data.GetGeoTransform()
        minX = geoTransform[0]
        maxY = geoTransform[3]
        maxX = minX + geoTransform[1] * data.RasterXSize
        minY = maxY + geoTransform[5] * data.RasterYSize
        data = None
        
        r = ogr.Geometry(ogr.wkbLinearRing)
        #r = ogr.Geometry(ogr.wkbPolygon)
        
        r.AddPoint(minX,minY)
        r.AddPoint(minX,maxY)
        r.AddPoint(maxX,maxY)
        r.AddPoint(maxX,minY)
        r.AddPoint(minX,minY)
        poly = ogr.Geometry(ogr.wkbPolygon)
        poly.AddGeometry(r)
        return poly
        #return r.ExportToWkt()
        
     #   r = QgsGeomerty()
     #   r.addPointsXY
        
        #asPolygon

#slow but simpler.
def rasterExtents2(file):
    if os.path.exists(file):
        d = gdal.Info(file, format='json')['cornerCoordinates']
        r = ogr.Geometry(ogr.wkbLinearRing)
        for c in ['upperLeft','lowerLeft','lowerRight','lowerRight']:
            r.AddPoint(d[c][0],d[c][1])
        return r

