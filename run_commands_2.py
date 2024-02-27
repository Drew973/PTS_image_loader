# -*- coding: utf-8 -*-
"""
Created on Fri May 19 07:57:15 2023

@author: Drew.Bennett
"""

from PyQt5.QtCore import QProcess,pyqtSignal,QObject
from PyQt5.QtWidgets import QProgressDialog,QPlainTextEdit,QDialog,QVBoxLayout,QDialogButtonBox,QProgressBar,QListWidget
#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication


#def dictProcess(QProcess):
   # def __init__(self,parent = None):
  #      super().__init__(parent)
   #     self.data = {}



class command:
    
    commandCompleted = pyqtSignal(int,str,str)

    def __init__(self,number,text):
        self.number = number
        self.text = ''
        self.status = ''
        
        
        
class processManager(QObject):
    commandCompleted = pyqtSignal(int,str,str)
    
    def __init__(self,progress = None,parent=None):
        super().__init__(parent=parent)
        self.commands = []
        self.progress = progress
        
        
#in series. blocking.
    def runCommands(self,commands):
        self.progress.setRange(0,len(commands))
        for i,c in enumerate(commands):
            if not self.wasCanceled():
           #     print('running {c}\n'.format(c=c))
                proc = QProcess(parent = None)
                proc.start(c)
                proc.waitForFinished()
                self.progress.setValue(i+1)
                e = str(proc.readAllStandardError().data(), encoding='utf-8')
                e = ''
                self.commandCompleted.emit(i,c,e)
             #   print('completed',c)
                QApplication.processEvents()


    def wasCanceled(self):
        if self.progress is not None:
            return self.progress.wasCanceled()
        return False



class commandRunner(QObject):
    commandCompleted = pyqtSignal(int,str,str)
    
    def __init__(self,progress,parent=None):
        super().__init__(parent=parent)
        self.progress = progress
        self.progress.canceled.connect(self.abort)
        self.completedCount = 0
        self.processes = {}
        self.commands = []
        self.commandCompleted.connect(progress.commandCompleted)
        
    def runCommands(self,commands):
   #     print('runCommands',commands)
        self.processes = {}
        self.progress.setRange(0,len(commands))
        self.progress.setValue(0)
        self.nextInd = 0
        self.commands = commands
        self.completedCount = 0
        for i in [0,1,2,3]:
            self._startNext(i)

    def abort(self):
    #    print('abort')
        self.commands = []
        for p in self.processes.values():
            p.close()
        #self.wait()



    def _startNext(self,number):
        if self.nextInd < len(self.commands) and not self.progress.wasCanceled():
            
            self.processes[number] = QProcess(parent = None)
            
            if number == 0:
                print('number0')
                self.processes[number].finished.connect(self.process0Completed)
            
            if number == 1:
                self.processes[number].finished.connect(self.process1Completed)     
                
            if number == 2:
                self.processes[number].finished.connect(self.process2Completed)    
                
            if number == 3:
                self.processes[number].finished.connect(self.process3Completed)
                
       #     self.processes[number] = process
