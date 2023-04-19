# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 15:11:50 2023

@author: Drew.Bennett
"""


class imageModel:
    #public. write unit tests for these.
    


    
    def loadImages(self,indexes,progress):
        pass
    
    
    def remake(self,indexes,progress):
        pass
    
    
    def dropRows(self,indexes):
        pass
    
    
    def openFile(self,file):
        pass
    
    
    def saveAs(self,file):
        pass
    

    #set chainage/offset corrections from startPoint and endPoint
    
   # QgsPointXY,QgsPointXY,QModelIndex
    def addCorrection(self,startPoint,endPoint,index):
        pass
    
    
    #if run index in indexes set all in run.
    def mark(self,indexes,value = True):
        pass
    
    
    def markBetween(self,runIndex,start,end):
        pass
    
    
    
    #private. start with _ . don't necesarrily need unit tests for these.
    
    
    
    
    