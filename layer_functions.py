# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 12:55:17 2023

@author: Drew.Bennett
"""

from qgis.core import QgsProject
import os

#remove layers where normalized path is in sources.
def removeSources(sources):
    sources = [os.path.normpath(s) for s in sources]
    toRemove = []
    for layer in QgsProject.instance().mapLayers().values():
        if os.path.normpath(layer.source()) in sources:
            toRemove.append(layer.id())
        QgsProject.instance().removeMapLayers(toRemove)


def test():
    sources = ['C:/Users/drew.bennett/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/image_loader/test/1_007/ImageRng/2023-01-21 10h08m11s LCMS Module 1 002710_warped.vrt']
    removeSources(sources)