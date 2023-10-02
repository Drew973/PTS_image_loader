# -*- coding: utf-8 -*-
"""
Created on Fri May 19 07:57:15 2023

@author: Drew.Bennett
"""

from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QProgressDialog
#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


class commandRunner:
    
    def __init__(self,progress,batchSize = 10):
      #  super().__init__(parent=parent)
        self.progress = progress
        self.processes = []
     #   for i in range(0,batchSize):
         #   proc = QProcess()
         #   proc.finished.connect(lambda state : self._processCompleted())            
        self.progress.canceled.connect(self.abort)
        self.batchSize = batchSize
        
        
        
    def runCommands(self,commands):
        self.progress.setRange(0,len(commands))
        self.progress.setValue(0)
       # print('max',self.progress.maximum())
       
        self.nextInd = 0
        self.processes = []
        self.commands = commands

        for c in commands:
            proc = QProcess()
            proc.finished.connect(lambda process:self._processCompleted(proc,c))           
            self.processes.append(proc)
        
        for i in range(0,self.batchSize):
            self._startNextProcess()

        self.wait()
        


    def _startNextProcess(self):
       # print('Canceled',self.progress.wasCanceled())
        if self.nextInd < len(self.commands) and not self.progress.wasCanceled():
            self.processes[self.nextInd].start(self.commands[self.nextInd])#obsolete. should change this
            self.nextInd += 1
      

    def wait(self):
        for p in self.processes:
            p.waitForFinished()
            QApplication.processEvents()



    def abort(self):
    #    print('abort')
        self.commands = []
        for p in self.processes:
            p.close()
        self.wait()



    def _processCompleted(self,process,command):
       # print('_processCompleted',state)
        e = process.readAllStandardError()
        if e:
            print('error running {c}:{e}:'.format(c=command,e = e))
        else:
            pass
            #print(command)
        self.progress.setValue(self.progress.value()+1)
        self._startNextProcess()
        

'''
run iterable of commands as subprocess in paralell.
update progress dialog and allow cancelling
'''



def runCommands(commands,labelText = 'running...',progress = None):
    
    if progress is None:
        progress = QProgressDialog(labelText,"Cancel", 0, len(commands),parent = None)#QObjectwithout parent gets deleted like normal python object
        progress.forceShow()
        QApplication.processEvents()
    
    d = commandRunner(progress = progress)
    d.runCommands(commands)
    del d
    progress.close()

    
    
    
    
    
def updateProgress(listLike,labelText='running...',progress = None):
    if progress is None:
        progress = QProgressDialog(labelText,"Cancel", 0, len(listLike),parent = None)
    progress.setRange(0,len(listLike))
    for i,v in enumerate(listLike):
        if progress.wasCanceled():
            break
        progress.setValue(i)
        yield(v)
    progress.close()
        
    
    
    
    
    
    
    
    
    
    
    
    
