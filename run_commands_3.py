# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 10:37:05 2024

@author: Drew.Bennett


tools to run external commands in paralell and keep progress dialog updated and responsive.

needs to work from inside QGIS.
    multithreading seems to cause crash
    QThreadPool causes crash
    so does multiprocessing module
    QgsTask? simpler to use QApplication.processEvents()
    
QProcess:waitForFinished() doesn't always?
    
    
"""


from PyQt5.QtWidgets import QProgressDialog , QApplication
from PyQt5.QtCore import QProcess , QObject , pyqtSignal , Qt


def createProgressDialog(parent : QObject = None , labelText : str = '') -> QProgressDialog:
        progress = QProgressDialog(labelText,"Cancel", 0, 1,parent=parent)#QObjectwithout parent gets deleted like normal python object
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        return progress
    

class command(QObject):
    finished = pyqtSignal(int,str,str)# identifier,command, error. '' for sucess
    
    def __init__(self , identifier:int , parent : QObject = None):
        super().__init__(parent)
        self.identifier = identifier
        self.command = ''
        self.process = None
    
    
    def start(self , command:str):
        self.command = command
        self.process = QProcess()
        self.process.finished.connect(self.processFinished)
        self.process.start(command)
        if self.process.waitForStarted():#True for invalid arguments
            #print('started')
            pass
        else:
            print('not started')
            
            

    def processFinished(self , exitCode:int , exitStatus:int):
        
        error = 'Unknown error'
        
        if exitStatus == QProcess.CrashExit:
            error = 'Crash exit: '+str(self.process.readAllStandardError())
            
        if exitStatus == QProcess.NormalExit:
            error = ''
        
        self.finished.emit(self.identifier,self.command,error)
        
        
    def close(self):
        if self.process:
            self.process.close()
 

BATCH = 32


class commandRunner(QObject):
    
    def __init__(self , progress:QProgressDialog = None,parent : QObject = None):
        super().__init__(parent)
        self.progress = progress
        self.initializeCounts()
        
        
    def initializeCounts(self):
        self.completedCount = 0
        self.startedCount = 0
        self.current = {}
        self.canceled = False

        
    #Run list of commands in Parallel and update progress when command completed.
    def run(self , commands : list):
        self.toDo = commands
        self.total = len(commands)
        self.initializeCounts()
        if hasattr(self.progress,'setRange'):
            self.progress.setRange(0,self.total)
        self._setProgress(0)
        for i in range(BATCH):
            self.startNext()
                
        
    #set progress bar value if applicable
    def _setProgress(self , value : int):
        #print('{v} of {t}'.format(v = value,t = self.total))
        if hasattr(self.progress,'value'):
            v = self.progress.value()
        else:
            v = None
        canceled = False
        if hasattr(self.progress,'wasCanceled'):
            canceled = self.progress.wasCanceled()
        if hasattr(self.progress,'setValue') and value != v and not canceled:
            self.progress.setValue(value)
            
        
    def processFinished(self , identifier : int , command:str, error:str ):
        self.completedCount += 1
        #print(command+':'+error)
        del self.current[identifier]
        self._setProgress(self.completedCount)
        if hasattr(self.progress,'commandCompleted'):
            self.progress.commandCompleted(identifier,command,error)
        self.startNext()


    def isRunning(self) -> bool:
        return self.current or self.toDo

    #unused
    def check(self):
        for p in self.current:
            if p.state == QProcess.NotRunning:
                pass
            
            
    def startNext(self):
        if len(self.toDo)>0:
            c = self.toDo.pop(0)
            process = command(identifier = self.startedCount)
            self.startedCount += 1
            process.finished.connect(self.processFinished)
            self.current[process.identifier] = process
            process.start(c)
            
        
    #cancel ongoing subprocesses with close()
    def cancel(self):
        self.toDo = []
        for p in list(self.current.values()):
            p.close()
        self._setProgress(self.total)
        self.canceled = True

    def waitForFinished(self):
        while self.isRunning():
            QApplication.processEvents()


#returns true if all commands attempted. False if user canceled.
def runCommands(commands : list, progress : QObject) -> bool:        
    runner = commandRunner(progress = progress)
    progress.canceled.connect(runner.cancel)
    runner.run(commands = commands )
    progress.exec_()
    runner.waitForFinished()
    return not runner.canceled
    

def test():
    #python -c "import time;time.sleep(10);print('ok');"
    py = "import time;time.sleep(3);print('ok');"
    s = 'python -c "{py}"'.format(py = py)
    commands = [s] * 100
    d = QProgressDialog()
    d.show()
    runner = commandRunner(progress = d)
    d.canceled.connect(runner.cancel)
    runner.run(commands = commands )
    return runner,d
    
    
if __name__ in ('__main__','__console__'):    
    runner,d = test()#closes immediately without reference
    
    
    
    
