# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 08:57:19 2024

@author: Drew.Bennett
"""

from PyQt5.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt5.QtWidgets import QTableView


SERVER_NAME = 'PTS-DBEN-DV3500\SQLEXPRESS'
DATABASE_NAME = 'HAWKEYE001'
USERNAME = ''
PASSWORD = ''

def createConnection():
    connString = f'DRIVER={{SQL Server}};'\
                f'SERVER={SERVER_NAME};'\
                f'DATABASE={DATABASE_NAME}'

    global db
    db = QSqlDatabase.addDatabase('QODBC')
    db.setDatabaseName(connString)

    if db.open():
        print('connect to SQL Server successfully')
        return True
    else:
        print('connection failed')
        return False

def displayData():
    print('processing query...')
    qry = QSqlQuery(db)
    
    qry.prepare('select * from  dbo.tbResultsLcmsJoints limit 100')
    qry.exec()

    model = QSqlQueryModel()
    model.setQuery(qry)

    view = QTableView()
    view.setModel(model)
    return view    

if __name__=='__console__':
  #  app = QApplication(sys.argv)

    if createConnection():
        dataView = displayData()
        dataView.show()
        