#
            print('_startNext',number)
           # command = r'python "C:\\Users\\drew.bennett\\AppData\\Roaming\\QGIS\\QGIS3\\profiles\\default\\python\\plugins\\image_loader\\georeference.py" "D:\RAF_BENSON\Data\2024-01-08\MFV1_007\Run 7\LCMS Module 1\Images\IntensityWithoutOverlay\2024-01-08 13h29m23s LCMS Module 1 000045.jpg" "D:\RAF_BENSON\Data\2024-01-08\MFV1_007\Run 7\LCMS Module 1\Images\IntensityWithoutOverlay\2024-01-08 13h29m23s LCMS Module 1 000045_warped.tif" "[(462817.25451149343, 191031.18473576196, 0, 1250), (462814.636631912, 191027.20938695985, 0, 0), (462814.00135534233, 191033.51217535444, 1038, 1250), (462811.25700605544, 191029.34904325698, 1038, 0)]"'
            command  = self.commands[self.nextInd]
            self.processes[number].start(command)#obsolete. should change this?
            self.processes[number].waitForStarted()
            
            state = self.processes[number].state()
            print('state',state)
            
       #     e = self.processes[number].error()
        #    print('e',e)
            
          #  self.processes[number].waitForFinished()
           # QApplication.processEvents()
            self.nextInd += 1



    def process0Completed(self):
     #   print('process0Completed')
        self._processCompleted(0)

    def process1Completed(self):
        self._processCompleted(1)
        
    def process2Completed(self):
        self._processCompleted(2)
        
    def process3Completed(self):
        self._processCompleted(3)
                
    def _processCompleted(self,number):
 #       print('_processCompleted',number)
        process = self.processes[number]
        self.completedCount += 1
       # command = self.commands[number]
        e = process.readAllStandardError()
        self.progress.setValue(self.completedCount)
        e = str(e.data(), encoding='utf-8')
        command = process.arguments()
        self.commandCompleted.emit(self.completedCount,str(command),e)
        self._startNext(number)
        
           

'''
run iterable of commands as subprocess in paralell.
update progress dialog and allow cancelling
'''


def textBox():
    textBox = QPlainTextEdit()
    textBox.setReadOnly(True)



def runCommands(commands,labelText = 'running...',progress = None,textBox = textBox()):
    if progress is None:
        progress = commandsDialog(parent = None)
     #   progress = QProgressDialog(labelText,"Cancel", 0, len(commands),parent = None)#QObjectwithout parent gets deleted like normal python object
    #    progress.forceShow()
        progress.show()

   # QApplication.processEvents()
    d = processManager(progress = progress)
    d.commandCompleted.connect(progress.commandCompleted)
    d.runCommands(commands)
    #results = d.results
    del d
   # progress.close()
 #   return results
    


class commandsDialog(QDialog):
    
    
    canceled = pyqtSignal()
    
    def __init__(self,parent=None,title = 'Processing'):
        super().__init__(parent)
        self.canceledValue = False
        self.setLayout(QVBoxLayout())

        self.progressBar = QProgressBar()
        self.layout().addWidget(self.progressBar)
        
        self.resultsBox = QListWidget()
        self.resultsBox.setToolTip('Errors')
        self.layout().addWidget(self.resultsBox)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
     #   buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
       # buttons.closed.connect(self.close)
        self.layout().addWidget(buttons)
        self.setLabelText(title)
        
    
    def setLabelText(self,text):
        self.setWindowTitle(text)
        
    def setValue(self,value):
        self.progressBar.setValue(value)
        
        
    def value(self):
        return self.progressBar.value()
        
        
    def wasCanceled(self):
        return self.canceledValue
    
    
    def setRange(self,minimum,maximum):
        self.progressBar.setRange(minimum,maximum)
    
    
    def commandCompleted(self,i,command,result):
      #  print('{c} : {r}'.format(c = command,r = result))
      
        self.progressBar.setValue(i+1)  
      
      
        if result != '':
            self.resultsBox.addItem('{c} : {r}'.format(c = command,r = result))
        if self.progressBar.value() == self.progressBar.maximum():
            if self.resultsBox.count() == 0:
                self.resultsBox.addItem('completed with no errors')
          #      self.close()
            




    def accept(self):
        self.canceled.emit()
        super().accept()
        
        
    def reject(self):
        self.canceled.emit()
        super().reject()
    
    
    def close(self):
        self.reject()
        super().close()
    
if __name__ in ('__main__','__console__'):
    d = commandsDialog()
    d.exec()
    
    
    
'''    
def updateProgress(listLike,labelText='running...',progress = None):
    if progress is None:
       # progress = QProgressDialog(labelText,"Cancel", 0, len(listLike),parent = None)
        progress = commandsDialog(parent = None)
    progress.setRange(0,len(listLike))
    for i,v in enumerate(listLike):
        if progress.wasCanceled():
            break
        progress.setValue(i)
        yield(v)
    progress.close()
        
 '''
    
    
    
    
    
    
    
    
    
    
    
