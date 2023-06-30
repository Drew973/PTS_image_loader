# -*- coding: utf-8 -*-
"""
Created on Fri May 19 07:57:15 2023

@author: Drew.Bennett
"""

from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QProgressDialog
from PyQt5.QtCore import Qt
import time

class commandRunner(QProgressDialog):
    
    def __init__(self,parent=None,labelText=''):
        super().__init__(parent=parent)
        self.processes = []
        self.batchSize = 100
        self.setWindowModality(Qt.WindowModal)
        self.setLabelText(labelText)
        
        
    def runCommands(self,commands):
        #split = [s for s in splitList(commands,batchSize)]#.
        self.setRange(0,len(commands))
        self.setValue(0)
        self.nextInd = 0
        self.finished = False
        
        self.commands = commands
        for i in commands[0:self.batchSize]:
            self._startNextProcess()
            

    def _startNextProcess(self):
        i = self.nextInd
        self.nextInd += 1
   #     print(i)
        if i < len(self.commands):
            proc = QProcess()
            self.processes.append(proc)
            proc.finished.connect(self._processCompleted)
            self.processes.append(proc)
            proc.start(self.commands[i])#obsolete. should change this 
        else:
            self.wait()
        

    def wait(self):
        for p in self.processes:
            p.waitForFinished()
        self.finished = True


    def close(self):
        for p in self.processes:
            p.close()
        self.wait()
        return super().close()



  #  def end(self):
   #     for p in self.processes:
    #        p.close()
     #   for p in self.processes:
      #      p.waitForFinished()    


    def _processCompleted(self,process):
        self.setValue(self.value()+1)
    #    if process.exitStatus() == QProcess.CrashExit:
     #       print(process.readAllStandardError())
        self._startNextProcess()
        

'''
run iterable of commands as subprocess in paralell.
update progress dialog and allow cancelling
'''



def runCommands(commands,labelText = 'processing'):
   # print(commands)
    d = commandRunner(labelText = labelText)
    d.runCommands(commands)
    d.exec()

    


'''
run iterable of commands as subprocess in paralell.
update progress dialog and allow cancelling
todo: use [(program,[args])]

run batchsize at time. Too high causes os error whilst too low results in unnecessary waiting.

'''
def oldrunCommands(commands,progress=None,batchSize=20,shell=False):
    processes = []

    if progress is None:
        progress = QProgressDialog()
        progress.show()
        
    
    def checkResult(process):
        progress.setValue(progress.value()+1)
        if process.exitStatus() == QProcess.CrashExit:
           # print('error')
            print(process.readAllStandardError())
    
    
    
    def cancelProcesses():
        for p in processes:
            p.kill()
            
    progress.canceled.connect(cancelProcesses)
        
    progress.setRange(0,len(commands))
    progress.setValue(0)
    split = [s for s in splitList(commands,batchSize)]#.

    
    for s in split:
        processes = []
        for c in s:
            proc = QProcess()
            processes.append(proc)
            proc.finished.connect(lambda:checkResult(proc))
            proc.start(c)#obsolete. should change this 
        
        for p in processes:
            if progress.wasCanceled():
                p.close()
            p.waitForFinished()
        
        if progress.wasCanceled():
            break


#split Iterible into lists up to maxSize long
def splitList(lis, maxSize = 10):
    c = []
    for d in lis:
        if len(c) >= maxSize:
            yield c
            c = []
        c.append(d)
    if len(c)>0:
        yield c
        
        
        
def testSplitList():
    test = [i for i in range(0,53)]
    print(test)
    for d in splitList(test):
        print(d)
#testSplitList()  