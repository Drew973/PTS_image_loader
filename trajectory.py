# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 07:45:21 2023

@author: Drew.Bennett


module for trajectories.
linestringM
uses SQLITE for performance with large number of points.


"""


W = 0.5


import sqlite3
import numpy

setupScript = '''create table if not exists points(m float unique
,x float
,y float
,last_m float
,next_m float);

    create index if not exists m on points(m);
    create index if not exists x on points(x);
    create index if not exists y on points(y);
    '''
    
    
    
def dist(x1,y1,x2,y2):
    return numpy.sqrt((x1-x2)*(x1-x2) + (y2-y1)*(y2-y1))
    

#perpendicular vector to left.
#numpy.array -> numpy.array
def leftPerp(vector):
    return numpy.array([ - vector[1],vector[0]])


#numpy.array -> numpy.array
def unitVector(vector):
    return vector/(vector**2).sum()**0.5


def normalizeRows(a):
    s = a*a
    rowSums = numpy.sqrt(s.sum(axis=1))
    return a / rowSums[:, numpy.newaxis]


def testNormalize():
    a = numpy.array([[0,10],[0,100],[10,10],[-10,-10]])
    print(normalizeRows(a))
    
    
xyType = [('x',numpy.double),('y',numpy.double)]
    
    
class trajectory:
    
    def __init__(self,con = None):
        if con is None:
            self.con = sqlite3.connect(":memory:")
            #self.con = sqlite3.connect("test_traj.db")
        cur = self.con.cursor()
        cur.executescript(setupScript)
        self.con.commit()
    
    
    def line(self,startM,endM,maxPoints):
        q = '''select :s
                ,last.x + (next.x-last.x)*(:s - last.m)/(next.m-last.m)
                ,last.y + (next.y-last.y)*(:s - last.m)/(next.m-last.m)
                from
                (select m,x,y,next_m from points where m <= :s and next_m > :s) last
                inner join points as next on next.m = last.next_m
        union		
        select m,x,y from points where :s<= m and m <= :e
        UNION
        select :e
                ,last.x + (next.x-last.x)*(:e - last.m)/(next.m-last.m)
                ,last.y + (next.y-last.y)*(:e - last.m)/(next.m-last.m)
                from
                (select m,x,y,next_m from points where m <= :e and next_m > :e) last
                inner join points as next on next.m = last.next_m
        order by m
        limit {maxPoints}
        '''.format(maxPoints=maxPoints)

        cur = self.con.execute(q,{'s':startM,'e':endM})
        return numpy.array([row for row in cur.fetchall()],dtype = numpy.double)

    
    
    def count(self):
        cur = self.con.execute('select count(m) from points')
        r = cur.fetchone()
        return r[0]
    
  
    #-> [(m,offset)] for each line segment in maxDistance
    #point is 1D array [x,y]
    def locatePoint(self,point,minM=0,maxM=numpy.inf,maxDist = 10.0):
        
        x = point[0]
        y = point[1]
        #lines starting within maxDist square of point. good enough where maxDist >> line_length
        q = '''select p.m,p.x,p.y,n.m as next_m,n.x as next_x,n.y as next_y from 
        points as p inner join points as n on n.m = p.next_m
        and :x - :d <= p.x and p.x <= :x + :d and :y - :d <=p.y and p.y <= :y+:d
        and :minM <= n.m and p.m <= :maxM
        order by p.m
        '''
       
        cur = self.con.execute(q,{'x':x,'y':y,'d':maxDist,'minM':minM,'maxM':maxM})
        lastEnd = None
        mod = []#m,offset,dist
        
        for r in cur.fetchall():
            start = numpy.array([r[1],r[2]])
            end = numpy.array([r[4],r[5]])
            
            f,offset = fractionAndOffset(start,end,point)
            m = r[0] + (r[3]-r[0]) * f
            
            if f < 0:
                dist = magnitude(start-point)
            if 0 <= f and f <= 1:
                dist = abs(offset)
            if f > 1:
                dist = magnitude(end-point) 
                
            startM = r[0]
            if startM != lastEnd:
                mod.append((m,offset,dist))
            else:
                if dist < mod[-1][2]:
                    mod[-1] = (m,offset,dist)
            
            lastEnd = r[3]
                
        return [(row[0],row[1]) for row in sorted(mod, key=lambda x: x[2])]#sort by distance
        
    
    def runQuery(self,query,values):
        cur = self.con.cursor()
        cur.execute(query,values)
        
    
    #points along centerline. start/end interpolated.
    #array m -> array x,y
    #nan where m out of range
    #something wrong in here. same x,y for different m.
    def interpolatePoints(self,mValues):
        cur = self.con.cursor()
        r = []
        q = '''select
        last.x + (next.x-last.x)*(:m - last.m)/(next.m-last.m) as x
        ,last.y + (next.y-last.y)*(:m - last.m)/(next.m-last.m) as y
        from
        (select m,x,y,next_m from points where m <= :m and next_m > :m limit 1) last
        inner join points as next on next.m = last.next_m
        '''
        data = [{'m':m} for m in mValues]
        for d in data:
            cur.execute(q,d)
            row = cur.fetchone()
            if row is not None:
                r.append(row)
            else:
                r.append((numpy.nan,numpy.nan))
                
        
        return numpy.array(r,dtype = xyType)
    
    
    #array of m
    def leftPerp(self,m,w = W):
        f = self.interpolatePoints(m+w) - self.interpolatePoints(m-w)#forward direction [[x,y],]
        n = numpy.empty(shape = f.shape,dtype = f.dtype)
        n['x'],n['y'] = -1*n['y'],n['x']
        n = normalizeRows(n)
        return n
    
    
    #2 column array [m,offset]
    def offsetPoints(self,vals, w = W):
        print('m',vals['m'])
        cent = self.interpolatePoints(vals['m'])#x,y
        p = self.leftPerp(vals['m'],w)
        print('cent',cent)
        print('perp',p)
        return cent + p*vals['offset'] #original+offset*perp

    
# find left offset of points
    def findOffsets(self,m,pt,w = W):
        s = self.interpolatePoints(m - w)
        e = self.interpolatePoints(m + w)
        r = []
        for i,v in enumerate(s):
            r.append(fractionAndOffset(s[i],e[i],pt[i])[1])
        return numpy.array(r,dtype=numpy.double)


    #return array of points x,y given m and offset                 
    def point(self,m,offset,w = W):
        centers = self.interpolatePoints(numpy.array([m-w,m,m+w]))
        perp = unitVector(leftPerp(centers[2]-centers[0]))
        return centers[1] + perp*offset
        
    
    #3 col array of m,x,y
    def setValues(self,vals):
        print('setValues',vals)
        cur = self.con.cursor()
        cur.execute('delete from points')
        cur.executemany('insert into points(m,x,y) values (?,?,?)',[tuple(row) for row in vals])
        cur.execute('update points set next_m = (select m from points as np where np.m>points.m order by np.m limit 1)')
        cur.execute('update points set last_m = (select m from points as lp where lp.m<points.m order by lp.m desc limit 1)')
        

    def values(self):
        cur = self.con.cursor()
        cur.execute('select m,x,y from points order by m')
        t = [('m',numpy.double),('x',numpy.double),('y',numpy.double)]
        return numpy.array([row for row in cur.fetchall()],dtype = t)
    
    
    def __del__(self):
        self.con.commit()
     

    
def magnitude(v):
    return numpy.linalg.norm(v)
    

#(distance/linelength,offset)
#start = start point of line
#end: end point of line
#point x,y

#numpy array. start and end x,y. point :  numpy array x,y
def fractionAndOffset(start,end,point):
    se = end-start
    sp = point-start
    f = numpy.dot(se,sp)/numpy.sum(se*se)#fraction
    offset = numpy.cross(se,sp)/magnitude(se)
    return (f,offset)
    
        
def testFractionAndOffset():
    s = numpy.array([0,0])
    e = numpy.array([10,10])
    p = numpy.array([100,100])
    
    f = fractionAndOffset(s,e,p)
    print(f)
    
    
def test():
    t = trajectory()
    vals = [[3.00000000e+00,4.98621220e+05,3.62690619e+05]
    ,[4.00000000e+00,4.98620993e+05,3.62691471e+05]
    ,[5.00000000e+00,4.98620675e+05,3.62692297e+05]
    ,[6.00000000e+00,4.98620307e+05,3.62693110e+05]
    ,[7.00000000e+00,4.98619899e+05,3.62693915e+05]
    ,[8.00000000e+00,4.98619457e+05,3.62694729e+05]
    ,[9.00000000e+00,4.98619006e+05,3.62695564e+05]
    ,[1.00000000e+01,4.98618556e+05,3.62696412e+05]
    ,[1.10000000e+01,4.98618118e+05,3.62697329e+05]
    ,[1.20000000e+01,4.98617708e+05,3.62698306e+05]]
        
    vals = numpy.array(vals,dtype = numpy.double)
    t.setValues(vals)
    #print(t.values())
  #  p = t.interpolatePoints([20,30,50,999])
  #  print(p)
    
   # r = t.locatePoint(numpy.array([5,5]))#2,0
    #r = t.locatePoint(numpy.array([4,4]))#2,0

    p = numpy.array([[5.5,5.0],[9.0,5.0]])

    r = t.offsetPoints(p)
    
    print(r)
    del t    
     
    
if __name__ in ('__main__','__console__'):
    test()
    
    
    
    
    