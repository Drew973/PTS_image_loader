import numpy as np
from scipy.interpolate import CubicSpline , UnivariateSpline,splrep,PPoly
import csv
from collections import namedtuple

from image_loader import db_functions
from image_loader.db_functions import prepareQuery,queryError,createDb
from PyQt5.QtSql import QSqlDatabase

K = 2
S = 0.5


#ESPG:4326
#meant for rutacd csvs. 1m intervals
def parseCsv(file : str , interval = 5):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        for i , d in enumerate(reader):
            try:
                # need round to avoid floating point errors like int(1.001*1000) = 1000
                m : int = round(float(d['Chainage (km)'])*1000)
                lon = float(d['Longitude (deg)'])
                lat = float(d['Latitude (deg)'])
                alt = float(d['Altitude (m)'])
                yield ( m , lon , lat , alt )
            except Exception as e:
                print(e)
                pass






#--for start_m <= m <= end_m:
#--x = x0 + x1 * (m-start_m) + x2*(m-start_m)^2 + x3*(m-start_m)^3
#--y = y0 + y1 * (m-start_m) + y2*(m-start_m)^2 + y3*(m-start_m)^3




#y = c0 + c_1*(x-start) + c_2 * (x-start)^2 + c_3*(x-start)^3
coefficient = namedtuple('coefficient', ['start', 'end', 'c_0','c_1','c_2','c_3'])


#K = 3

#cs = cubic spline
#xVals = array of x values used to make spline.
def coefficients(cs , xVals):
    
    for i,v in enumerate(cs.c[0]):
        yield coefficient(start = xVals[i],
                          end = xVals[i+1],
            c_0 = cs.c.item(3,i),
            c_1 = cs.c.item(2,i),
            c_2 = cs.c.item(1,i),
            c_3 = cs.c.item(0,i)
                          )




def test1():
    # calculate 5 natural cubic spline polynomials for 6 points
    # (x,y) = (0,12) (1,14) (2,22) (3,39) (4,58) (5,77)
    x = np.array([0, 1, 2, 3, 4, 5])
    y = np.array([12,14,22,39,58,77])
    # calculate natural cubic spline polynomials
    spline = CubicSpline(x,y,bc_type='natural')
    quadSpline = UnivariateSpline(x, y , s = 0, ext='const', k = 2)
    for c in coefficients(spline , x):
        print(c)
        
        
    
#update x_spline and y_spline tables from original_points table for mfv number

def recalcSplineTable(db:QSqlDatabase , mfv:str):
    
    db = db_functions.defaultDb()
    db.transaction()
    db_functions.runQuery('delete from x_spline where mfv_number = :mfv', values = {':mfv':mfv} , db = db)
    db_functions.runQuery('delete from y_spline where mfv_number = :mfv', values = {':mfv':mfv} , db = db)

    
    
    mVals = []
    xVals = []
    yVals = []
    q = db_functions.runQuery('select m,x,y from original_points order by m' , db = db)
    while q.next():
        mVals.append(q.value(0))
        xVals.append(q.value(1))
        yVals.append(q.value(2))
        
  
    #update x_spline table
    xSpline = PPoly.from_spline(splrep(x = mVals, y = xVals, s = S, k=K))#PPoly
  #  print(xSpline.c)# [...quadratic term,linear,constant]
  #  print(xSpline.x)# start m


    xQuery = prepareQuery('insert into x_spline(mfv_number,start_m,end_m,x0,x1,x2) values (:mfv,:start_m, :end_m, :x0 , :x1 ,:x2)' , db = db)


    for i,m in enumerate(xSpline.x[0:-1]):
        xQuery.bindValue(':mfv' , mfv)
        xQuery.bindValue(':start_m' , float(m))
        xQuery.bindValue(':end_m' , float(xSpline.x[i+1]))
        xQuery.bindValue(':x0' , float(xSpline.c.item(2,i)))
        xQuery.bindValue(':x1' , float(xSpline.c.item(1,i)))
        xQuery.bindValue(':x2' , float(xSpline.c.item(0,i)))
        if not xQuery.exec():
            raise queryError(xQuery)


    #update y_spline table
    ySpline = PPoly.from_spline(splrep(x = mVals, y = yVals, s = S, k=K))#PPoly
    yQuery = prepareQuery('insert into y_spline(mfv_number,start_m,end_m,y0,y1,y2) values (:mfv,:start_m, :end_m, :y0 , :y1 ,:y2)' , db = db)
    for i,m in enumerate(ySpline.x[0:-1]):
        yQuery.bindValue(':mfv' , mfv)
        yQuery.bindValue(':start_m' , float(m))
        yQuery.bindValue(':end_m' , float(ySpline.x[i+1]))
        yQuery.bindValue(':y0' , float(ySpline.c.item(2,i)))
        yQuery.bindValue(':y1' , float(ySpline.c.item(1,i)))
        yQuery.bindValue(':y2' , float(ySpline.c.item(0,i)))
        if not yQuery.exec():
            raise queryError(yQuery)


    db.commit()



if __name__ in ('__main__','__console__'):
    db = createDb()
    recalcSplineTable(db = db , mfv = 'test')
