# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 10:12:18 2025

@author: Drew.Bennett



runs list of QProcess in paralel. 
use QProcess.setProgram() and setArguments()

emits progressChanged signal when process ends.
does not emit this when user canceled.


emits errorOccured signal on error
    
"""

#can use QProgressDialog for ui. iface.messageBar for errors. 
from PyQt5.QtCore import pyqtSignal , QProcess , QObject , QTimer
import os
from PyQt5.QtWidgets import QApplication

coreCount = os.cpu_count()#number of CPU cores



class processRunner(QObject):
    progressChanged = pyqtSignal(int)
    errorOccured = pyqtSignal(str)
    completed = pyqtSignal()


    def __init__(self , parent = None):
        super().__init__(parent)
        self.toDo = []
        self.active = {}
        self.completedCount = 0
        self.canceled  = False # prevent progressChanged emitting after cancel. Makes QProgressDialog visible.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(100)#time in miliseconds


    #cancel any ongoing processes then start processes
    def beginProcesses(self , processes):
        self.toDo = []
        for p in self.active.values():
            p.close()
        self.toDo = processes
        self.active = {}
        self.completedCount = 0
        self.canceled  = False
        self.update()


    def update(self):
        if self.canceled == True:
            return
        #call processFinished and remove finished processes from active
        fin = [k for k in self.active if self.active[k].state() == QProcess.NotRunning]
        for k in fin:
            self.processFinished(self.active[k])
            #getting k not in self.active
            #emits progressChanged signal. this causes connected slots to happen before leaving this method.
            #modal qprogressbar.setValue calls processEvents()
            #connecting QProcess.finished can trigger this method again.
            if k in self.active:
                del self.active[k]
            else:
                print(k,self.active.keys())

        #start next processes until coreCount processes active or toDo empty.
        for i in range(coreCount - len(self.active)):
            self.startNext()

        if len(self.active) == 0 and len(self.toDo) == 0:
            self.completed.emit()


    #emit signals and update completedCount
    def processFinished(self , process):
        if process.exitStatus() == QProcess.CrashExit:
            err = str(process.readAllStandardError())
            self.errorOccured.emit(err)
            
        self.completedCount += 1
        self.progressChanged.emit(self.completedCount)
  #      print(self.completedCount)



    def startNext(self):
        if len(self.toDo) > 0:
            p = self.toDo.pop()
            #p.finished.connect(self.update)
            p.start()
         #   print('starting new process')
            p.waitForStarted()
            if p.state() == QProcess.Running:
                self.active[len(self.toDo)] = p
            else:
                self.errorOccured.emit('Subprocess not started')
                print('Subprocess not started')
            

    def cancel(self):
        self.canceled = True
        for p in self.active.values():
            p.close()
        for p in self.active.values():
            p.waitForFinished()
        


    #blocking.
    def waitForFinished(self):
        while len(self.toDo) + len(self.active) > 0 and not self.canceled:
            QApplication.processEvents()


    



