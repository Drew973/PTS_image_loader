# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 08:52:54 2022

@author: Drew.Bennett
"""


import os


testFolder = os.path.dirname(__file__)
#dbFile = os.path.join(testFolder,'outputs','test.sqlite')


profileFolder = os.path.join(os.path.dirname(__file__),'profiles')

import cProfile


def profileFunction(function,args):
    pr = cProfile.Profile()
    pr.enable()
   # with cProfile.Profile() as profiler:#context manager not in earlier versions of cProfile
    r = function(**args)
    pr.disable()
    to = os.path.join(profileFolder,str(function)+'.prof')
    pr.dump_stats(to)
    return r