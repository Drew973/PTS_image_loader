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
        self.toDo = []
        self.process1 = None
        self.command1 = None
       

        
    def process1Finished(self):
        e = self.process1.readAllStandardError()
        e = str(e.data(), encoding='utf-8')
        self.commandCompleted.emit(str(self.command1),e)
        self.startProcess1()

    
        
    def startProcess1(self):
        self.process1 = QProcess(parent = None)
        self.process1.finished.connect(self.process1Finished)
        if len(self.toDo) > 0 and not self.progress.wasCanceled():
            self.command1 = self.toDo.pop()
            self.process1.start(self.command1)#obsolete. should change this?
            self.process1.waitForStarted()
            
        
    def runCommands(self,commands):
        self.toDo = commands
        self.startProcess1()
        

    def abort(self):
    #    print('abort')
        self.toDo = []
        self.process1.close()


           
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
    
    
    
    
    
    
    
    
    
    
    
