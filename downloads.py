# -*- coding: utf-8 -*-
"""


functions to download data as qgis layers.


Created on Thu Feb 29 15:39:58 2024

@author: Drew.Bennett
"""

from image_loader.db_functions import runQuery,prepareQuery,defaultDb,queryError
from image_loader.backend import corrections_functions
from image_loader import file_locations,settings , dims
from qgis import processing
from qgis.utils import iface
from PyQt5.QtCore import QByteArray,Qt
from PyQt5.QtWidgets import QProgressDialog,QApplication
from qgis.core import QgsFeature,QgsGeometry,edit,QgsPointXY,QgsVectorLayer,QgsProject,QgsWkbTypes
from image_loader import group_functions
from image_loader.backend import gps_functions





#from itertools import islice
'''
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
'''








#make layer with centerlines.
#1 feature per frame.
#might have less than 1 point/frame if using shapefile geom.
# different results if reproject in QGIS vs in spatialite.experiment with this.
def downloadGps() -> QgsVectorLayer:
    
    s = gps_functions.getSplineString()
    if s is not None:
        
        uri = "LineString?crs=epsg:{p}&field=frame:int&field=start_chain:int&field=end_chain:int&index=yes".format(p = settings.destSrid())    
        layer = QgsVectorLayer(uri,'original_GPS',"memory")
        
        fields = layer.fields()
        
        maxFrame = dims.mToFrame(gps_functions.maxM())
                                 
                                 
        def features():
            for frame in range(0,maxFrame+1):
                f = QgsFeature(fields)
                startChain = dims.frameToM(frame)
                endChain = startChain + dims.HEIGHT
                f['start_chain'] = startChain
                f['end_chain'] = endChain
                f['frame'] = frame
                points = s.centerLinePoint([startChain,endChain])#array [(x1,y1),(x2,y2)]
                geom = QgsGeometry.fromPolylineXY([QgsPointXY(points[0,0],points[0,1]),QgsPointXY(points[1,0],points[1,1])])
                f.setGeometry(geom)
                if f.isValid():
                    yield f
                    
        with edit(layer):
             layer.addFeatures(features())
        layer.loadNamedStyle(file_locations.centerStyle)
       # load_image.loadLayer(layer)
        group = group_functions.getGroup(['image_loader'])#QgsLayerTreeGroup
        group.addLayer(layer)
    
        node = group.findLayer(layer)
        node.setItemVisibilityChecked(True)
        node.setExpanded(False)        
        QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
        return layer




def downloadCracks(progress) -> QgsVectorLayer:
    progressInterval = 100
    srid = settings.destSrid()
    uri = "Linestring?crs=epsg:{srid}&field=frame:int&field=crack_id:int&field=length:real&field=width:real&field=depth:real&index=yes".format(srid = srid)
    layer = iface.addVectorLayer(uri, 'cracking', "memory")
    fields = layer.fields()
    
    q = runQuery('select count(section_id) from cracks inner join runs on section_id>= start_frame and section_id <= end_frame')
    while q.next():
        count = q.value(0)
        progress.setRange(0,count)
        
    def features():
        i = 0
        lastRun = None
        spline = None
        
        q = runQuery('select runs.pk,section_id,crack_id,len,depth,width,wkt from cracks inner join runs on section_id>= start_frame and section_id <= end_frame order by runs.pk')
        
        while q.next() and not progress.wasCanceled():
            if i%progressInterval == 0:
                progress.setValue(i)
                QApplication.processEvents()
                
            if lastRun != q.value(0):
                    spline = corrections_functions._getCorrectedSpline(q.value(0))
                    lastRun = q.value(0)
                
            if spline is not None:
                wkt = q.value(6)
                geom = spline.moGeomToXY(geom = QgsGeometry.fromWkt(wkt))

                if geom.type() == QgsWkbTypes.LineGeometry:
                    #not QgsWkbTypes.LineString for some reason
                    f = QgsFeature(fields)
                    f['frame'] = q.value(1)
                    f['crack_id'] = q.value(2)
                    f['length'] = q.value(3)
                    f['width'] = q.value(4)
                    f['depth'] = q.value(5)
                    f.setGeometry(geom)
                    yield f
                    
            i += 1

    with edit(layer):
         layer.addFeatures(features())
    layer.loadNamedStyle(file_locations.crackStyle)
    progress.setValue(progress.maximum())
    progress.close()
    return layer





  
