# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:01:00 2023

@author: Drew.Bennett


corrections done as xy shift per point.
offset direction from dx/dm and dy/dm

"""

from scipy.interpolate import UnivariateSpline
import numpy as np
from image_loader.db_functions import runQuery
from image_loader import dims


k = 2 #degree of splines. 1=linear, 2 = quadratic, 3=cubic
#derivitives and perpendicular direction discontinuous for linear.


correctionsK = 1

class splineModel:
    
    def __init__(self):
        self.download()
        self.downloadCorrections()


    def download(self):
        q = runQuery('select m,st_x(pt),st_y(pt) from original_points order by m')
        m = []
        x = []
        y = []
        while q.next():
            m.append(q.value(0))
            x.append(q.value(1))
            y.append(q.value(2))
        self.xSpline = UnivariateSpline(m, x,k=k)
        self.ySpline = UnivariateSpline(m, y,k=k)
        self.xDerivitive = self.xSpline.derivative(1)
        self.yDerivitive = self.ySpline.derivative(1)    


    def downloadCorrections(self):
        mo = []
        newXY = []
        q = runQuery('select frame_id,line,pixel,new_x,new_y from corrections order by frame_id,line desc ')
        while q.next():
            mo.append((dims.lineToM(frame = q.value(0),line = q.value(1)),dims.pixelToOffset(q.value(2))))
            newXY.append((q.value(3),q.value(4)))
        mo = np.array(mo,dtype=np.float)
        newXY = np.array(newXY,dtype=np.float)
        shifts = newXY - self.xy(mo,corrected=False)
        m = mo[:,0]
        self.xCorrection = UnivariateSpline(m, shifts[:,0], k = correctionsK,ext=3)
        self.yCorrection = UnivariateSpline(m, shifts[:,1], k = correctionsK,ext=3)

        
    def xy(self,mo,corrected=False):
        m = mo[:,0]
        xy = np.transpose(np.vstack([self.xSpline(m),self.ySpline(m)]))
        #offsets if necessary
        if mo.shape[1]>1:
            xy += self.leftPerp(m)*mo[:,1][:,np.newaxis]
        #add xy shifts to each point
        if corrected:
            xy[:,0] += self.xCorrection(m)
            xy[:,1] += self.yCorrection(m)
        return xy
        
        
        
    def moSingle(self,x,y,corrected=False,maxDist = 10):
        q = runQuery('select m from original_points where distance(pt,makePoint(:x,:y,27700)) <= :d order by distance(pt,makePoint(:x,:y,27700)) limit 1',values = {':x':x,':y':y,':d':maxDist})                         
        while q.next():
            nearest = q.value(0)
            
        def sqdist(m):
            (self.xSpline(m)-x)*(self.xSpline(m)-x) + (self.ySpline(m)-y)*(self.ySpline(m)-y)

        
    def sqDist(self,m,x,y):
        return (self.xSpline(m)-x)*(self.xSpline(m)-x) + (self.ySpline(m)-y)*(self.ySpline(m)-y)
        
        
    #perpendicular unit vectors at m
    def leftPerp(self,m):
        dx = self.xDerivitive(m)
        dy = self.yDerivitive(m)
        magnitudes = np.sqrt(dx*dx+dy*dy)
        return np.transpose((np.vstack([-dy/magnitudes,dx/magnitudes])))
    
    
    
#UnivariateSpline(x, y,k=2)

if __name__ in ('__main__','__console__'):
    m = splineModel()
    mo = np.array([(0,0),(10,0),(20,5)],dtype = np.float)
    xy = m.xy(mo,corrected=True)
    print('xy',xy)