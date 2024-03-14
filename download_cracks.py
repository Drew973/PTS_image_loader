# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 15:39:58 2024

@author: Drew.Bennett
"""

from image_loader.db_functions import runQuery,prepareQuery,defaultDb,dbFile
from image_loader.layer_styles import styles
from qgis import processing

from qgis.core import QgsFeature,QgsGeometry,edit,QgsWkbTypes
from qgis.utils import iface
#from image_loader import db_functions
#from image_loader.layer_styles.styles import centerStyle
from PyQt5.QtCore import QByteArray,QProcess
from PyQt5.QtWidgets import QProgressDialog,QApplication




from itertools import islice

#split generator into chunks
def chunk(gen, k):
    """Efficiently split `gen` into chunks of size `k`.

       Args:
           gen: Iterator to chunk.
           k: Number of elements per chunk.

       Yields:
           Chunks as a list.
    """ 
    while True:
        chunk = [*islice(gen, 0, k)]
        if chunk:
            yield chunk
        else:
            break




def downloadCracks(gpsModel,progress):
    interval = 50
    uri = "Linestring?crs=epsg:27700&field=frame:int&field=crack_id:int&field=length:real&field=width:real&field=depth:real&index=yes"
    layer = iface.addVectorLayer(uri, 'cracking', "memory")
    fields = layer.fields()
    
    q = runQuery('select count(section_id) from cracks_view')
    while q.next():
        count = q.value(0)
        progress.setRange(0,count)
        
    def features():
        i = 0
        q = runQuery('select section_id,crack_id,len,depth,width,st_asText(geom),chainage_shift,offset from cracks_view')
        while q.next() and not progress.wasCanceled():
            if i%interval == 0:
                progress.setValue(i)
                QApplication.processEvents()
            wkt = q.value(5)
            g = QgsGeometry.fromWkt(wkt)
           # r = g.translate(dx = q.value(6), dy = q.value(7))#add mo correction
           # if not r:
            #    print('failed to translate',r,g,mShift = q.value(6),offset = q.value(7))
            geom = gpsModel.moGeomToXY(g,mShift = q.value(6),offset = q.value(7))
            i += 1
         #   print(geom.asWkt())
         #   print('type',geom.type())
            if geom.type() == QgsWkbTypes.LineGeometry:
                #not QgsWkbTypes.LineString for some reason
                f = QgsFeature(fields)
                f['frame'] = q.value(0)
                f['crack_id'] = q.value(1)
                f['length'] = q.value(2)
                f['width'] = q.value(3)
                f['depth'] = q.value(4)
                f.setGeometry(geom)
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
    layer.loadNamedStyle(styles.crackStyle)
    progress.setValue(progress.maximum())
    progress.close()
    


class downloadRutDialog(QProgressDialog):
    def __init__(self,parent = None):
        super().__init__(parent)
        self.setAutoClose(False)
        self.setLabelText('Recalculating rutting geometry...')


    def downloadRuts(self,gpsModel,saveTo,chunkSize = 100):
        db = defaultDb()
        db.transaction()
        q = runQuery('select count(frame) from rut_view',db = db)
       
        #set range
        while q.next():
            count = q.value(0)
        self.setRange(0,count+100)
        
        #update geom column of rut
        q = runQuery('select pk,chainage_shift,offset,mo_wkb from rut_view',db=db)##########test
        updateQuery = prepareQuery('update rut set geom = PolygonFromWKB(?,27700) where pk = ?', db= db)##########test
        
        i = 0
        while q.next():
            g = QgsGeometry()
            wkb = q.value(3)
            if isinstance(wkb,QByteArray):
                g.fromWkb(wkb)
                geom = gpsModel.moGeomToXY(g,mShift = q.value(1),offset = q.value(2))
                
                if i == 0:
                    print('g',g,'geom',geom)
                
                updateQuery.bindValue(0,geom.asWkb())
                updateQuery.bindValue(1,int(q.value(0)))
                updateQuery.exec()
            self.setValue(i)
            if i%chunkSize == 0:
                QApplication.processEvents()
            i+=1            
        db.commit()   
        
        #copy rut table to geopackage
       # to = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\ruts.gpkg'
     #   command = 'ogr2ogr "{to}" "{db}" -sql "select frame,chainage,wheelpath,width,depth,type,deform,x_section,geom from rut_view" -t_srs EPSG:27700 -s_srs EPSG:27700 -nln rutting -overwrite'.format(to = saveTo,
                                                                                                                                                                                                            # db = dbFile())
       # print(command)
    #    p = QProcess()
    #    p.start(command)
     #   p.waitForFinished()#~5s
        
        #load it
      #  source = saveTo + '|layername=rutting'
       # layer = iface.addVectorLayer(source, "rutting", "ogr")
        #  layer.loadNamedStyle(styles.crackStyle)    
        
        #run processing algorithm. can make tempuary layer this way.
        params = { 'INPUT' : 'spatialite://dbname=\'{db}\' table=\"runs_view\"'.format(db = dbFile()), 'OPTIONS' : '-sql \"select frame,chainage,wheelpath,width,depth,type,deform,x_section,geom from rut_view\" -t_srs EPSG:27700 -s_srs EPSG:27700 -nln rutting -overwrite', 'OUTPUT' : 'TEMPORARY_OUTPUT' }
        r = processing.run('gdal:convertformat',params)
        layer = iface.addVectorLayer(r['OUTPUT'], "Rutting", "ogr")
        layer.setName('Rutting')
        self.setValue(self.maximum())
        return
            

#import cProfile

def downloadRuts(gpsModel,saveTo = None):
   # pr = cProfile.Profile()
   # pr.enable()
    
    d = downloadRutDialog()
    d.downloadRuts(gpsModel = gpsModel,saveTo=saveTo)
    d.close()
  #  pr.disable()
  #  pr.dump_stats(r"C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\download_ruts.prof")
    #   snakeviz C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\download_ruts.prof
  
    
    
    