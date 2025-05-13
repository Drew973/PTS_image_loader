# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 08:57:51 2025

@author: Drew.Bennett
"""

from image_loader.db_functions import runQuery

from image_loader import dims

#only used for testing
def allImagePks():
    pks = []
    query = runQuery('select pk from images order by pk')
    while query.next():
        pks.append(query.value(0))
    return pks




#only used for testing
def allRunPks():
    q = runQuery('select pk from runs order by pk')
    pks = []
    while q.next():
        pks.append(q.value(0))        
    return pks


def clearImages():
    q = runQuery('delete from images')



#start_frame,end_frame
def frameRange(runPk:int):
    q = runQuery('select start_frame,end_frame from runs where pk = :pk',values = {':pk':runPk})
    while q.next():
        return (q.value(0),q.value(1))
    return (0,int(dims.MAX))
    
    



