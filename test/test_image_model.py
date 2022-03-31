# -*- coding: utf-8 -*-
"""
Created on Tue Mar 29 09:14:33 2022

@author: Drew.Bennett
"""
from image_loader import image_model
import os


if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)

else:
    testFolder = os.path.dirname(__file__)


def testFromFolder():
    folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01'
    m = image_model.imageModel()
    m.fromFolder(folder)
    return m
    
    
def testWriteCsv(m):
    f = os.path.join(testFolder,r'outputs\test_write.csv')
    m.saveAsCsv(f)
    return m
  
  
def testLoadCsv():
    f = os.path.join(testFolder,r'inputs/test.csv')
    m = image_model.imageModel()
    m.loadCsv(f)
    return m
  
def testLoadImages(m):
    QgsProject.instance().clear()
    m.loadImages(hide=True)
    
    
def testLoadTxt():  
    f = os.path.join(testFolder,r'inputs/TXY_Y Raster Image Load File.txt')
    m = image_model.imageModel()
    m.loadTxt(f)
    return m
    
  
if __name__ == '__main__' or __name__=='__console__':
    from PyQt5.QtWidgets import QTableView
    from qgis.core import QgsProject
    v = QTableView()
    testFromFolder()
    m = testLoadCsv()
    testWriteCsv(m)
    m = testLoadTxt()
    v.setModel(m)
    testLoadImages(m)
    v.show()
    #m.loadImages()