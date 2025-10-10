# -*- coding: utf-8 -*-
"""
"""

import os
from PyQt5.QtCore import pyqtSignal,QUrl,QItemSelectionModel,Qt
import csv
from qgis.utils import iface
from qgis.core import Qgis

from PyQt5.QtWidgets import QMenuBar,QFileDialog,QAbstractItemView,QProgressDialog,QDialog , QDockWidget


from PyQt5 import QtGui,QtCore
from PyQt5.QtSql import QSqlDatabase

from image_loader import check_imports
check_imports.checkImports()#need to check imports before using them

from image_loader import (db_functions , file_locations , upload_xml , runs_model , image_model , settings_dialog ,
                          downloads , settings , process_runner , layer_functions , georeference_data,
                          backend , runs_from_layer_dialog , image_loader_dockwidget_base , type_conversions , vrt, dims,
                                                      )


from image_loader.backend import corrections_model

version = 3.50

def message(message : str , level : int = Qgis.Info ):
    iface.messageBar().pushMessage("Image_loader", message, level=level)


#brgin running run list of processes and increnent progress dialog
def beginProcesses(progress:QProgressDialog , processes:list):
    runner = process_runner.processRunner(parent = progress)#garbage collected without parent.
    progress.canceled.connect(runner.cancel)
    runner.errorOccured.connect(message)
    runner.progressChanged.connect(lambda : progress.setValue(progress.value()+1))
    #print('running',processes)
    runner.beginProcesses(processes)
    return runner


def runProcesses(parent , processes , labelText):
    prog = QProgressDialog(labelText = labelText , parent = parent , maximum = len(processes))
    prog.setWindowModality(Qt.WindowModal)
    prog.show()
    runner = beginProcesses(processes = processes , progress = prog)
    runner.waitForFinished()
    prog.hide()
    prog.deleteLater()





