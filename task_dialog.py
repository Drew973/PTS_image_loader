# -*- coding: utf-8 -*-
"""
Created on Tue Mar 12 12:00:18 2024

@author: Drew.Bennett
"""
from PyQt5.QtWidgets import QProgressDialog
from qgis.core import QgsTask,QgsApplication
from qgis.utils import iface


#from PyQt5.QtWidgets import *
import time


class testTask(QgsTask):

    def run(self):
        """This function is where you do the 'heavy lifting' or implement
        the task which you want to run in a background thread. This function 
        must return True or False and should only interact with the main thread
        via signals"""
        for i in range (21):
            time.sleep(0.5)
            self.setProgress(int(100*i/20))
            #check to see if the task has been cancelled
            if self.isCanceled():
                return False
        return True

    def finished(self, result):
        """This function is called automatically when the task is completed and is
        called from the main thread so it is safe to interact with the GUI etc here"""
        if result is False:
            iface.messageBar().pushMessage('Task was cancelled')
        else:
            iface.messageBar().pushMessage('Task Complete')



class taskDialog(QProgressDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setRange(0,100)
        self.task = None


    def startTask(self,task,priority = 99999999999999):
        """Create a task and add it to the Task Manager"""
        self.task = task
        #connect to signals from the background threads to perform gui operations
        #such as updating the progress bar
        self.task.begun.connect(lambda: print('Working...'))
        self.task.progressChanged.connect(self.setValue)
        self.task.taskCompleted.connect(lambda: print('Task Complete'))
        self.task.taskTerminated.connect(self.taskCanceled)
        self.canceled.connect(self.cancelTask)
        added = QgsApplication.taskManager().addTask(self.task,priority)
        
        
       # self.task.run()
        if added == 0:
            raise ValueError('task could not be started')

    def cancelTask(self):
        print('canceling task')
        if self.task is not None:
            self.task.cancel()
            self.task = None


    def taskCanceled(self):
        self.reset()
        

if __name__ == '__console__':
    d = taskDialog()
    d.show()
    d.startTask(testTask('Custom Task'))