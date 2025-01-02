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

MAX = 999999 # 999 km maximum chainage
#max size of QDoubleSpinbox is 2147483647

#use np.clip for arrays
def clamp(v,lower,upper):
    if v < lower:
        return lower
    if v > upper:
        return upper
    return v

#start of frame
def mToFrame(m:float) -> int:
    return int(m/HEIGHT)+1


#chainage at start of frame
def frameToM(frame : int) -> float:
    return float(frame-1)*HEIGHT


def lineToM(frame:int , line:int) -> float:
    return HEIGHT * (frame-line/LINES)


def pixelToOffset(pixel:int) -> float:
    return WIDTH*0.5-pixel*WIDTH/PIXELS


#need frame arg to distinguish end from start of next frame
def mToLine(m,frame):
    if np.isfinite(m):
        startM = frameToM(frame)
    #    endM = frame*HEIGHT
        r = LINES - LINES*(m-startM)/HEIGHT
    return clamp(r,0,LINES)
    

#(m:float[],frame:int)->int[]
def vectorizedMToLine(m,frame):
    startM = frameToM(frame)
    return np.clip(LINES - LINES*(m-startM)/HEIGHT,0,LINES).astype(int)


#float/np float -> int
def offsetToPixel(offset):
    if np.isfinite(offset):
        return clamp(round(PIXELS * 0.5 - offset * PIXELS / WIDTH ),0,PIXELS)
    else:
        return 0
  

#-> int[]
def vectorizedOffsetToPixel(offsets):
    return np.clip(PIXELS * 0.5 - offsets * PIXELS / WIDTH,0,PIXELS).astype(int)

