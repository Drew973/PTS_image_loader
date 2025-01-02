# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 14:05:54 2024

@author: Drew.Bennett
"""

from PyQt5.QtCore import QSettings
from image_loader.type_conversions import asInt


settings = QSettings("pts" , "image_loader")


def destSrid() -> int:
    return asInt(settings.value('destSrid'),27700)


def value(k):
    return settings.value(k)