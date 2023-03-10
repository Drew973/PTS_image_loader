# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 08:07:39 2023

@author: Drew.Bennett
"""


from image_loader.details_tree_model import detailsTreeModel
from image_loader.details_tree_view import detailsTreeView



def test1():

    m = detailsTreeModel()
    
   
    m.addDetail(run = 'a',imageId = 5)
    m.addDetail(run = 'a',imageId = 3)
    m.addDetail(run = 'a',imageId = 4)
    m.addDetail(run = 'b',imageId = 3)
    m.addDetail(run = 'a',imageId = 0)

  
    v = detailsTreeView()
    v.setModel(m)
    #v.setHeaderHidden(True)
    v.show()
    return v
    
if __name__=='__console__' or __name__=='__main__':
    v = test1()
    