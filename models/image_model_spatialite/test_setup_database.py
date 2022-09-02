# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 11:52:44 2022

@author: Drew.Bennett
"""




from image_loader.models.image_model_spatialite.setup_database import setupDb


def test():
    dbFile = r'C:\Users\drew.bennett\Documents\image_loader\test.db'
    setupDb(dbFile,overwrite = True)
    
    
if __name__=='__console__':
    test()