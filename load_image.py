# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 13:17:19 2023

@author: Drew.Bennett
"""

from qgis.core import QgsProject,QgsRasterLayer,QgsContrastEnhancement
import os
from image_loader import group_functions

'''
def loadLayer(layer,groups):
    group = getGroup(groups)#QgsLayerTreeGroup
    group.addLayer(layer)
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    node.setExpanded(False) 
'''


#iface.addRasterLayer
def loadImage(file,groups):
    name = os.path.splitext(os.path.basename(file))[0]
    group = group_functions.getGroup(groups)#QgsLayerTreeGroup
    layer = QgsRasterLayer(file,name)        
    layer.setContrastEnhancement(QgsContrastEnhancement.NoEnhancement)#remove contrast enhancement. end up with same pixel value showing as different color.
    group.addLayer(layer)
    
   # group_functions.sortGroup(group)
    
    #group.setExpanded(False)#why?
    #addLayer
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
    node = group.findLayer(layer)
    node.setItemVisibilityChecked(True)
    #node.setExpanded(False)#why?
    
    
