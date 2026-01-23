# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:05:54 2024

@author: Drew.Bennett
mypy settings.py --follow-imports=silent
"""

from PyQt5.QtCore import QSettings
from image_loader.type_conversions import asInt , asFloat , asBool
from qgis.utils import iface
from qgis.core import QgsCoordinateReferenceSystem , QgsCoordinateTransform , QgsProject

settings = QSettings("pts" , "image_loader")


def startAtZero() -> bool:
    return asBool(value('startAtZero'),False)


def destSrid() -> int:
    return asInt(settings.value('destSrid'),27700)


def getCanvasCrs() -> QgsCoordinateReferenceSystem:
    return iface.mapCanvas().mapSettings().destinationCrs()


def value(k):
    return settings.value(k)


def outsideRunDistance():
    return asFloat(value('outsideRunDistance'),50.0)


def makeTransform(fromSrid:int , toSrid:int) -> QgsCoordinateTransform :
    return QgsCoordinateTransform(QgsCoordinateReferenceSystem(fromSrid) ,
                                  QgsCoordinateReferenceSystem(toSrid),
                                  QgsProject.instance())


def canvasToDestTransform() -> QgsCoordinateTransform:
    return QgsCoordinateTransform(getCanvasCrs() , destCrs(), QgsProject.instance())


def transformToDestCrs(fromSrid:int) -> QgsCoordinateTransform:
        return makeTransform(fromSrid , destSrid())


def transformFromDestCrs(toSrid:int) -> QgsCoordinateTransform :
        return makeTransform(destSrid() , toSrid)


def destCrs() -> QgsCoordinateReferenceSystem :
    return QgsCoordinateReferenceSystem(destSrid())


def setValue(k , v):
    return settings.setValue(k,v)