def downloadRuts(saveTo = None , parentWidget = None , progressInterval = 100):
    
    srid = settings.destSrid()
    
    db = defaultDb()
    db.transaction()
    q = runQuery('select count(frame) from rut_view',db = db)
    #set range
    while q.next():
        count = q.value(0)
    d = QProgressDialog(parent = parentWidget)
    d.setWindowModality(Qt.WindowModal);
    d.setLabelText('Loading rutting...')
    d.setRange(0,count+1)
    d.show()        
    
    uri = "Polygon?crs=epsg:{srid}&field=frame:int&field=chainage:realt&field=wheelpath:string&field=width:real&field=depth:real&field=type:int&field=deform:real&field=x_section:real&index=yes".format(srid = srid)
    layer = iface.addVectorLayer(uri, 'rutting', "memory")
    
    fields = layer.fields()
    
    
    def rutFeatures():
        i = 0
        lastRun = None
        spline = None
        q = runQuery('select run_pk,rut_pk,mo_wkb,frame,chainage,wheelpath,depth,width,type,deform,x_section from rut_view order by run_pk',db=db)   

        while q.next() and not d.wasCanceled():
            
            runPk = q.value(0)
            if runPk != lastRun:
                lastRun = runPk
                spline = corrections_functions._getCorrectedSpline(runPk)
            
            if spline is not None:
                g = QgsGeometry()
                wkb = q.value(2)
                if isinstance(wkb,QByteArray):
                    g.fromWkb(wkb)
                    newGeom = spline.moGeomToXY(geom = g)                  
                    f = QgsFeature(fields)
                    f.setGeometry(newGeom)
                    f['frame'] = q.value(3)
                    f['chainage'] = q.value(4)
                    f['wheelpath'] = q.value(5)
                    f['depth'] = q.value(6)
                    f['width'] = q.value(7)
                    f['type'] = q.value(8)
                    f['deform'] = q.value(9)
                    f['x_section'] = q.value(10)
                    yield f
                                                
            if i%progressInterval ==0:
                d.setValue(i)
            i+=1            
                
    db.commit()   
    with edit(layer):
        layer.addFeatures(rutFeatures())
    
    layer.setName('Rutting')
    d.setValue(d.maximum())
    return layer


    

#faulting,width
##########finish this
def downloadFaulting(parent = None):
    
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
        q = runQuery('select run_pk,mo_wkb,frame,joint_id,joint_offset,faulting,width from faulting_view')##########test
        i = 0
        lastRun = None
        spline = None
        while q.next() and not d.wasCanceled():
            run = q.value(0)
            if run != lastRun:
                lastRun = run
                spline = corrections_functions._getCorrectedSpline(run)
            
            if spline:
                wkb = q.value(1)
                if isinstance(wkb,QByteArray):
                    g = QgsGeometry()
                    g.fromWkb(wkb)
                    geom = spline.moGeomToXY(g)
                    #print(geom.asWkt())#Polygon(...)
                    f = QgsFeature(fields)
                    f['frame'] = q.value(2)
                    f['joint_id'] = q.value(3)
                    f['joint_offset'] = q.value(4)
                    f['faulting'] = q.value(5)
                    f['width'] = q.value(6)
                    f.setGeometry(geom)
                    yield f
            if i%100 == 0:#setValue slow. due to modal QProgressDialog calling processEvents. Balance responsiveness vs performance.
                d.setValue(i)
            i+=1
            
    with edit(layer):
        if not layer.addFeatures(features()):#False
            print(layer.lastError())

    d.setValue(d.maximum())
    return layer
    



#move this?
#currently for debugging only

def downloadCorrectedPoints() -> None:
    uri = "Point?crs=epsg:{p}&field=m:int&index=yes".format(p = settings.destSrid())    
    layer = QgsVectorLayer(uri,'corrected_centerline',"memory")
    print(layer)
    fields = layer.fields()
               
    def features():
        q = runQuery('select m , x, y from corrected_points')
        while q.next():
            f = QgsFeature(fields)
            f['m'] = q.value(0)
            geom = QgsGeometry.fromPointXY(QgsPointXY(q.value(1),q.value(2)))
            f.setGeometry(geom)
            if f.isValid():
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
  
    group = group_functions.getGroup(['image_loader'])#QgsLayerTreeGroup
    group.addLayer(layer)

    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    node.setExpanded(False)        
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend


