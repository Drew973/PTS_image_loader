# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 13:17:19 2023

@author: Drew.Bennett
"""

from qgis.core import QgsProject,QgsRasterLayer,QgsLayerTreeGroup,QgsContrastEnhancement
import os


#iface.addRasterLayer
def loadImage(file,groups):
    name = os.path.splitext(os.path.basename(file))[0]
    group = getGroup(groups)#QgsLayerTreeGroup
    layer = QgsRasterLayer(file,name)        
    layer.setContrastEnhancement(QgsContrastEnhancement.NoEnhancement)#remove contrast enhancement. end up with same pixel value showing as different color.
    group.addLayer(layer)
    group.setExpanded(False)    
    #addLayer
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    node.setExpanded(False)        
    
    
'''
returns new or existing QgsLayerTreeGroup with name child and parent
#child:str
#parent:QgsLayerTreeGroup or QgsLayerTree
'''
def findOrMake(child,parent=QgsProject.instance().layerTreeRoot()):
    child = str(child)
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
    