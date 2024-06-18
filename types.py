# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 08:50:26 2024

@author: Drew.Bennett
"""

def asFloat(v,default = 0.0):
    try:
        return float(v)
    except:
        return default
    
    
def asBool(v,default = False):
    try:
        return bool(v)
    except:
        return default    