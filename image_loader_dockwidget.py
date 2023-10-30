# -*- coding: utf-8 -*-
"""
/***************************************************************************
 imageLoaderDockWidget
                                 A QGIS plugin
 Loads and unloads images.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-03-24
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Drew
        email                : drew.bennett@ptsinternational.co.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal,QUrl#,Qt
from qgis.utils import iface
from qgis.core import Qgis

from PyQt5.QtWidgets import QMenuBar,QFileDialog#,QDataWidgetMapper
from PyQt5 import QtGui
from PyQt5.QtSql import QSqlDatabase

from image_loader.image_model import imageModel

from image_loader.functions.load_frame_data import loadFrameData
from image_loader.functions.load_cracking import loadCracking
from image_loader.widgets import set_layers_dialog

from image_loader import view_gps_layer
from image_loader import db_functions
from image_loader.gps_model_2 import gpsModel
from image_loader import runs_table_model


FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'image_loader_dockwidget_base.ui'))


class imageLoaderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):        
        super(imageLoaderDockWidget, self).__init__(parent)
        self.setupUi(self)
        self.layersDialog = set_layers_dialog.setLayersDialog(parent=self)
        db_functions.createDb()

        self.model = imageModel(parent=self)
        self.model.fields = self.layersDialog
        self.imagesView.setModel(self.model)
        self.initTopMenu()
        
        self.gpsModel = gpsModel()
        self.runsModel = runs_table_model.runsTableModel()
        self.runsWidget.setModel(self.runsModel)
        self.runsWidget.setGpsModel(self.gpsModel)
        self.runsModel.dataChanged.connect(self.model.select)
        
        self.runBox.setModel(self.runsModel)

        self.runBox.currentIndexChanged.connect(self.runChange)
        self.runChange()
        #self.tabs.setTabEnabled(2, False)
        
        

    def loadImages(self):
        self.model.loadImages(self.imagesView.selected())
        
    
    def createOverviews(self):
        self.model.createOverviews()
        
   
    def georeferenceImages(self):
        if self.gpsModel.hasGps():
            #self.gpsModel.applyCorrections()
            self.gpsModel.applyChainageCorrections()
            self.model.georeference(self.gpsModel)
        else:
            iface.messageBar().pushMessage("Image_loader", "GPS data required", level=Qgis.Info)
        
        
    def runChange(self):
        t = self.runBox.currentText()
        try:
            run = int(t)
        except:
            run = 0
        self.model.setRun(run)
        #set combobox color
    #    c = self.runBox.model().index(index,0).data(Qt.BackgroundColorRole)#QColor or None
     #   if c is not None:
     #       p = self.runBox.palette()
     #       p.setColor(QtGui.QPalette.Button, c)
      #      self.runBox.setPalette(p)

    
    def new(self):
        self.model.clear()
        self.gpsModel.clear()


    def load(self):
        f = QFileDialog.getOpenFileName(caption = 'Load file',filter = ';sqlite database (*.db)')
        if f:
            if f[0]:
                self.model.load(f[0])
        

    def initTopMenu(self):
        topMenu = QMenuBar(self.mainWidget)    
        
        fileMenu = topMenu.addMenu("File")
        newAct = fileMenu.addAction('New')
        newAct.triggered.connect(self.new)
                
        saveAsAct = fileMenu.addAction('Save as...')
        saveAsAct.triggered.connect(self.saveAs)
        openMenu = fileMenu.addMenu('Open')
        openAct = openMenu.addAction('Open...')
        openAct.triggered.connect(self.load)
        
        openRilAct = openMenu.addAction('Open Raster image load file...')
        openRilAct.triggered.connect(self.openRilFile)
        
     #  openCorrectionsAct = openMenu.addAction('Open corrections...')
      #  openCorrectionsAct.triggered.connect(self.openCorrections)
        
        loadGpsAct = openMenu.addAction('Open GPS...')
        loadGpsAct.triggered.connect(self.loadGps)
        
        ######################load
        toolsMenu = topMenu.addMenu("Tools")
        fromFolderAct = toolsMenu.addAction('Find details from folder...')
        fromFolderAct.triggered.connect(self.detailsFromFolder)


        viewMenu = toolsMenu.addMenu('View')

        #layersMenu = topMenu.addMenu("Load layers")
        loadFramesAct = viewMenu.addAction('View Spatial Frame Data...')
        loadFramesAct.triggered.connect(self.loadFrames)
        
        loadGpsAct = viewMenu.addAction('View original GPS data...')
        loadGpsAct.triggered.connect(lambda:view_gps_layer.loadGpsLines(corrected = False))
        
        loadCorrectedGpsAct = viewMenu.addAction('View corrected GPS data...')
        loadCorrectedGpsAct.triggered.connect(lambda:view_gps_layer.loadGpsLines(corrected = True))
        
        loadCracksAct = viewMenu.addAction('View Cracking Data...')
        loadCracksAct.triggered.connect(self.loadCracks)     
        
        setLayers = toolsMenu.addAction('Settings...')
        setLayers.triggered.connect(self.layersDialog.exec_)
        
        selectMenu = topMenu.addMenu("Select")
        markAllAct = selectMenu.addAction('Mark all images')
        markAllAct.triggered.connect(self.model.markAll)

        unmarkAllAct = selectMenu.addAction('Unmark all images')
        unmarkAllAct.triggered.connect(self.model.unmarkAll)
         
        markRunAct = selectMenu.addAction('Mark all images in run')
        markRunAct.triggered.connect(self.model.markRun)

        unmarkRunAct = selectMenu.addAction('Unmark all images in run')
        unmarkRunAct.triggered.connect(self.model.unmarkRun)
        
        processMenu = topMenu.addMenu("Process")
        
        loadAct = processMenu.addAction('Load selected images')
        loadAct.triggered.connect(self.loadImages)
        
        georeferenceAct = processMenu.addAction('Georeference selected images')
        georeferenceAct.triggered.connect(self.georeferenceImages)
        
       # overviewsAct = processMenu.addAction('Create overviews for selected images')
      #  overviewsAct.triggered.connect(self.createOverviews)
        
        vrtAct = processMenu.addAction('Make combined VRTs for selected images')
        vrtAct.triggered.connect(self.makeVrt)
        
        helpMenu = topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help (in your default web browser)')
        openHelpAct.triggered.connect(self.openHelp)        
        self.mainWidget.layout().setMenuBar(topMenu)



    def framesLayer(self):
        return self.layersDialog.framesLayer()

    def idField(self):
        return self.layersDialog.idField()
  
    def runField(self):
        return self.layersDialog.runField()
    

#opens help/index.html in default browser
    def openHelp(self):
        helpPath = os.path.join(os.path.dirname(__file__),'help','help.html')
        helpPath = 'file:///'+os.path.abspath(helpPath)
        QtGui.QDesktopServices.openUrl(QUrl(helpPath))

        

    def loadFrames(self):
        f = QFileDialog.getOpenFileName(caption = 'Load Spatial Frame Data',filter = 'txt (*.txt)')
        if f:
            if f[0]:
                loadFrameData(f[0])



    def makeVrt(self):
        self.model.makeVrt()


    def loadGps(self):
        p = os.path.join(self.layersDialog['folder'],'Hawkeye Exported Data')
        if os.path.isdir(p):
            d = p
        else:
            d = ''
        f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = 'csv (*.csv);;shp (*.shp)',directory=d)
        if f:
            if f[0]:
                self.gpsModel.loadFile(f[0])
                iface.messageBar().pushMessage("Image_loader", "Loaded GPS data.", level=Qgis.Info)



    def loadCracks(self):
        f = QFileDialog.getOpenFileName(caption = 'Load Crack data Data',filter = 'txt (*.txt)')
        if f:
            if f[0]:
                loadCracking(f[0])
                

    #open dialog and load csv/sqlite file
    def openRilFile(self):
        f = QFileDialog.getOpenFileName(caption = 'open',filter = '*;;*.csv;;*.txt')[0]
        if f:
           # self.setFile(f)
            self.model.loadRIL(f)    
            
            
    def openCorrections(self):
        f = getFile(folder = os.path.join(self.layersDialog['folder'],'Processed Data') , filt = '*;;*.csv')
       # f = QFileDialog.getOpenFileName(caption = 'open',filter = '*;;*.csv')[0]
        if f:
            self.model.runsModel.select()
        
            
    #save all tables to sqlite database.
    def saveAs(self):
        f = QFileDialog.getSaveFileName(caption = 'Save details',filter = 'sqlite database (*.db)')[0]
        if f:
            self.model.save(f)
            iface.messageBar().pushMessage("Image_loader", "Saved to {file}".format(file=f), level=Qgis.Info)


    #load all tif files in folder and consider showing progress bar
    def detailsFromFolder(self):
        f = QFileDialog.getExistingDirectory(self,'Folder with images')
        if f:
           # progress = QProgressDialog("Finding image details...","Cancel",0,0,self)
         #   progress.setWindowModality(Qt.WindowModal)
            self.model.addFolder(f)
           # progress.deleteLater()           


    def closeEvent(self, event):
        QSqlDatabase.database('image_loader').close()
        self.closingPlugin.emit()
        event.accept()


def getFile(folder,filt):
        if os.path.isdir(folder):
            d = folder
        else:
            d = ''
        f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = filt,directory=d)
        if f:
            return f[0]