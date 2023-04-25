from osgeo import gdal, osr


def georeference(file,GCPs):
    
    noData = 255 #max size of unsigned int
    ds = gdal.Open(file)

    srs = osr.SpatialReference()
    srs.ImportFromEPSG(27700)
    ds.SetProjection(srs.ExportToWkt())
    
    
    wkt = ds.GetProjection()
    ds.SetGCPs(GCPs, wkt)
    ds.GetRasterBand(1).SetNoDataValue(noData)
    ds.GetRasterBand(2).SetNoDataValue(noData)
    ds.GetRasterBand(3).SetNoDataValue(noData)

    
  #  ds.BuildOverviews

    ds.FlushCache()
    ds = None
   
    

#'GDAL translate command to add GCPS to raster'
def _GCPCommand(gcp):
    #-gcp <pixel> <line> <easting> <northing>
    return '-gcp {pixel} {line} {x} {y}'.format(pixel = gcp.GCPPixel,
        line = gcp.GCPLine,
        x = gcp.GCPX,
        y = gcp.GCPY)



def overviewCommand(file):
    return 'gdaladdo "{}" 2 4 8 16 --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL'.format(file)


import subprocess


def editCommand(file,gcps):
    g = ' '.join([_GCPCommand(gcp) for gcp in gcps])
    return 'gdal_edit "{file}" -ro -a_srs "EPSG:27700" -a_nodata 255 {gcp}'.format(file=file,gcp=g)
    


def editArgs(file,gcps):
    return ['"{file}"'.format(file=file), '-ro','-a_srs', '"EPSG:27700"','-a_nodata 255'] + [_GCPCommand(gcp) for gcp in gcps]

from PyQt5.QtCore import QProcess




def test():
    PIXELS = 1038
    LINES = 1250

    gcps = [ gdal.GCP(354936.334,322907.213,0,0,0),#tl
            gdal.GCP(354937.341,322903.420,0,PIXELS,0),#tr
            gdal.GCP(354931.769,322906.206,0,0,LINES),#bl
            gdal.GCP(354932.608,322902.245,0,PIXELS,LINES)]

    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000001.jpg'


   # c = editCommand(f,gcps)
   # print(c)

    p = QProcess()
    args = editArgs(f,gcps)
    
    p.finished.connect(finished)

    prog = r'C:\OSGeo4W\apps\Python39\Scripts\gdal_edit'
    p.start(prog, args)
    p.waitForFinished()
    print(p.error())
    return p

    #print(overviewCommand(f))

    #tested these in osgeo4w shell
    
def finished(exitCode, exitStatus):
    print('code',exitCode)
        
    if exitStatus()==QProcess.NormalExit:
        print('success')
    else:
        print('error')
    
    
if __name__ == '__console__':
    t = test()