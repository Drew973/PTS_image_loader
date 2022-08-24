# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022

@author: Drew.Bennett
"""
import os

from image_loader.models.image_model import image_model
from image_loader.models import runs_model
from image_loader.test.get_db import getDb
from image_loader.functions.setup_database import setupDb 
from image_loader import exceptions


if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)

else:
    testFolder = os.path.dirname(__file__)


def testInit(db = getDb()):
    setupDb(db)
    rm = runs_model.runsModel(db)
    #rm.updateTable()
   # rm.selectAll()
    return rm
    
#imageModel
def testLoadFolder(im):
    f = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images'
    m.fromFolder(f)
  
 
if __name__ == '__main__' or __name__=='__console__':
    from PyQt5.QtWidgets import QTableView
    from qgis.core import QgsProject
    rm = testInit()
    v = QTableView()
    v.setModel(rm)
    v.show()
    #m.loadImages()