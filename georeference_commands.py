# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 12:50:38 2024

@author: Drew.Bennett
chain gdal commands?
Not opening python interpreter every process might be more efficient
"""

import os
import platform

from image_loader import georeference

s = platform.system()


def warpedFileName(origonalFile):
    return os.path.splitext(origonalFile)[0] + '_warped.tif'


def sibling(file,newFile):
    return os.path.join(os.path.dirname(__file__),newFile)


def changeExt(file,ext):
    return os.path.splitext(file)[0] + ext


def translateCommand(inputFile,gcps,intermediate):
    g = ['-gcp {pixel} {line} {easting} {northing}'.format(pixel = p[2],line = p[3],easting = p[0],northing = p[1]) for p in gcps]
    return 'gdal_translate "{inputFile}" "{outputFile}" {gcp} -b 1 -colorinterp_1 gray -a_srs EPSG:27700'.format(gcp = ' '.join(g),inputFile = inputFile,outputFile = intermediate)


def warpCommand(intermediate,outputFile):
    return 'gdalwarp -dstnodata 0  -r near -of COG -overwrite -co quality=60 -co compress=JPEG'\
        ' -co OVERVIEWS=IGNORE_EXISTING "{intermediate}" "{outputFile}" '.format(intermediate = intermediate,outputFile = outputFile)
    

def georeferenceCommand(inputFile:str , gcps:str , srid:int) -> str:
#    gcpList = ['-gcp {pixel} {line} {easting} {northing}'.format(pixel = p[2],line = p[3],easting = p[0],northing = p[1]) for p in gcps]
  #  gcp = ' '.join(gcpList)
    dest = warpedFileName(inputFile)
   # intermediate = changeExt(inputFile,'.vrt')
    #intermediate = r'/vsimem/' + changeExt(os.path.basename(inputFile),'.vrt')
    if s == 'Windows' and False:
        pass
        #testing windows specific batch file.
        #would expect batch file to be faster than opening python interpreter. doesn't seem to be
  #      batchFile = sibling(__file__,'georeference.bat')
   #     return '{bf} "{i}" "{gcp}" "{vrt}" "{dest}"'.format(bf = batchFile, i = inputFile, gcp = gcp, vrt = intermediate , dest = dest)
    else:
        return 'python "{script}" "{i}" "{dest}" "{gcps}" {srid}'.format(i = inputFile,
                                                          script = georeference.__file__,
                                                          dest = dest,
                                                          gcps = gcps,
                                                          srid = srid)



if __name__ in ('__main__','__console__'):
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\ImageInt\2023-01-21 10h08m11s LCMS Module 1 002703.jpg'
    gcps = '[[354537.8412658522, 321846.43105571566, 0, 1250], [354532.847262905, 321847.57317921636, 0, 0], [354538.62003033806, 321850.3545141232, 1038, 1250], [354533.8395471249, 321851.44814657455, 1038, 0]]'
    
    cc = georeferenceCommand(f , gcps , 27700)
    print('command',cc,'\n\n')

    from PyQt5.QtCore import QProcess
    proc = QProcess()
    proc.start(cc)
    proc.waitForFinished()
    err = proc.readAllStandardError()
    
    print('err',err)

