# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 15:39:58 2024

@author: Drew.Bennett
"""

from image_loader.db_functions import runQuery
from image_loader.layer_styles import styles

from qgis.core import QgsFeature,QgsGeometry,edit,QgsWkbTypes,QgsTask
from qgis.utils import iface
#from image_loader import db_functions
#from image_loader.layer_styles.styles import centerStyle
from PyQt5.QtCore import QThread,pyqtSignal



def downloadCracks(gpsModel,progress):
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
            progress.setValue(i+1)
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
    
    
class layerLoader(QThread):
    
    
    countChanged = pyqtSignal(int)
    
    
    def __init__(self,gpsModel,progress,parent = None):
        super().__init__(parent=parent)
        self.gpsModel = gpsModel
        self.progress = progress

    def run(self):
        downloadRuts()



class downloadRutsTask(QgsTask):
        
    def run(self,gpsModel):
     
        #taskCompleted.connect
        uri = "Polygon?crs=epsg:27700&field=frame:int&field=chainage:real&field=wheelpath:string&field=depth:real&field=width:real&field=x_section:real&field=type:int&field=deform:real&index=yes"
        layer = iface.addVectorLayer(uri, 'Rutting', "memory")
        fields = layer.fields()
       
        q = runQuery('select count(frame) from rut_view')
        while q.next():
            count = q.value(0)
            
            
        def features():
            i = 0
            q = runQuery('select frame,chainage,wheelpath,width,depth,type,deform,chainage_shift,offset,st_asText(geom) from rut_view')##########test
            while q.next():
                if self.isCanceled():
                    return False
            
                self.setProgress(int(i/count * 100))
                
                wkt = q.value(9)
                g = QgsGeometry.fromWkt(wkt)
               # r = g.translate(dx = q.value(6), dy = q.value(7))#add mo correction
               # if not r:
                #    print('failed to translate',r,g,mShift = q.value(6),offset = q.value(7))
                geom = gpsModel.moGeomToXY(g,mShift = q.value(7),offset = q.value(8))
                i += 1
                if i == 1:
                    print(geom.asWkt())
                    print('type',geom.type())
                    
                if True:
              #  if geom.type() == QgsWkbTypes.LineGeometry:
                    #not QgsWkbTypes.LineString for some reason
                    f = QgsFeature(fields)
                    f['frame'] = q.value(0)
                    f['chainage'] = q.value(1)
                    f['wheelpath'] = q.value(2)
                    f['width'] = q.value(3)
                    f['depth'] = q.value(4)
                    f['type'] = q.value(5)
                    f['deform'] = q.value(6)
                    f.setGeometry(geom)
                    yield f
                    
                    
        #split into several parts to allow cancelling?
        with edit(layer):
             layer.addFeatures(features())
      #  layer.loadNamedStyle(styles.crackStyle)
        return True





def downloadRuts(gpsModel,progress):
    task = downloadRutsTask()
    progress.setRange(0,100)
    task.progressChanged.connect(progress.setValue)
    progress.canceled.connect(task.cancel)
    task.run(gpsModel = gpsModel)
    
    
    

def old___downloadRuts(gpsModel,progress):
    uri = "Polygon?crs=epsg:27700&field=frame:int&field=chainage:real&field=wheelpath:string&field=depth:real&field=width:real&field=x_section:real&field=type:int&field=deform:real&index=yes"
    layer = iface.addVectorLayer(uri, 'Rutting', "memory")
    fields = layer.fields()
   
    q = runQuery('select count(frame) from rut_view')
    while q.next():
        count = q.value(0)
        progress.setRange(0,count)
        
    def features():
        i = 0
        q = runQuery('select frame,chainage,wheelpath,width,depth,type,deform,chainage_shift,offset,st_asText(geom) from rut_view where frame = 10')##########test
        while q.next() and not progress.wasCanceled():
            progress.setValue(i+1)
            wkt = q.value(9)
            g = QgsGeometry.fromWkt(wkt)
           # r = g.translate(dx = q.value(6), dy = q.value(7))#add mo correction
           # if not r:
            #    print('failed to translate',r,g,mShift = q.value(6),offset = q.value(7))
            geom = gpsModel.moGeomToXY(g,mShift = q.value(7),offset = q.value(8))
            i += 1
            if i == 1:
                print(geom.asWkt())
                print('type',geom.type())
                
            if True:
          #  if geom.type() == QgsWkbTypes.LineGeometry:
                #not QgsWkbTypes.LineString for some reason
                f = QgsFeature(fields)
                f['frame'] = q.value(0)
                f['chainage'] = q.value(1)
                f['wheelpath'] = q.value(2)
                f['width'] = q.value(3)
                f['depth'] = q.value(4)
                f['type'] = q.value(5)
                f['deform'] = q.value(6)
                f.setGeometry(geom)
                yield f
                
    with edit(layer):
         layer.addFeatures(features())
    layer.loadNamedStyle(styles.crackStyle)
        
    
    
    
    
    
    
    
    
    