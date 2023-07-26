# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:38:07 2023

@author: Drew.Bennett
"""

from image_loader import db_functions
from image_loader.db_functions import runQuery
from shapely import wkt
from shapely.geometry import LineString


def flip(line):
    return LineString(line.coords[::-1])

                      

def offset(line,offset):
    if offset>0:
        return line.parallel_offset(abs(offset),side = 'left',resolution=32)
    else:
        return line.parallel_offset(abs(offset),side = 'right',resolution=32)



def resample(line):
    return LineString([line.interpolate(v,normalized=True) for v in [0,0.2,0.4,0.6,0.8,1]])
    
    


class gpsModel:
    
    
    def __init__(self):
        pass
    
    def loadGps(self,file):
        db_functions.loadGps(file=file)
        
        
    def clear(self):
        db_functions.runQuery('delete from points')
    

    
    """
    def getLine(self,startM:float,endM:float,offset:float=0,run:str=''):->str
    replace with getGCPs method?
    def getLine(self,startM,endM,offset=0,run=''):
        lineQuery = '''select st_asText(line_substring(makeLine(pt)
        ,abs(:start_m-min(m))/abs(max(m)-min(m))
        ,abs(:end_m-min(m))/abs(max(m)-min(m))))
         from points where next_m>=:start_m and last_m<=:end_m order by m
        '''
        q = runQuery(lineQuery,values={':start_m':startM,':end_m':endM})
        while q.next():
            g = q.value(0)
            geom = wkt.loads(g)
         #   print(geom)
            if offset>0:
               # side = 'left'
                return resample(geom.parallel_offset(abs(offset),side = 'left',resolution=8)).wkt
            else:
                return resample(flip(geom.parallel_offset(abs(offset),side = 'right',resolution=8))).wkt#direction inverted for this side?
          #  return geom.parallel_offset(abs(offset),side=side,resolution=64).wkt
    """
    
    
    
    
    
    def getPoint(self,m,run='',offset = 0):
        pass
    
        #get line between nearest 2 points to m.
        #offset it and use st_lineInterpolatePoint
    
    
    #(self,pt:QgsPointXY,run:str)->(m:float,offset:float)
    def getM(self,pt,run=''):
        pass
    
    
    #->bool
    def hasGps(self):
        return db_functions.hasGps()
        
        
        
        
def test():
    m = gpsModel()
    r = m.getLine(startM = 10,endM = 15, offset = 5)
    print(r)
    r = m.getLine(startM = 10,endM = 15, offset = -5)
    print(r)
    
   # g = ' LINESTRING (354570.3559647518 322004.50366052514, 354570.8990242868 322004.0645348509, 354570.8637205029 322004.01389852405, 354570.1085703796 322004.5403912305, 354570.1067056165 322004.54169134836, 354569.43342086725 322004.898035479, 354568.74689906614 322005.2060629779, 354568.19081126584 322005.37101811555, 354567.92643990857 322005.4131623503, 354567.2820186154 322005.51589149056, 354567.29173622513 322005.5768501882, 354567.8116240485 322005.52248441096)'
   # geom = wkt.loads(g)
 #   print(resample(geom))
    
if __name__ in ('__console__','__main__'):
    test()
    