class imageLoaderDockWidget(QDockWidget , image_loader_dockwidget_base.Ui_imageLoaderDockWidgetBase):
#class imageLoaderMainWidget(QWidget , main_window.Ui_MainWindow):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):        
        super(imageLoaderDockWidget, self).__init__(parent)
        self.setupUi(self)
        
        title = 'PTS image loader v{ver}'.format(ver = version)
        self.setWindowTitle(title)
        self.setupMenu()
        
        self.settingsDialog = settings_dialog.settingsDialog(parent=self)
        self.imagesModel = image_model.imageModel(parent=self)
        self.imagesModel.fields = self.settingsDialog
        self.imagesView.setModel(self.imagesModel)
        
        self.runsModel = runs_model.runsModel()
        
        self.runsWidget.setModel(self.runsModel)
        self.runsWidget.doubleClicked.connect(self.setChainages)
        
        self.runBox.setModel(self.runsModel)
        self.runBox.setModelColumn(self.runsModel.fieldIndex('run_name'))
        self.runBox.currentIndexChanged.connect(self.runChanged)
        
        self.setFile(file_locations.dbFile)
        self.runChanged(self.runBox.currentIndex())
        self.selectRunButton.clicked.connect(self.selectRun)



    def setupMenu(self):
        #top menu
        topMenu = QMenuBar()
        self.dockWidgetContents.layout().setMenuBar(topMenu)
        
        #topMenu = QMenuBar(self.mainWidget)

        fileMenu = topMenu.addMenu("File")
        newAct = fileMenu.addAction('New')
        newAct.triggered.connect(self.new)
                
        #saveAsAct = fileMenu.addAction('Save as...')
        #saveAsAct.triggered.connect(self.saveAs)
        
       # saveRuns = fileMenu.addAction('Save runs as csv...')
       # saveRuns.triggered.connect(self.saveRuns)        
        
        openMenu = fileMenu.addMenu('Open')

        loadGpsAct = openMenu.addAction('Open GPS...')
        loadGpsAct.triggered.connect(self.loadGps)


        loadXMLAct = openMenu.addAction('Open Distress files...')
        loadXMLAct.triggered.connect(self.loadXML)
        
        loadCorrectionPerRun = openMenu.addAction('Open File with 1 correction per run...')
        loadCorrectionPerRun.triggered.connect(self.loadCorrectionPerRun)
        
        
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
        processRunsAct.setToolTip('Georeference,make and load VRT')
        processRunsAct.triggered.connect(self.processRuns)
        
        processMenu = runsMenu.addMenu('More Processing options')

        
        georeferenceRunsAct = processMenu.addAction('Georeference selected runs')
        georeferenceRunsAct.triggered.connect(self.georeferenceRuns)

        runsVrtAct = processMenu.addAction('Remake VRT files for selected runs')
        runsVrtAct.triggered.connect(self.makeRunsVrt)

        loadRunsVrtAct = processMenu.addAction('Load VRT files for selected runs')
        loadRunsVrtAct.triggered.connect(self.loadRunsVrt)

        openRilAct = runsMenu.addAction('Open Raster image load file...')
        openRilAct.triggered.connect(self.openRilFile)
        
        RunsFromAreasAct = runsMenu.addAction('Add runs from polygon layer...')
        RunsFromAreasAct.triggered.connect(self.runsFromLayer)


        correctionsMenu = topMenu.addMenu("Corrections")
        correctionsMenu.setToolTipsVisible(True)
        saveCorrectionsAct = correctionsMenu.addAction('Save corrections...')
        saveCorrectionsAct.triggered.connect(self.saveCorrections)
        loadCorrectionsAct = correctionsMenu.addAction('Load corrections...')
        loadCorrectionsAct.triggered.connect(self.loadCorrections)



        imagesMenu = topMenu.addMenu("Images")
        
        fromFolderAct = imagesMenu.addAction('Find details from folder...')
        fromFolderAct.triggered.connect(self.detailsFromFolder)

        clearImagesAct = imagesMenu.addAction('Clear images table')
        clearImagesAct.triggered.connect(self.clearImages)

        #loadAct = imagesMenu.addAction('Load selected images')
        #loadAct.triggered.connect(self.loadImages)
        
        helpMenu = topMenu.addMenu('Help')
        openHelpAct = helpMenu.addAction('Open help')
        openHelpAct.triggered.connect(self.openHelp)
       # self.mainWidget.layout().setMenuBar(topMenu)




    def setFile(self , file:str):
        db_functions.setFile(file)
        self.runsModel.select()
        self.imagesModel.select()
        self.correctionsView.setModel(corrections_model.correctionsModel(parent = self))
        

    def loadImages(self):
        image_model.loadImages(self.imagesView.selectedPks())


    def selectRun(self):
        row = self.runBox.currentIndex()
        self.runsWidget.selectRow(row)
        

    def runChanged(self , row:int):
        col = self.runsModel.fieldIndex('pk')
        pk = type_conversions.asInt(self.runsModel.index(row,col).data(),-1)
        cm = self.correctionsView.model()
        if hasattr(cm,'setRun'):
            cm.setRun(pk)
            self.correctionsView.correctionDialog.close()

    def runsFromLayer(self):
        d = runs_from_layer_dialog.runsFromAreasDialog(parent = self , runsModel = self.runsModel)
        res = d.exec()
        if res == QDialog.Accepted:
            self.runsModel.select()
            

    #tests if has gps and display message if not. -> bool
    def checkGps(self):
        pc = backend.pointCount()
        if pc > 0:
            return True
        else:
            message('Check GPS was loaded (file,open,open GPS...)')
            return False



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

        
    def processRuns(self):
        self.georeferenceRuns()
        self.makeRunsVrt()
        self.loadRunsVrt()
        
        
        
    #connected to action
    def georeferenceRuns(self):
        if self.checkImages() and self.checkRuns() and self.checkGps():
            runPks = self.runsWidget.selectedPks()
            if len(runPks) == 0:
                message("No runs selected")
                return
            
            #need to remove any VRT containing georeferenced images.
            toRemove = [v.vrtFile for v in backend.runs_functions.vrtDataFromRuns(runPks = runPks)]
            georeferenceProcesses = []
            errorMessages = []
            
            for run in runPks:
                backend.correctRun(run)
                for gd in georeference_data.getGeoreferenceData(run):
                    georeferenceProcesses.append(gd.asQProcess(parent = self))
                    toRemove.append(gd.warpedFile)
            
            for e in errorMessages:
                message(e)
            
            if georeferenceProcesses:
                layer_functions.removeSources(toRemove)
                
            runProcesses(parent = self , processes = georeferenceProcesses , labelText = 'Georeferencing runs')

            del georeferenceProcesses



    #connected to action
    def makeRunsVrt(self):
        runPks = self.runsWidget.selectedPks()
        if len(runPks) == 0:
            message("No runs selected")
            return
        vrt.makeRunsVrt(runPks)


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
        self.imagesModel.clear()
        backend.clearGps()
        self.runsModel.clear()
        backend.clearCorrections()
        self.correctionsView.model().select()
        db_functions.clear()



    def loadCorrectionPerRun(self):
        file = QFileDialog.getOpenFileName(caption = 'Load file with correction per run',filter = ';csv (*.csv)')
        if file:
            print(file)
            runPks = []
            t = settings.transformFromDestCrs(4326)

            with open(file[0],'r') as f:
                reader = csv.DictReader(f,delimiter='\t')
                data = [r for r in reader]
                runPks = backend.runs_functions.addRuns(data)
                self.runsModel.select()
                

                for i,r in enumerate(data):
                    
                    print(r)
                    sf = int(r['start_frame'])
                    ef = int(r['end_frame'])

                    m = dims.frameToM(sf) + float(r["chainage_shift"])
                    offset = float(r["offset"])
                    
                    p = t.transform(backend.getGpsPoint(m = m , offset = offset))
                    print(runPks[i])
                    backend.insertCorrection(frame = sf ,
                                            line = dims.LINES/2,
                                            pixel = dims.PIXELS/2,
                                            m = m,
                                            offset = offset,
                                            lon = p.x(),
                                            lat = p.y(),
                                            run = runPks[i])


            self.correctionsView.model().select()


    #open... handler
    def load(self):
        f = QFileDialog.getOpenFileName(caption = 'Load file',filter = ';sqlite database (*.db)')
        if f:
            file = f[0]
            if file:
                db_functions.loadFile(file)
                self.imagesModel.select()
                self.runsModel.select()
        
    

    def downloadGpsLayer(self):
        try:
            downloads.downloadGps()
        except Exception as e:
            message("Error displaying GPS:"+str(e), level=Qgis.Warning)



    #handle open settings... action
    def openSettings(self):
        oldSrid = settings.destSrid()
        self.settingsDialog.exec_()
        newSrid = settings.destSrid()
        if oldSrid != newSrid:
            backend.reproject()
        

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
        f = QFileDialog.getOpenFileName(caption = 'Load GPS Data',filter = 'rutacd csv (*rutacd*.csv);;csv (*.csv);;anpp (*.anpp)',directory=d)

        if f:
            if f[0]:
                backend.uploadFile(f[0])
                for run in backend.runs_functions.allRunPks():
                    backend.correctRun(run)


    def downloadCracks(self):
        cc = db_functions.crackCount()
        if cc == 0:
            return message("No crack data. Are distress files loaded?")
        if self.runsModel.rowCount() == 0:
            return message("No runs. This only shows cracks within runs.")
        if not self.checkGps():
            return
        progress = QProgressDialog(parent = self)
        progress.setLabelText('Loading cracks...')
        progress.show()
        downloads.downloadCracks(progress = progress)   
        progress.close()
            

    def clearImages(self):
        backend.clearImages()
        self.imagesModel.select()


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
        downloads.downloadRuts(saveTo = None , parentWidget = self)

    
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
        downloads.downloadFaulting()
    
    
    #upload xml or acdx into database
    def loadXML(self):
        files = QFileDialog.getOpenFileNames(caption = 'open distress files' , filter = '*.xml;;*.acdx')[0]
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


    #save all tables to sqlite database.
    def saveCorrections(self):
        f = QFileDialog.getSaveFileName(caption = 'Save corrections' , filter = 'csv (*.csv)')[0]
        if f:
            backend.saveCorrectionsCsv(f)
            iface.messageBar().pushMessage("Image_loader" , "Saved corrections to {file}".format(file=f), level=Qgis.Info)



    def loadCorrections(self):
        f = QFileDialog.getOpenFileName(caption = 'Load corrections' , filter = '*.csv')[0]
        if f:
            backend.loadCorrectionsCsv(f)
            self.correctionsView.model().select()



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