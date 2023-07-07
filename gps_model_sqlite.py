# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 09:26:59 2023

@author: Drew.Bennett
"""



class gpsModel:
    
    
    
    
    def __init__(self,con):
        self.con = con
        connection.cursor()
        
        q = '''
        create table if not exists points(
            m float not null unique
            ,x float
            ,y float
            )
        '''
        
        
        cursor.execute(q)
        
        
        
        
        
        
    def getPoint(self,m,offset):
        pass
    
    
    
    
    def getM(self,pt,run=''):
        pass
    
    
import sqlite3    
    
# define connection and cursor
connection = sqlite3.connect(r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\test.db')
cursor = connection.cursor()
 
# create the user defined function
#connection.create_function("ROHACK", 2, _customFun)
connection.close()
