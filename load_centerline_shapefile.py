from PyQt5.QtSql import QSqlQuery
from image_loader.db_functions import defaultDb,queryPrepareError,queryError,runQuery


def parseCenterlineShapefile(layer):
    m = 0.0
    last = None
    i = 0
    for f in layer.getFeatures():
        for v in f.geometry().vertices():
            if i==0:
                last = v
                m = 0.0
            else:
                m += v.distance(last) 
                v.x()
                v.y()
            yield {'id':i,'m':m,'lon':v.x(),'lat':v.y()}
            i+=1
           
def loadCenterlineShapefile(file):
    db = defaultDb()
    db.transaction()
    runQuery('delete from p',db=db)
    
    
    q = QSqlQuery(db)
    if not q.prepare('insert into p(id,m,pt) values (:id,:m,st_transform(MakePoint(:lon,:lat,4326),27700))'):
        raise queryPrepareError(q)
        
    for r in parseCenterlineShapefile(file):
        q.bindValue(':id',r['id'])
        q.bindValue(':m',r['m'])
        q.bindValue(':lon',r['lon'])
        q.bindValue(':lat',r['lat'])
    
        if not q.exec():
            print(q.boundValues())
            raise queryError(q)
    db.commit()
    
    
    
layer = QgsProject.instance().mapLayersByName('2023-01-21 10h08m11s GPS MFV1_007(Polyline)')[0]
loadCenterlineShapefile(layer)
