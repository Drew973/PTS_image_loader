# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 10:59:26 2023

@author: Drew.Bennett
"""
import re    
from PyQt5.QtCore import QSortFilterProxyModel

#sort list
def naturalSort(l): 
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)
    

def lessThan(left,right):
    s = naturalSort([left,right])
    return s[0] == left
            
            
            
#s = '2test1a5'
#print(toList(s))
#print(lessThan('1qgfd4.66','20'))
    
    
class naturalSortProxy(QSortFilterProxyModel):
    
    #QModelIndex,QModelIndex
    def lessThan(source_left,source_right):
        return lessThan(source_left.data(),source_right.data())
        
        