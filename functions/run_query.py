# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 09:22:35 2022

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlQuery
from image_loader import exceptions


    #checks query text and returns QSqlQuery
def preparedQuery(text,db):
    query = QSqlQuery(db)
    if not query.prepare(text):
        print(text)
        raise exceptions.imageLoaderQueryError(query)
    return query



#attempts to run query .Raise imageLoaderQueryError on failure.

#"For SQLite, the query string can contain only one statement at a time. If more than one statements are give, the function returns false"
#Wrong. Query doesn't execute but exec() is returning True
def runQuery(text,db,bindValues={}):
    q = preparedQuery(text,db)
    
    for k in bindValues:
        q.bindValue(k,bindValues[k])
    
    if not q.exec():
        raise exceptions.imageLoaderQueryError(q)
    return q