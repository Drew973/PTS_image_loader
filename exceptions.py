# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 10:11:21 2022

@author: Drew.Bennett
"""

class imageLoaderError(Exception):
    pass

     
class imageLoaderQueryError(Exception):
    def __init__(self,q):
        message = 'query "%s" failed with "%s"'%(q.lastQuery(),q.lastError().databaseText())
        super().__init__(message)
        