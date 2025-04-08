# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:52:54 2022

@author: Drew.Bennett
"""


import os


testFolder = os.path.dirname(__file__)
dbFile = os.path.join(testFolder,'test.db')
profileFolder = os.path.join(testFolder,'profiles')



import cProfile



#profile function and write [function_name].prof to test/profiles.
#returns function(**args)
def profileFunction(function , args = None):
    pr = cProfile.Profile()
    pr.enable()
    
    #get ValueError: Another profiling tool is already active if profiler not closed due to error etc.

    try:
       # with cProfile.Profile() as profiler:#context manager not in earlier versions of cProfile
        if args:
            r = function(**args)
        else:
            r = function()
            
        to = os.path.join(profileFolder,function.__name__+'.prof')
        pr.dump_stats(to)
        return r
        
        
    except Exception as e:
        raise e
    
    finally:
        pr.disable()
        
