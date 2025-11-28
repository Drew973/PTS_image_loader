import numpy as np
from scipy.interpolate import CubicSpline
import csv
from collections import namedtuple





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






# Declaring namedtuple()
coefficient = namedtuple('coefficient', ['start', 'end', 'x_0','x_1','x_2','x_3'])
K = 3


def coefficients(cs , xVals):
    t = '{start}<=x<= {end}: y = {a} + {b}(x-{start}) + {c}(x-{start})^2 + {d}(x-{start})^3'
    for i,v in enumerate(cs.c):
        print(t.format(start = xVals[i],
                       end = xVals[i+1],
                       a = cs.c.item(3,i),
                       b = cs.c.item(2,i),
                       c = cs.c.item(1,i),
                       d = cs.c.item(0,i)
                       ))



 





# calculate 5 natural cubic spline polynomials for 6 points
# (x,y) = (0,12) (1,14) (2,22) (3,39) (4,58) (5,77)
x = np.array([0, 1, 2, 3, 4, 5])
y = np.array([12,14,22,39,58,77])

# calculate natural cubic spline polynomials
spline = CubicSpline(x,y,bc_type='natural')
coefficients(spline , x)
