
import sqlite3
from image_loader.models.image_model.details import imageDetails


def dbToCon(db):
    con = sqlite3.connect(db.databaseName())
    con.enable_load_extension(True)
    con.execute('SELECT load_extension("mod_spatialite")')
    return con

def loadDetails(details,useExtents=True):
    db = QSqlDatabase.database('imageLoader')
    con = dbToCon(db)
    cur = con.cursor()
    e = None 
    try:
        data = [(d['run'],d['imageId'],d['filePath'],d['name'],str(d['groups']),d['extents']) for d in details]
        #print(data[0])
        q = 'insert into details(run,image_id,file_path,name,groups,geom) values(?,?,?,?,?,MakePolygon(GeomFromText(?)))'
        cur.executemany(q,data)
        con.commit()
    except Exception as err:
        e = err
        con.rollback()
    finally:
        con.close()
        db.close()
        if e is not None:
            raise e


    
def test():
    testFolder = r'C:\Users\drew.bennett\Documents\image_loader\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
    tifs = [os.path.join(testFolder,f) for f in os.listdir(testFolder) if os.path.splitext(f)[-1]=='.tif']
    details = [imageDetails(t) for t in tifs]
    loadDetails(details)
    
    
if __name__=='__console__':
    test()