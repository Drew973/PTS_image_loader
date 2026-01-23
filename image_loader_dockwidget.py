# -*- coding: utf-8 -*-
"""
"""

import os

from qgis.PyQt import QtWidgets, uic
from PyQt5.QtCore import pyqtSignal,QUrl,QItemSelectionModel,Qt

from qgis.utils import iface
from qgis.core import Qgis

from PyQt5.QtWidgets import QMenuBar,QFileDialog,QAbstractItemView,QProgressDialog,QDialog,QMessageBox,QDataWidgetMapper

from PyQt5 import QtGui,QtCore
from PyQt5.QtSql import QSqlDatabase

from image_loader import check_imports
check_imports.checkImports()#need to check imports before using them

from image_loader import (db_functions , file_locations , upload_xml , runs , image_model , settings_dialog , gps_model ,
                          download_distress , settings , layer_functions , georeference_process,
                          backend,runs_from_layer_dialog,add_mfv_dialog,gps)


from image_loader.mfv_model import mfvModel
from image_loader.process_runner import runProcesses



def message(message : str , level : int = Qgis.Info ):
    iface.messageBar().pushMessage("Image_loader", message, level=level)



FORM_CLASS, _ = uic.loadUiType(file_locations.uiFile)
version = 3.5



class imageLoaderDockWidget(QtWidgets.QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):        
        super(imageLoaderDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        
        self.gps = gps.gpsSystem()
        
        
        title = 'PTS image loader v{ver}'.format(ver = version)
        self.setWindowTitle(title)
        
        self.settingsDialog = settings_dialog.settingsDialog(parent=self)

        self.runsWidget.doubleClicked.connect(self.setChainages)
        
        #top menu
        topMenu = QMenuBar(self.mainWidget)
        
        fileMenu = topMenu.addMenu("File")
        newAct = fileMenu.addAction('New...')
        newAct.triggered.connect(self.new)
                
        saveAsAct = fileMenu.addAction('Save as...')
        saveAsAct.triggered.connect(self.saveAs)
        
        saveRuns = fileMenu.addAction('Save runs as csv...')
        saveRuns.triggered.connect(self.saveRuns)        
        
        openMenu = fileMenu.addMenu('Open')
        
       # loadRunsCsvAct = openMenu.addAction('Open runs csv...')
       # loadRunsCsvAct.triggered.connect(self.loadRunsCsv)

        openRilAct = openMenu.addAction('Open Raster image load file...')
        openRilAct.triggered.connect(self.openRilFile)
        
       # loadGpsAct = openMenu.addAction('Open GPS...')
    #    loadGpsAct.triggered.connect(self.loadGps)
        self.browseGpsButton.clicked.connect(self.loadGps)


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
        
        processSelectedRunsAct = runsMenu.addAction('Process selected runs')
        processSelectedRunsAct.setToolTip('Georeference,make and load VRT')
        processSelectedRunsAct.triggered.connect(self.processSelectedRuns)
        
        georeferenceRunsAct = runsMenu.addAction('Georeference selected runs')
        georeferenceRunsAct.triggered.connect(self.georeferenceRuns)

        runsVrtAct = runsMenu.addAction('Remake VRT files for selected runs')
   #     runsVrtAct.setToolTip('Only useful when run start/end changed.')
        runsVrtAct.triggered.connect(self.makeRunsVrt)

        loadRunsVrtAct = runsMenu.addAction('Load VRT files for selected runs')
   #     runsVrtAct.setToolTip('Only useful when run start/end changed.')
        loadRunsVrtAct.triggered.connect(self.loadRunsVrt)



        RunsFromAreasAct = runsMenu.addAction('Add runs from polygon layer...')
        RunsFromAreasAct.triggered.connect(self.runsFromLayer)

        imagesMenu = topMenu.addMenu("Images")
        
        fromFolderAct = imagesMenu.addAction('Find details from folder...')
        fromFolderAct.triggered.connect(self.detailsFromFolder)

        loadAct = imagesMenu.addAction('Load selected images')
        loadAct.triggered.connect(self.loadImages)
        
        helpMenu = topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.triggered.connect(self.openHelp)
        self.mainWidget.layout().setMenuBar(topMenu)

        self.addMfvButton.clicked.connect(self.addMfv)
        self.dropMfvButton.clicked.connect(self.dropMfv)

        self.setDb(db_functions.createDb())
        self.mfvBox.currentIndexChanged.connect(self.mfvChanged)


    def setDb(self, db:QSqlDatabase):
        db_functions.vacuum()
        self.imagesModel = image_model.imageModel(parent=self)
        self.imagesModel.fields = self.settingsDialog
        self.imagesView.setModel(self.imagesModel)
        self.gpsModel = gps_model.gpsModel(db = db)
        
        
        
        self.runsModel = runs.runsModel()
        self.runsModel.gpsModel = self.gpsModel
        self.runBox.setModel(self.runsModel)
        
        
        self.runsWidget.setModel(self.runsModel)
        self.runsWidget.setGpsModel(self.gpsModel)
        
        self.mfvModel = mfvModel(db)
        self.mfvBox.setModel(self.mfvModel)
        self.mfvModel.select()
        
        self.gps = gps.gpsSystem.fromDatabase(db,mfvs = self.mfvModel.allMfvs())
        self.runsWidget.chainagesDialog.setGpsModel(self.gps)
        self.runsModel.gps = self.gps

        self.mfvMapper = QDataWidgetMapper()
        self.mfvMapper.setModel(self.mfvModel)
        self.mfvMapper.addMapping(self.mfvName,self.mfvModel.fieldIndex('mfv_ref'))
        self.mfvMapper.addMapping(self.gpsFileDisplay,self.mfvModel.fieldIndex('gps_file'))
        self.mfvBox.currentIndexChanged.connect(self.mfvMapper.setCurrentIndex)
        self.mfvMapper.setCurrentIndex(self.mfvBox.currentIndex())
        
        self.mfvChanged()
        

    def mfvChanged(self):
        mfv = self.currentMfv()
        self.runsModel.setMfv(mfv)
        self.runsModel.select()
        self.imagesModel.mfv = mfv
        self.imagesModel.select()
        self.gps.setMfv(mfv)
    
    #dialog for adding mfv.
    def addMfv(self):
        #print(self.mfvBox.currentText())
        d = add_mfv_dialog.addMfvDialog(parent=self)
        res = d.exec()
        if res == QDialog.Accepted:
            self.mfvModel.insertMfv(d.getMfv())


    #dialog to drop current mfv,
    def dropMfv(self):
        reply = QMessageBox.question(None , 'Image loader:' , 'Delete MFV "{mfv}"?'.format(mfv = self.currentMfv()) , QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.mfvModel.dropMfv(self.currentMfv())



    def currentMfv(self) -> str:
        return self.mfvBox.itemText(self.mfvBox.currentIndex())
      
        

    def loadImages(self):
        image_model.loadImages(self.imagesView.selectedPks())


    def runsFromLayer(self):
        d = runs_from_layer_dialog.runsFromAreasDialog(parent = self , runsModel = self.runsModel)
        res = d.exec()
        if res == QDialog.Accepted:
            self.runsModel.select()
            

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
 #   def georeferenceImages(self):
    #    if self.checkGps():
       #     image_model.beginGeoreference(self.gpsModel , pks = self.imagesView.selectedPks())
        
        
    def processSelectedRuns(self):
        runPks = self.runsWidget.selectedPks()
        self.runsModel.processRuns(gps = self.gps , runPks = runPks)
        
      #  self.georeferenceRuns()
       # self.makeRunsVrt()
     #   self.loadRunsVrt()
        
        
    #connected to action
    def georeferenceRuns(self):
        if self.checkImages() and self.checkRuns() and self.checkGps():
            runPks = self.runsWidget.selectedPks()
            if len(runPks) == 0:
                message("No runs selected")
                return
            imagePks = backend.runs_functions.imagePksFromRun(runPks)
            
            #need to remove any VRT containing georeferenced images.
            vrtSources = [v.vrtFile for v in backend.runs_functions.vrtDataFromRuns(runPks = runPks)]

            
            if not imagePks:
                message("No images found in runs {runs}".format(runs = runPks))
                return
            georeferenceProcesses , sources , errors = georeference_process.georeferenceProcesses(imagePks = imagePks , gpsModel = self.gpsModel)
            
            for e in errors:
                message(e)
            
            if georeferenceProcesses:
                layer_functions.removeSources(vrtSources + sources)
                
            runProcesses(parent = self , processes = georeferenceProcesses , labelText = 'Georeferencing runs')


    #connected to action
    def makeRunsVrt(self):
        runPks = self.runsWidget.selectedPks()
        if len(runPks) == 0:
            message("No runs selected")
            return
        vrtData = backend.runs_functions.vrtDataFromRuns(runPks = runPks)
        
        n = len(vrtData)
    
        d = QProgressDialog(parent = self)
        d.setWindowModality(Qt.WindowModal)
        d.setRange(0,n*2)
        
        d.setLabelText('Removing layers')
        d.show()

        for row in vrtData:
            row.removeSources()
        
        d.setLabelText('Writing txt files')#io bound. 
        for i,row in enumerate(vrtData):
            if d.wasCanceled():
                return
            row.writeTextFile()
            d.setValue(i)
        
        d.setLabelText('Remaking vrt files')
        processes = [row.asQProcess() for row in vrtData]
        runner = beginProcesses(processes = processes , progress = d)
        runner.waitForFinished()

        d.setValue(d.maximum())
        d.hide()
        d.deleteLater()


    def loadRunsVrt(self):
        runPks = self.runsWidget.selectedPks()
        if len(runPks) == 0:
            message("No runs selected")
            return
        
        vrtData = backend.runs_functions.vrtDataFromRuns(runPks = runPks)
        n = len(vrtData)
        d = QProgressDialog(parent = self)
        d.setWindowModality(Qt.WindowModal)
        d.setRange(0,n)
        d.setLabelText('Loading vrt files')

        for i,row in enumerate(vrtData):
            if d.wasCanceled():
                return
            d.setValue(i)
            row.load()
        d.hide()
        d.deleteLater()



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
        reply = QMessageBox.question(None , 'Image loader:' , 'Clear all data?' , QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.imagesModel.clear()
            self.gpsModel.clear()
            self.runsModel.clear()
            self.mfvModel.dropAllMfv()
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
                backend.runs_functions.loadCsv(file)
                self.runsModel.select()
    
    
    def saveRuns(self):
        f = QFileDialog.getSaveFileName(caption = 'Save runs',filter = 'CSV (*.csv)')[0]
        if f:
            backend.runs_functions.saveRunsCsv(f)
            iface.messageBar().pushMessage("Image_loader", "Saved to {file}".format(file=f), level=Qgis.Info)

    
    



    def downloadGpsLayer(self):
      #  try:
      #      self.gpsModel.downloadGpsLayer()
      #  except Exception as e:
      #      iface.messageBar().pushMessage("Image_loader", "Error displaying GPS:"+str(e), level=Qgis.Warning)
            
        curves = {}
        db = self.runsModel.database()
        for mfv in self.mfvModel.allMfvs():
            try:
                curves[mfv] = gps.curve.fromDatabase(db = db , mfvNumber = mfv)
            except Exception as e:
                print(e)
        
        gps.makeLayer(data = curves)

        print(curves)



    #handle open settings... action
    def openSettings(self):
        oldSrid = settings.destSrid()
        self.settingsDialog.exec_()
        newSrid = settings.destSrid()
        if oldSrid != newSrid:
            self.gpsModel.setSrid(newSrid)#redownload model GPS in selected CRS. takes ~0.2s
        

#opens help/index.html in default browser
    def openHelp(self):
        QtGui.QDesktopServices.openUrl(QUrl(file_locations.helpPath))
        
        

    #handle load gps... action
    def loadGps(self):
        p = os.path.join(str(settings.value('folder')),'Hawkeye Exported Data') 
        if os.path.isdir(p):
            d = p
        else:
            d = ''
        f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = 'rutacd csv (*rutacd*.csv);;csv (*.csv)',directory=d)

        if f:
            if f[0]:
               # self.gpsModel.loadGpsFile(file = f[0],mfv = self.currentMfv())
                #self.gpsModel.setSrid(self.gpsModel.srid)#reprojects
                
                #set gps file for mfvModel
                index = self.mfvModel.index(self.mfvBox.currentIndex(),self.mfvModel.fieldIndex('gps_file'))
                if index.isValid():
                    self.mfvModel.setData(index,f[0])
                c = gps.curve.fromRutacd(f[0] , startAtZero = settings.startAtZero())
                c.upload(mfvNumber = self.currentMfv() , db = self.mfvModel.database())
                self.gps.setCurve(self.currentMfv(),c)


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
        download_distress.downloadRuts(gpsModel = self.gpsModel,saveTo = None , parent = self)

    
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
            self.imagesModel.addFolder(f,mfv=self.currentMfv())


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