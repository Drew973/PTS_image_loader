# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 09:22:36 2022

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
 
        
    q = '''
            CREATE TABLE if not exists runs (
                run varchar NOT NULL primary key,
                load bool default False,
                min_id int,
                max_id int,
                start_id int default -1 not null,
                end_id int default -1 not null        
            )
        ''' 
    db.exec(q)
    db.commit()
    return db