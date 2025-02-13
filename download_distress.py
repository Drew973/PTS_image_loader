# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 15:39:58 2024

@author: Drew.Bennett
"""

from image_loader.db_functions import runQuery,prepareQuery,defaultDb

from image_loader import file_locations,settings

from qgis import processing

from qgis.core import QgsFeature,QgsGeometry,edit,QgsWkbTypes
from qgis.utils import iface
from PyQt5.QtCore import QByteArray,Qt
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
    srid = settings.destSrid()
    uri = "Linestring?crs=epsg:{srid}&field=frame:int&field=crack_id:int&field=length:real&field=width:real&field=depth:real&index=yes".format(srid = srid)
    layer = iface.addVectorLayer(uri, 'cracking', "memory")
    fields = layer.fields()
    
    q = runQuery('select count(section_id) from cracks_view')
    while q.next():
        count = q.value(0)
        progress.setRange(0,count)
        
    def features():
        i = 0
        q = runQuery('select section_id,crack_id,len,depth,width,wkt,chainage_shift,offset from cracks_view')
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
    layer.loadNamedStyle(file_locations.crackStyle)
    progress.setValue(progress.maximum())
    progress.close()
    







#updating database then using gdal:convertformat.
#faster than layer.addFeatures.
  
def downloadRuts(gpsModel,saveTo,parent = None):
    db = defaultDb()
    db.transaction()
    q = runQuery('select count(frame) from rut_view',db = db)
    #set range
    while q.next():
        count = q.value(0)
    d = QProgressDialog(parent = parent)
    d.setWindowModality(Qt.WindowModal);
    d.setLabelText('Recalculating rutting geometry...')
    d.setRange(0,count+1)
    d.show()        

    #update geom column of rut
    q = runQuery('select pk,chainage_shift,offset,mo_wkb from rut_view',db=db)##########test
    updateQuery = prepareQuery('update rut set xy_wkb = ? where pk = ?', db= db)##########test  PolygonFromWKB(?,27700)
    
    i = 0
    while q.next() and not d.wasCanceled():
        g = QgsGeometry()
        wkb = q.value(3)
        if isinstance(wkb,QByteArray):
            g.fromWkb(wkb)
            geom = gpsModel.moGeomToXY(g,mShift = q.value(1),offset = q.value(2))
            updateQuery.bindValue(0,geom.asWkb())
            updateQuery.bindValue(1,int(q.value(0)))
            updateQuery.exec()
        d.setValue(i)
        i+=1            
    db.commit()   
    
    if not d.wasCanceled():
        d.setLabelText('Loading layer...')

        srid = settings.destSrid()
        #copy to geopackage using processing algorithm. can make tempuary layer this way.
        params = { 'INPUT' : 'spatialite://dbname=\'{db}\' table=\"runs_view\"'.format(db = file_locations.dbFile),
                  'OPTIONS' : '-sql \"select frame,chainage,wheelpath,width,depth,type,deform,x_section,GeomFromWKB(xy_wkb) from rut_view\" -t_srs EPSG:{srid} -s_srs EPSG:{srid} -nln rutting -overwrite'.format(srid = srid),
                  'OUTPUT' : 'TEMPORARY_OUTPUT' }
        
        r = processing.run('gdal:convertformat',params)
        layer = iface.addVectorLayer(r['OUTPUT'], "Rutting", "ogr")
        layer.setName('Rutting')
        d.setValue(d.maximum())
            


    




#def recalcFaultingGeom(gpsModel):
    


#faulting,width
##########finish this
def downloadFaulting(gpsModel,parent = None):
    
    srid = settings.destSrid()
    uri = "Polygon?crs=epsg:{srid}&field=frame:int&field=joint_id:int&field=joint_offset:int&field=faulting:real&field=width:real&index=yes".format(srid = srid)
    layer = iface.addVectorLayer(uri, 'transverse joint faulting', "memory")
    fields = layer.fields()
    q = runQuery('select count(frame) from faulting_view')
    #set range
    while q.next():
        count = q.value(0)
    d = QProgressDialog(parent = parent)
    d.setWindowModality(Qt.WindowModal);
    d.setLabelText('Loading faulting...')
    d.show()        
    d.setRange(0,count)    
    
    def features():
        q = runQuery('select mo_wkb,chainage_shift,left_offset,frame,joint_id,joint_offset,faulting,width from faulting_view')##########test
        i = 0
        while q.next() and not d.wasCanceled():
            wkb = q.value(0)
            if isinstance(wkb,QByteArray):
                g = QgsGeometry()
                g.fromWkb(wkb)
                geom = gpsModel.moGeomToXY(g,mShift = q.value(1),offset = q.value(2))
                #print(geom.asWkt())#Polygon(...)
                f = QgsFeature(fields)
                f['frame'] = q.value(3)
                f['joint_id'] = q.value(4)
                f['joint_offset'] = q.value(5)
                f['faulting'] = q.value(6)
                f['width'] = q.value(7)
                f.setGeometry(geom)
                yield f
            if i%100 == 0:#setValue slow. due to calling processEvents as modal. Balance responsiveness vs performance.
                d.setValue(i)
            i+=1
            
    with edit(layer):
        if not layer.addFeatures(features()):#False
            print(layer.lastError())

    d.setValue(d.maximum())
    return layer
    
