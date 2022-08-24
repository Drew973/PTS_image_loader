# -*- coding: utf-8 -*-
"""
Created on Fri Aug 19 13:05:05 2022

@author: Drew.Bennett
"""



from qgis.core import QgsProject
from qgis.core import QgsRasterLayer,QgsCoordinateReferenceSystem


from image_loader.models.image_model import generate_details,group_functions,raster_extents


'''
load raster image.


groups:
    iterable or None
'''
def loadImage(filePath,run=None,imageId=None,name=None,groups=None,show=True,expand=False,crs=QgsCoordinateReferenceSystem('EPSG:27700')):
    
        if run is None:
            run = generate_details.generateRun(filePath)
    
        if imageId is None:
           imageId = generate_details.generateImageId(filePath)
      
        if name is None:
            name = generate_details.generateLayerName(filePath)
    
        if groups is None:
            groups = generate_details.generateGroupsList(filePath)
        print(groups)
           
           
        layer = QgsRasterLayer(filePath, name)
        layer.setCrs(crs)
        
        group = group_functions.getGroup(groups)
        group.addLayer(layer)
                
        QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
            
        node = group.findLayer(layer)
        node.setItemVisibilityChecked(show)
        node.setExpanded(expand)
                
    
    
if __name__=='__console__':
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\MFV2_01_ImageInt_000005.tif'
    loadImage(f)
    
    
    
    
    
    