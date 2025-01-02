# -*- coding: utf-8 -*-
"""
"""

import os

from qgis.PyQt import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal,QUrl,QItemSelectionModel

from qgis.utils import iface
from qgis.core import Qgis

from PyQt5.QtWidgets import QMenuBar,QFileDialog,QAbstractItemView,QProgressDialog,QApplication

from PyQt5 import QtGui,QtCore
from PyQt5.QtSql import QSqlDatabase

from image_loader import check_imports
check_imports.checkImports()#need to check imports before using them

from image_loader import (db_functions , file_locations , upload_xml , runs_model , image_model , settings_dialog , gps_model ,
                          commands_dialog , download_distress , layer_functions , settings)


FORM_CLASS, _ = uic.loadUiType(file_locations.uiFile)
version = 3.46


def message(message : str , level : int = Qgis.Info ):
    iface.messageBar().pushMessage("Image_loader", message, level=level)


#make vrt files from data
def makeLoadVrt(data):
    prog = QProgressDialog(labelText = 'remaking VRT files')  
    try:
        vrtFiles = [k for k in data]
        layer_functions.removeSources(vrtFiles)#remove layers to allow file to be edited.
        prog.setMaximum(len(data))
        prog.show()
        for i,vrtFile in enumerate(data):
            QApplication.processEvents()
            if prog.wasCanceled():
                return
            image_model.makeVrtFile(vrtFile = vrtFile , files = data[vrtFile][0])
            image_model.loadImage(file = vrtFile , groups = ['image_loader', 'combined VRT', data[vrtFile][1], data[vrtFile][2] ] )
            prog.setValue(i)
    except Exception as e:
        iface.messageBar().pushMessage("Image_loader", "Error making VRTs:"+str(e), level=Qgis.Warning)
    finally:
        prog.close()


class imageLoaderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):        
        super(imageLoaderDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        title = 'PTS image loader v{ver}'.format(ver = version)
        self.setWindowTitle(title)
        
        self.settingsDialog = settings_dialog.settingsDialog(parent=self)
        db_functions.createDb()

        self.imagesModel = image_model.imageModel(parent=self)
        self.imagesModel.fields = self.settingsDialog
        self.imagesView.setModel(self.imagesModel)
        self.initTopMenu()
        self.gpsModel = gps_model.gpsModel()
        
        self.runsModel = runs_model.runsModel()
        self.runsModel.gpsModel = self.gpsModel
        
        self.runsWidget.setModel(self.runsModel)
        self.runsWidget.setGpsModel(self.gpsModel)
        self.runsWidget.doubleClicked.connect(self.setChainages)
        #self.chainageBar.rangeChanged.connect()


    def loadImages(self):
        image_model.loadImages(self.imagesView.selectedPks())


    #tests if has gps and display message if not. -> bool
    def checkGps(self):
        if self.gpsModel.error != '':
            iface.messageBar().pushMessage("Image_loader",'bad GPS:'+self.gpsModel.error, level=Qgis.Info)
        return self.gpsModel.error == ''


    #tests if has runs and display message if not. -> bool
    def checkRuns(self):
        r = self.runsModel.rowCount() > 0
        if not r:
            iface.messageBar().pushMessage("Image_loader", "No Runs.", level=Qgis.Info)
        return r


    def checkImages(self):
        r = self.imagesModel.rowCount() > 0
        if not r:
            iface.messageBar().pushMessage("Image_loader", "No Image details.", level=Qgis.Info)
        return r        


    #connected to action
    def georeferenceImages(self):
        if self.checkGps():
            image_model.beginGeoreference(self.gpsModel , pks = self.imagesView.selectedPks())
        
        
    #connected to action
    def processRuns(self):
        if self.checkImages() and self.checkRuns() and self.checkGps():
            runPks = self.runsWidget.selectedPks()
            if len(runPks) == 0:
                message("No runs selected")
                return
            imagePks = runs_model.imagePksFromRun(runPks)
            if not imagePks:
                message("No images found in runs {runs}".format(runs = runPks))
                return
            image_model.beginGeoreference(gpsModel = self.gpsModel , pks=imagePks)
            makeLoadVrt(image_model.vrtData(imagePks))


    #connected to action
    def makeRunsVrt(self):
        runPks = self.runsWidget.selectedPks()
        if len(runPks) == 0:
            message("No runs selected")
            return
        imagePks = runs_model.imagePksFromRun(runPks)
        makeLoadVrt(image_model.vrtData(imagePks))
    

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
    
    
    #file...new handler
    def new(self):
        self.imagesModel.clear()
        self.gpsModel.clear()
        self.runsModel.clear()
        db_functions.clear()


    #open... handler
    def load(self):
        f = QFileDialog.getOpenFileName(caption = 'Load file',filter = ';sqlite database (*.db)')
        if f:
            file = f[0]
            if file:
                db_functions.loadFile(file)
                self.imagesModel.select()
                self.runsModel.select()
        
        
    #load Runs csv handler
    def loadRunsCsv(self):
        f = QFileDialog.getOpenFileName(caption = 'Load runs CSV',filter = ';csv (*.csv)')
        if f:
            file = f[0]
            if file:
                self.runsModel.loadCsv(file)
    
    
    def saveRuns(self):
        f = QFileDialog.getSaveFileName(caption = 'Save runs',filter = 'CSV (*.csv)')[0]
        if f:
            runs_model.saveRunsCsv(f)
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
        
        loadRunsCsvAct = openMenu.addAction('Open runs csv...')
        loadRunsCsvAct.triggered.connect(self.loadRunsCsv)

        openRilAct = openMenu.addAction('Open Raster image load file...')
        openRilAct.triggered.connect(self.openRilFile)
        
        loadGpsAct = openMenu.addAction('Open GPS...')
        loadGpsAct.triggered.connect(self.loadGps)


        loadXMLAct = openMenu.addAction('Open Distress files...')
        loadXMLAct.triggered.connect(self.loadXML)
        
        
        ######################load
        toolsMenu = topMenu.addMenu("Tools")

        viewMenu = toolsMenu.addMenu('View')

        loadGpsAct = viewMenu.addAction('View GPS data')
        loadGpsAct.triggered.connect(self.downloadGpsLayer)
        
        loadCracksAct = viewMenu.addAction('View Cracking Data')
        loadCracksAct.triggered.connect(self.downloadCracks)     
        
        loadRutsAct = viewMenu.addAction('View Rutting Data')
        loadRutsAct.triggered.connect(self.downloadRuts)   
        
        loadFaultingAct = viewMenu.addAction('View Transverse joint faulting(concrete)')
        loadFaultingAct.triggered.connect(self.downloadFaulting)   
        
      #  loadCracksAct = viewMenu.addAction('View runs')
      #  loadCracksAct.triggered.connect(self.downloadRuns)     
        
        openSettingsAct = toolsMenu.addAction('Settings...')
        openSettingsAct.triggered.connect(self.openSettings)

       
        runsMenu = topMenu.addMenu("Runs")
        runsMenu.setToolTipsVisible(True)

        
        processRunsAct = runsMenu.addAction('Process selected runs')
        processRunsAct.setToolTip('Georeferences and make VRT files')
        processRunsAct.triggered.connect(self.processRuns)

        runsVrtAct = runsMenu.addAction('Remake VRT files for selected runs')
        runsVrtAct.setToolTip('Only useful when run start/end changed.')
        runsVrtAct.triggered.connect(self.makeRunsVrt)

        imagesMenu = topMenu.addMenu("Images")
        
        fromFolderAct = imagesMenu.addAction('Find details from folder...')
        fromFolderAct.triggered.connect(self.detailsFromFolder)

        loadAct = imagesMenu.addAction('Load selected images')
        loadAct.triggered.connect(self.loadImages)
        
        georeferenceAct = imagesMenu.addAction('Georeference selected images')
        georeferenceAct.triggered.connect(self.georeferenceImages)
    
        vrtAct = imagesMenu.addAction('Make combined VRTs for selected images')
        vrtAct.triggered.connect(self.makeVrt)
        
        helpMenu = topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.triggered.connect(self.openHelp)
        self.mainWidget.layout().setMenuBar(topMenu)


    def downloadGpsLayer(self):
        try:
            self.gpsModel.downloadGpsLayer()
        except Exception as e:
            iface.messageBar().pushMessage("Image_loader", "Error displaying GPS:"+str(e), level=Qgis.Warning)

    #handle open settings... action
    def openSettings(self):
        self.settingsDialog.exec_()
        self.gpsModel.setSrid(settings.destSrid())#redownload model GPS in selected CRS. takes ~0.2s
        

#opens help/index.html in default browser
    def openHelp(self):
        QtGui.QDesktopServices.openUrl(QUrl(file_locations.helpPath))
        
        
    def makeVrt(self):
        progress = commands_dialog.commandsDialog(title = 'Remaking VRT files',parent = self)
        progress.show()
        self.imagesModel.makeVrt(pks = self.imagesView.selectedPks(),progress = progress)


    #handle load gps... action
    def loadGps(self):
        p = os.path.join(str(settings.value('folder')),'Hawkeye Exported Data') 
        if os.path.isdir(p):
            d = p
        else:
            d = ''
        #f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = 'csv (*.csv);;shp (*.shp)',directory=d)
        f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = 'csv (*rutacd*.csv);;shp (*.shp);;all (*.*)',directory=d)

        if f:
            if f[0]:
                try:
                    self.gpsModel.loadFile(f[0])
                    iface.messageBar().pushMessage("Image_loader", "Loaded GPS data.", level=Qgis.Info)
                except Exception as e:
                    iface.messageBar().pushMessage("Image_loader", "Error loading GPS:"+str(e), level=Qgis.Warning)


    def downloadCracks(self):
        cc = db_functions.crackCount()
        if cc == 0:
            iface.messageBar().pushMessage("Image_loader", "No crack data. Are XML files loaded?", level=Qgis.Info)
            return
        if self.runsModel.rowCount() == 0:
            iface.messageBar().pushMessage("Image_loader", "No runs. This only shows cracks within runs.", level=Qgis.Info)
            return
        if not self.checkGps():
            return
        progress = QProgressDialog(parent = self)
        progress.setLabelText('Loading cracks...')
        progress.show()
        download_distress.downloadCracks(gpsModel = self.gpsModel,progress = progress)   
        progress.close()
            

    def downloadRuts(self):
        rc = db_functions.rutCount()
        if rc == 0:
            iface.messageBar().pushMessage("Image_loader", "No rut data. Are XML files loaded?", level=Qgis.Info)
            return
        if not self.checkGps():
            return
        if self.runsModel.rowCount() == 0:
            iface.messageBar().pushMessage("Image_loader", "No runs. This only shows rutting within runs.", level=Qgis.Info)
            return
        download_distress.downloadRuts(gpsModel = self.gpsModel,saveTo = None)

    
    def downloadFaulting(self):
        rc = db_functions.faultingCount()
        if rc == 0:
            iface.messageBar().pushMessage("Image_loader", "No joint faulting data. Are XML files loaded?", level=Qgis.Info)
            return
        if not self.checkGps():
            return
        if self.runsModel.rowCount() == 0:
            iface.messageBar().pushMessage("Image_loader", "No runs. This only shows faulting within runs.", level=Qgis.Info)
            return
        download_distress.downloadFaulting(gpsModel = self.gpsModel)
    
    
    #upload xml or acdx into database
    def loadXML(self):
        files = QFileDialog.getOpenFileNames(caption = 'open XML files' , filter = '*.xml;;*.acdx')[0]
        if len(files) > 0:
            db_functions.clearDistresses()
            upload_xml.uploadXML(files = files,parent=self)    

                    
    #open dialog and load csv/sqlite file
    def openRilFile(self):
        f = QFileDialog.getOpenFileName(caption = 'open' , filter = '*;;*.csv;;*.txt')[0]
        if f:
            self.imagesModel.loadRIL(f)    
            

    #save all tables to sqlite database.
    def saveAs(self):
        f = QFileDialog.getSaveFileName(caption = 'Save details' , filter = 'sqlite database (*.db)')[0]
        if f:
            self.imagesModel.save(f)
            iface.messageBar().pushMessage("Image_loader" , "Saved to {file}".format(file=f), level=Qgis.Info)


    #add all jpg files in folder to images
    def detailsFromFolder(self):
        f = QFileDialog.getExistingDirectory(self , 'Folder with images')
        if f:
            self.imagesModel.addFolder(f)


    def closeEvent(self, event):
        QSqlDatabase.database('image_loader').close()
        self.closingPlugin.emit()
        event.accept()


def getFile(folder,filt):
    if os.path.isdir(folder):
        d = folder
    else:
        d = ''
    f = QFileDialog.getOpenFileName(caption = 'Load GPS Data' , filter = filt , directory=d)
    if f:
        return f[0]