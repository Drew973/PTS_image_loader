# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 13:31:30 2023

@author: Drew.Bennett
"""


from qgis.core import QgsProject
from qgis.core import QgsRasterLayer,QgsCoordinateReferenceSystem,QgsLayerTreeGroup




    #load layer. expand expands group. show renders image.
    
    #groups []
def loadImage(filepath,name,groups,expand=False,show=True,crs=QgsCoordinateReferenceSystem('EPSG:27700')):
   
   
    layer = QgsRasterLayer(filepath, name)
    layer.setCrs(crs)
        
    group = getGroup(groups)
    group.addLayer(layer)
                
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
            
    node = group.findLayer(layer)
    node.setItemVisibilityChecked(show)
    node.setExpanded(expand)
    return layer






'''
functions for QgsLayerTreeGroup
'''

'''
returns new or existing QgsLayerTreeGroup with name child and parent
#child:str
#parent:QgsLayerTreeGroup or QgsLayerTree
'''
def findOrMake(child,parent=QgsProject.instance().layerTreeRoot()):
    for c in parent.children():
        if c.name() == child and isinstance(c,QgsLayerTreeGroup):
            return c
    
    return parent.addGroup(child)
    


#finds or makes group from list of ancestors.
#groups: list of strings
def getGroup(groups):
    parent = QgsProject.instance().layerTreeRoot()
    for name in groups:
        parent = findOrMake(name,parent)
    return parent



#remove direct child group from parent
def removeChild(child,parent=QgsProject.instance().layerTreeRoot()):
        for c in parent.children():
            if c.name() == child and isinstance(c,QgsLayerTreeGroup):
                parent.removeChildNode(c)

