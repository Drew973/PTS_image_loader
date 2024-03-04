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
from PyQt5.QtCore import pyqtSignal,QUrl,QItemSelectionModel,QSettings

from qgis.utils import iface
from qgis.core import Qgis

from PyQt5.QtWidgets import QMenuBar,QFileDialog,QAbstractItemView,QApplication,QProgressDialog
from PyQt5 import QtGui,QtCore
from PyQt5.QtSql import QSqlDatabase

from image_loader.image_model import imageModel
from image_loader.settings_dialog import settingsDialog

from image_loader import download_gps
from image_loader import db_functions
from image_loader.gps_model_4 import gpsModel
from image_loader import runs_model
from image_loader.run_commands import commandsDialog
from image_loader.download_cracks import downloadCracks



FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'image_loader_dockwidget_base.ui'))


class imageLoaderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):        
        super(imageLoaderDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        self.settings = QSettings("pts","image_loader")
        self.settingsDialog = settingsDialog(parent=self)
        db_functions.createDb()

        self.imagesModel = imageModel(parent=self)
        self.imagesModel.fields = self.settingsDialog
        self.imagesView.setModel(self.imagesModel)
        self.initTopMenu()
        self.gpsModel = gpsModel()
        
        self.runsModel = runs_model.runsTableModel()
        self.runsModel.gpsModel = self.gpsModel
        
        self.runsWidget.setModel(self.runsModel)
        self.runsWidget.setGpsModel(self.gpsModel)
        self.runsWidget.doubleClicked.connect(self.setChainages)
        #self.chainageBar.rangeChanged.connect()


    def loadImages(self):
        self.imagesModel.loadImages(self.imagesView.selectedPks())


    def createOverviews(self):
        self.imagesModel.createOverviews()
        
   
    def georeferenceImages(self):
        if self.gpsModel.hasGps():
            progress = commandsDialog(title = 'Georeferencing',parent = self)
            progress.show()
            self.imagesModel.georeference(self.gpsModel,pks = self.imagesView.selectedPks(),progress=progress)
        else:
            iface.messageBar().pushMessage("Image_loader", "GPS data required", level=Qgis.Info)
        

    def processRuns(self):
        if self.gpsModel.hasGps():
            progress = commandsDialog(parent = self)
            progress.setLabelText('Processing runs...')
            progress.show()
            pks = self.runsModel.imagePks(self.runsWidget.selectedPks())
       #     print('pks',pks)
            self.imagesModel.georeference(gpsModel = self.gpsModel,pks=pks,progress = progress)
            
            
            progress.setLabelText('Remaking VRTs')
            self.imagesModel.makeVrt(pks=pks,progress = progress)

           # self.runsModel.georeference(gpsModel = self.gpsModel,pks = self.runsWidget.selectedPks(),progress = progress)
        else:
            iface.messageBar().pushMessage("Image_loader", "GPS data required", level=Qgis.Info)        


    #scroll images to run and select in widget
    #same for corrections.
    def setChainages(self,index):
        m = index.model()
        s = index.siblingAtColumn(m.fieldIndex('start_frame')).data()
        if not isinstance(s,int):
            s = 0   
        e = index.siblingAtColumn(m.fieldIndex('end_frame')).data()
        if not isinstance(e,int):
            e = 0              
#        print('s',s,'e',e)
        mode = QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
        selectionModel = self.imagesView.selectionModel()
        selectionModel.clear()
        col = self.imagesModel.fieldIndex('frame_id')
        top = None
        for i in range(self.imagesModel.rowCount()):
            index = self.imagesModel.index(i,col)
            if s<= index.data() and index.data() <= e:
                selectionModel.select(index, mode)
                if top is None:
                    top = index
        if top is not None:
            self.imagesView.scrollTo(top,QAbstractItemView.PositionAtTop)    
    

    def new(self):
        self.imagesModel.clear()
        self.gpsModel.clear()
        self.runsModel.clear()
        db_functions.clear()


    def load(self):
        f = QFileDialog.getOpenFileName(caption = 'Load file',filter = ';sqlite database (*.db)')
        if f:
            file = f[0]
            if file:
                db_functions.loadFile(file)
                self.imagesModel.select()
                self.runsModel.select()
        
        
    def loadRunsCsv(self):
        f = QFileDialog.getOpenFileName(caption = 'Load runs CSV',filter = ';csv (*.csv)')
        if f:
            file = f[0]
            if file:
                self.runsModel.loadCsv(file)
    
    
    def saveRuns(self):
        f = QFileDialog.getSaveFileName(caption = 'Save runs',filter = 'CSV (*.csv)')[0]
        if f:
            self.runsModel.saveCsv(f)
            iface.messageBar().pushMessage("Image_loader", "Saved to {file}".format(file=f), level=Qgis.Info)

    
    
    def initTopMenu(self):
        topMenu = QMenuBar(self.mainWidget)     
        fileMenu = topMenu.addMenu("File")
        newAct = fileMenu.addAction('New')
        newAct.triggered.connect(self.new)
                
        saveAsAct = fileMenu.addAction('Save as...')
        saveAsAct.triggered.connect(self.saveAs)
        
        saveRuns = fileMenu.addAction('Save runs as csv...')
        saveRuns.triggered.connect(self.saveRuns)        
        
        openMenu = fileMenu.addMenu('Open')
        openAct = openMenu.addAction('Open...')
        openAct.triggered.connect(self.load)
        
        loadRunsCsvAct = openMenu.addAction('Open runs csv...')
        loadRunsCsvAct.triggered.connect(self.loadRunsCsv)

        
        openRilAct = openMenu.addAction('Open Raster image load file...')
        openRilAct.triggered.connect(self.openRilFile)
        
     #  openCorrectionsAct = openMenu.addAction('Open corrections...')
      #  openCorrectionsAct.triggered.connect(self.openCorrections)
        
        loadGpsAct = openMenu.addAction('Open GPS...')
        loadGpsAct.triggered.connect(self.loadGps)


        loadXMLAct = openMenu.addAction('Open XML...')
        loadXMLAct.triggered.connect(self.loadXML)
        
        
        ######################load
        toolsMenu = topMenu.addMenu("Tools")
        fromFolderAct = toolsMenu.addAction('Find details from folder...')
        fromFolderAct.triggered.connect(self.detailsFromFolder)

        viewMenu = toolsMenu.addMenu('View')

        loadGpsAct = viewMenu.addAction('View GPS data')
        loadGpsAct.triggered.connect(lambda:download_gps.loadGps(corrected = False))
        
        loadCracksAct = viewMenu.addAction('View Cracking Data')
        loadCracksAct.triggered.connect(self.downloadCracks)     
        
      #  loadCracksAct = viewMenu.addAction('View runs')
      #  loadCracksAct.triggered.connect(self.downloadRuns)     
        
        setLayers = toolsMenu.addAction('Settings...')
        setLayers.triggered.connect(self.settingsDialog.exec_)
       
        runsMenu = topMenu.addMenu("Runs")
        processRunsAct = runsMenu.addAction('Process selected runs')
        processRunsAct.triggered.connect(self.processRuns)
        pasteRunsAct = runsMenu.addAction('Paste from clipboard')
        pasteRunsAct.triggered.connect(self.pasteRuns)


        processMenu = topMenu.addMenu("Images")
        
        loadAct = processMenu.addAction('Load selected images')
        loadAct.triggered.connect(self.loadImages)
        
        georeferenceAct = processMenu.addAction('Georeference selected images')
        georeferenceAct.triggered.connect(self.georeferenceImages)
    
        vrtAct = processMenu.addAction('Make combined VRTs for selected images')
        vrtAct.triggered.connect(self.makeVrt)
        
        helpMenu = topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.triggered.connect(self.openHelp)        
        self.mainWidget.layout().setMenuBar(topMenu)


#opens help/index.html in default browser
    def openHelp(self):
        helpPath = os.path.join(os.path.dirname(__file__),'help','help.html')
        helpPath = 'file:///'+os.path.abspath(helpPath)
        QtGui.QDesktopServices.openUrl(QUrl(helpPath))
        
        
    def pasteRuns(self):
        t = QApplication.clipboard().text()
        self.runsModel.loadText(t)


    def makeVrt(self):
        progress = commandsDialog(title = 'Remaking VRT files',parent = self)
        progress.show()
        self.imagesModel.makeVrt(pks = self.imagesView.selectedPks(),progress = progress)


    def loadGps(self):
        p = os.path.join(self.settingsDialog['folder'],'Hawkeye Exported Data')
        if os.path.isdir(p):
            d = p
        else:
            d = ''
        f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = 'csv (*.csv);;shp (*.shp)',directory=d)
        if f:
            if f[0]:
                startAtZero = self.settingsDialog.startAtZero.isChecked()
                self.gpsModel.loadFile(f[0],startAtZero = startAtZero)
                iface.messageBar().pushMessage("Image_loader", "Loaded GPS data.", level=Qgis.Info)


    def downloadCracks(self):
        cc = db_functions.crackCount()
        if cc:
            progress = QProgressDialog(parent = self)
            progress.setLabelText('Loading cracks...')
            progress.show()
            downloadCracks(gpsModel = self.gpsModel,progress = progress)   
                
         
    def downloadRuns(self):
        pass
         
    
    def loadXML(self):
        files = QFileDialog.getOpenFileNames(caption = 'open XML',filter = '*.xml')[0]
        if len(files)>0:
            print('files',files)
            progress = QProgressDialog(parent = self)
            progress.setLabelText('Loading XML files...')
            progress.setRange(0,len(files))
            progress.show()
            for i,f in enumerate(files):
                if not progress.wasCanceled():
                    progress.setValue(i+1)
                    db_functions.uploadXML(files = [f])
                              
                    
    #open dialog and load csv/sqlite file
    def openRilFile(self):
        f = QFileDialog.getOpenFileName(caption = 'open',filter = '*;;*.csv;;*.txt')[0]
        if f:
           # self.setFile(f)
            self.imagesModel.loadRIL(f)    
            
            
    def openCorrections(self):
        f = getFile(folder = os.path.join(self.settingsDialog['folder'],'Processed Data') , filt = '*;;*.csv')
       # f = QFileDialog.getOpenFileName(caption = 'open',filter = '*;;*.csv')[0]
        if f:
            self.imagesModel.runsModel.select()
        
            
    #save all tables to sqlite database.
    def saveAs(self):
        f = QFileDialog.getSaveFileName(caption = 'Save details',filter = 'sqlite database (*.db)')[0]
        if f:
            self.imagesModel.save(f)
            iface.messageBar().pushMessage("Image_loader", "Saved to {file}".format(file=f), level=Qgis.Info)


    #load all tif files in folder and consider showing progress bar
    def detailsFromFolder(self):
        f = QFileDialog.getExistingDirectory(self,'Folder with images')
        if f:
           # progress = QProgressDialog("Finding image details...","Cancel",0,0,self)
         #   progress.setWindowModality(Qt.WindowModal)
            self.imagesModel.addFolder(f)
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