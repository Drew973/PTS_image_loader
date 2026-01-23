# -*- coding: utf-8 -*-
"""
Created on Thu Jan  8 15:00:59 2026

@author: Drew.Bennett
"""



from image_loader import gps
from image_loader.db_functions import defaultDb,createDb
import os

from image_loader.gps import curve,MXY

from image_loader import test
import numpy as np

def testUpload():
    createDb()
    mfv = 'test'
   
  #print(curve.point(0))
    f = os.path.join(test.testFolder,'CRAMWELL 20240202 MFV2 01-rutacd-1.csv')
    c = gps.curve.fromRutacd(f)
    print(c)
   
    c.upload(db = defaultDb() , mfvNumber = mfv)
    c2 = gps.curve.fromDatabase(db = defaultDb() , mfvNumber = mfv)    


    print('offsetPoint:',c.offsetPoint(100,10))
   
   
    print(c.gcps(50,0.0,0.0))


def testCurve():
    n = 10
    m = np.linspace(0,100,n)
    x = np.linspace(0,1000,n)
    y = np.linspace(0,10,n)
    points = [MXY(m,x[i],y[i]) for i,m in enumerate(m)]

    c = curve.fromPoints(points)
    perp = c.leftPerp(50)#(0,1) for horizontal line
    print(perp)

    p = c.offsetPoint(50,10)#(50,10)
    print(p)

if __name__ == '__console__':
  #  testUpload()
    testCurve()
 
    
    
    
    