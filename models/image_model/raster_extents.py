from osgeo import gdal,ogr
import os

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
        r.AddPoint(minX,minY)
        r.AddPoint(minX,maxY)
        r.AddPoint(maxX,maxY)
        r.AddPoint(maxX,minY)
        r.AddPoint(minX,minY)
        return r
        #return r.ExportToWkt()

#slower
def rasterExtents2(file):
    if os.path.exists(file):
        d = gdal.Info(file, format='json')['cornerCoordinates']
        r = ogr.Geometry(ogr.wkbLinearRing)
        for c in ['upperLeft','lowerLeft','lowerRight','lowerRight']:
            r.AddPoint(d[c][0],d[c][1])
        return r


if __name__ == '__console__':
    #data uses transform rather than gcps. data.GetGCPs()=[]
    image = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000004.tif'
    data = gdal.Open(image, gdal.gdalconst.GA_ReadOnly)
    d = gdal.Info(image, format='json')

    print(rasterExtents2(image))