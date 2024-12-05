# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 07:58:02 2024

@author: Drew.Bennett
"""

import pandas as pd
import pyodbc

cnxn_str = (
    r'DRIVER=ODBC Driver 11 for SQL Server;'
    r'SERVER=(local)\SQLEXPRESS;'
    r'Trusted_Connection=yes;'
    r'AttachDbFileName=D:\RAF_BENSON\Hawkeye Database\HAWKEYE001.MDF.mdf;'
)
cnxn = pyodbc.connect(cnxn_str)
df = pd.read_sql("SELECT * FROM Table1", cnxn)




select * from dbo.tbRawDataModuleGps


select * from dbo.tbRawDataModuleDistance inner join dbo.tbRawDataModuleGps
on dbo.tbRawDataModuleDistance.RawDataModuleID = dbo.tbRawDataModuleGps.RawDataModuleID

