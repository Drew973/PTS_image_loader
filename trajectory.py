# -*- coding: utf-8 -*-
"""
Created on Wed Oct 25 07:45:21 2023

@author: Drew.Bennett


module for trajectories.
linestringM
uses SQLITE for performance with large number of points.


"""



import sqlite3
import numpy

setupScript = '''create table if not exists points(m float,x float,y float,last_m float,next_m float);
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
    
  
    #-> (m,offset)
    #point is array x,y
    #could add locatePoints() array x,y -> array m,offset
    def locatePoint(self,point,minM=0,maxM=numpy.inf,maxDist = 20.0):
        
        x = point[0]
        y = point[1]
        #lines starting within maxDist square of point. approximation as ignores lines ending but not starting within distance.
        q = '''select p.m,p.x,p.y,next.m as next_m,next.x as next_x,next.y as next_y from 
        points as p inner join points as next on next.m = p.next_m and abs(p.x-:x) <= :d and abs(p.y-:y) <= :d
        and :minM <= next.m and p.m <= :maxM
        '''

        cur = self.con.execute(q,{'x':x,'y':y,'d':maxDist,'minM':minM,'maxM':maxM})
        closest = (0.0,0.0)
        shortestDist = numpy.inf
        
        for r in cur.fetchall():
            start = numpy.array([r[1],r[2]])
            end = numpy.array([r[4],r[5]])
            f,offset = fractionAndOffset(start,end,point)
            m = r[0] + (r[3]-r[0]) * f
            
            if f <0:
                dist = magnitude(start-point)
            if 0 <= f and f <= 1:
                dist = abs(offset)
            if f>1:
                dist = magnitude(end-point) 
                
            if dist < shortestDist:
                closest = (m,offset)
                shortestDist = dist
                
        return closest
        
    #points along centerline. start/end interpolated.
    #array m,offset -> array x,y
    #nan where m out of range
    def interpolatePoints(self,mValues):        
        cur = self.con.cursor()
        r = []
        q = '''select
        last.x + (next.x-last.x)*(:m - last.m)/(next.m-last.m)
        ,last.y + (next.y-last.y)*(:m - last.m)/(next.m-last.m)
        from
        (select m,x,y,next_m from points where m <= :m and next_m > :m) last
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
        return numpy.array(r,dtype = numpy.double)
    
    
    
    
    def point(self,m,offset,w = 2.5):
        centers = self.interpolatePoints(numpy.array([m-w,m,m+w]))
        perp = unitVector(leftPerp(centers[2]-centers[0]))
        return centers[1] + perp*offset
        
    
    #3 col array of m,x,y
    def setValues(self,vals):
        cur = self.con.cursor()
        cur.execute('delete from points')
        cur.executemany('insert into points(m,x,y) values (?,?,?)',[tuple(row) for row in vals])
        cur.execute('update points set next_m = (select m from points as np where np.m>points.m order by np.m limit 1)')
        cur.execute('update points set last_m = (select m from points as lp where lp.m<points.m order by lp.m desc limit 1)')
        

    def values(self):
        cur = self.con.cursor()
        cur.execute('select m,x,y from points')
        return numpy.array([row for row in cur.fetchall()],dtype = numpy.double)
    
    
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
    vals = numpy.array([[1,2,3],[2,5,5],[100,1000,1000]],dtype = numpy.double)
    t.setValues(vals)
    #print(t.values())
  #  p = t.interpolatePoints([20,30,50,999])
  #  print(p)
    
   # r = t.locatePoint(numpy.array([5,5]))#2,0
    r = t.locatePoint(numpy.array([4,4]))#2,0

    print(r)
    del t    
     
    
if __name__ in ('__main__','__console__'):
    test()
    
    
    
    
    