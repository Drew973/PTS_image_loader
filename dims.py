# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 11:32:21 2023

@author: Drew.Bennett
"""


import numpy as np

WIDTH = 4.0
PIXELS = 1038
LINES = 1250
HEIGHT = 5.0


def lineToM(frame,line):
    return HEIGHT * (frame-line/LINES)


def pixelToOffset(pixel):
    return WIDTH*0.5-pixel*WIDTH/PIXELS


#need frame arg to distinguish end from start of next frame
def mToLine(m,frame):
    if np.isfinite(m):
        startM = (frame-1)*HEIGHT
        endM = frame*HEIGHT
        if m<startM:
            return LINES
        if m>endM:
            return 0
        return round(LINES - LINES*(m-startM)/HEIGHT)
    return 0
    

#float/np float -> int
def offsetToPixel(offset):
    if np.isfinite(offset):
        return round(PIXELS * 0.5 - offset * PIXELS / WIDTH )
    return 0
