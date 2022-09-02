# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 08:41:07 2022

@author: Drew.Bennett
"""

      
def setupDb(db,overwrite = False):
    
   #db.exec("SELECT load_extension('mod_spatialite')")
    
    q = '''
            CREATE TABLE if not exists details (
                pk integer primary key,
                load boolean,
                run varchar NOT NULL,
                image_id int NOT NULL,
                file_path VARCHAR NOT NULL,
                name varchar,
                groups varchar
            )
            '''
    db.exec(q)


    db.exec("SELECT InitSpatialMetadata(1)")
    db.exec("SELECT AddGeometryColumn('details', 'geom', 27700, 'POLYGON')")

    db.commit()
    return db
    

    