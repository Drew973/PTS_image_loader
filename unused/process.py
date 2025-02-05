# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 15:56:08 2025

@author: Drew.Bennett
"""



class process:
    
    
    
    def __init__(self , startArgs):
        self.startArgs = startArgs
    
    
    
    def start(self):
        super().start(self.startArgs)
        
        self.waitForStarted()
        if self.state() != QProcess.running:
            raise ValueError('could not start process')
            
            
        