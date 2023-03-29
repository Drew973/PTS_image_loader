# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 15:18:57 2023
@author: Drew.Bennett
test different methods here.
"""


#'GDAL translate command to add GCPS to raster'
def GCPCommand(gcp):
    #-gcp <pixel> <line> <easting> <northing>
    return '-gcp {pixel} {line} {x} {y}'.format(pixel = gcp.GCPPixel,
        line = gcp.GCPLine,
        x = gcp.GCPX,
        y = gcp.GCPY)



from osgeo import gdal
import subprocess
import os

'''
dstalpha creates alpha band for no data


find new geotransform?. set through
ds.SetGeoTransform(gt_new)
should change gcps without having to rewrite.
will rotation be correct?


multiple subprocess in paralell?
from subprocess import Popen
commands = ['command1', 'command2']
procs = [ Popen(i) for i in commands ]
for p in procs:
   p.wait()



'''
def remakeImage(origonal,to,GCPs,grayscale = True):
    temp = os.path.join(os.path.dirname(to),'temp.vrt')
    translateCommand = 'gdal_translate -a_srs "EPSG:27700" {g} -r bilinear "{f}" "{to}"'.format(
    g = ' '.join([GCPCommand(p) for p in GCPs]),
    f = origonal,
    to=temp)
    if grayscale:
        translateCommand += ' -b 1 -colorinterp_1 gray'
    #print(translateCommand)
    subprocess.check_call(translateCommand,creationflags = subprocess.CREATE_NO_WINDOW)
    warpCommand = 'gdalwarp -of COG -co NUM_THREADS=ALL_CPUS -co COMPRESS=JPEG -co QUALITY=75 -t_srs "EPSG:27700" -r bilinear -tps -dstalpha -overwrite "{s}" "{d}" '.format(
        s=temp,
        d=to
        )
    try:
        subprocess.check_call(warpCommand,creationflags = subprocess.CREATE_NO_WINDOW)
        return to
    except:
        return ''
    # if os.path.isfile(temp):
    #     os.remove(temp)




def remakeCommand(origonal,to,GCPs,grayscale = True):
    
    
    temp = os.path.join(os.path.dirname(to),os.path.basename(to)+'.vrt')
    translateCommand = 'gdal_translate -a_srs "EPSG:27700" {g} -r bilinear "{f}" "{to}"'.format(
    g = ' '.join([GCPCommand(p) for p in GCPs]),
    f = origonal,
    to=temp)
    if grayscale:
        translateCommand += ' -b 1 -colorinterp_1 gray'
    #print(translateCommand)
   
    warpCommand = 'gdalwarp -of COG -co NUM_THREADS=ALL_CPUS -co COMPRESS=JPEG -co QUALITY=75 -t_srs "EPSG:27700" -r bilinear -tps -dstalpha -overwrite "{s}" "{d}" '.format(
        s=temp,
        d=to
        )
    
    return translateCommand + ' ; ' + warpCommand
  
    
    
    
    

if __name__ in ('__console__'):

    from qgis.core import QgsRasterLayer
    
    WIDTH = 4.0
    PIXELS = 1038
    LINES = 1250
    
    
    gcps = [ gdal.GCP(354936.334,322907.213,0,0,0),#tl
        gdal.GCP(354937.341,322903.420,0,PIXELS,0),#tr
        gdal.GCP(354931.769,322906.206,0,0,LINES),#bl
        gdal.GCP(354932.608,322902.245,0,PIXELS,LINES)]
    
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000000.jpg'
    to = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\outputs\0000.tif'
         
    remakeImage(f,to,gcps)
    layer = QgsRasterLayer(to,'test')
    
    QgsProject.instance().addMapLayer(layer)
