# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:05:54 2024

@author: Drew.Bennett
"""

from PyQt5.QtCore import QSettings
from image_loader.type_conversions import asInt

from qgis.core import QgsCoordinateReferenceSystem , QgsCoordinateTransform , QgsProject


settings = QSettings("pts" , "image_loader")



def makeTransform(fromSrid:int , toSrid:int) -> QgsCoordinateTransform:
    return QgsCoordinateTransform(QgsCoordinateReferenceSystem(fromSrid) ,
                                  QgsCoordinateReferenceSystem(toSrid),
                                  QgsProject.instance())


def transformToDestCrs(fromSrid:int):
        return makeTransform(fromSrid , destSrid())


def transformFromDestCrs(toSrid:int):
        return makeTransform(destSrid() , toSrid)


def destSrid() -> int:
    return asInt(settings.value('destSrid'),27700)


def destCrs() -> QgsCoordinateReferenceSystem :
    return QgsCoordinateReferenceSystem(destSrid())

def value(k):
    return settings.value(k)




def setValue(k , v):
    return settings.setValue(k,v)