# -*- coding: utf-8 -*-
"""
Created on Tue Jan 28 08:57:51 2025

@author: Drew.Bennett
"""

from image_loader.db_functions import runQuery



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
