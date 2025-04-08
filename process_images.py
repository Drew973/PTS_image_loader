# -*- coding: utf-8 -*-
"""
Created on Thu Mar 27 10:18:06 2025

@author: Drew.Bennett
"""


from qgis.utils import iface
from qgis.core import Qgis
from PyQt5.QtWidgets import QProgressDialog , QLabel
from PyQt5.QtCore import Qt
from image_loader import (process_runner , georeference_data ,backend)










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





def georeferenceRuns(runPks , parentWidget):

    #need to remove any VRT or geotif containing georeferenced images.
    #remove layers containing image(s) to remove filelocks

    for v in backend.runs_functions.vrtDataFromRuns(runPks = runPks):
        v.removeSources()
    
    georeferenceProcesses = []
    errorMessages = []
    
    for run in runPks:
        backend.corrections_functions.correctRun(run)
        for gd in georeference_data.getGeoreferenceData(run):
            georeferenceProcesses.append(gd.asQProcess())    
        
    runProcesses(parent = parentWidget , processes = georeferenceProcesses , labelText = 'Georeferencing runs')



from image_loader import test

def profileGeoreferenceRuns():
    w = QLabel('parent widget')
    w.show()
    runPks = backend.allRunPks()[0:1]
    test.profileFunction(georeferenceRuns,{'runPks':runPks,'parentWidget':w})
    return w
    
if __name__ == '__console__':
    profileGeoreferenceRuns()
    



