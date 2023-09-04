# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 09:09:00 2023

@author: Drew.Bennett
"""

from PyQt5.QtCore import QProcess
from PyQt5.QtWidgets import QProgressDialog




#[{program:str,args:[str]}]
def runCommands(commands,progress=QProgressDialog(),batchsize = 20):
    
    
    nextIndex = 0
    
    def processFinished(process):
        progress.setValue(progress.value()+1)
        
        
        
    def startNext(process):
        
        if nextIndex < len(commands):
        
            c = commands[nextIndex]
            if isinstance(c,str):
                nextIndex += 1
                process.start(c)
            
        
        #process.start
    progress.canceled.connect
    
    processes = [QProcess() for i in range(batchsize)]
    
    for i,p in enumerate(processes):
        p.finished.connect(lambda p: processFinished(p))
    