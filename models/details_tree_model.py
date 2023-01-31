# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 12:00:08 2023

@author: Drew.Bennett






hard to display in QTableView.





"""





from PyQt5.QtGui import QStandardItemModel,QStandardItem
from PyQt5.QtCore import Qt,QModelIndex


cols = {'run':0,
        'name':1,
        'image_id':2,
        'load':3,
        'file_path':4,
        'groups':5
        }



detailCols = {'name':0,
              'image_id':1,
              'load':2,
               'file_path':3,
               'groups':4}



runCols = {'run':0,
           'max_id':1,
           'min_id':2}


minRole = Qt.UserRole
maxRole = Qt.UserRole+1
startRole = Qt.UserRole+2
endRole = Qt.UserRole+3


'''
hierarchal model to store both details and aggregated run info


markBetween dialog.
    startId,
    endId,
    unmark others checkbox.


'''
class detailsTreeModel(QStandardItemModel):
    
    
    def __init__(self,parent=None):
        super().__init__(0,1,parent=parent)
        #self.setHorizontalHeaderLabels(['run','name','image id','load','file path','groups'])
        self.setHorizontalHeaderLabels([k for k in cols])

        
    #order by imageId
    def addDetail(self,run,imageId,load=False,filepath='no filePath',groupsString='no groups'):
        ri = self.runItem(run)
        if ri is None:
            ri = self._addRun(run)
        
        
        items = [toItem(''),toItem('no name'),toItem(imageId),toItem(load),toItem(filepath),toItem(groupsString)]
        
        ri.appendRow(items)
    
    
    
    def addDetails(self,details):
        for d in details:
            pass
            
            
            
    def _updateRun(self,runItem):
        i = self.indexFromItem(runItem)
        ids = []
        
        idCol = cols['image_id']
        
        for r in range(self.rowCount(i)):
            ids.append(self.index(r,idCol,i).data())
            
            
            
        if not ids:
            self.invisibleRootItem().removeRow(runItem.row())
            return
        
       # print(ids)
        
        maxId = max(ids)
        minId = min(ids)
        
        
        runItem.setData(maxId,minRole)
        runItem.setData(minId,maxRole)


        #store start value for dialog here...?
        #probabaly easier to handle in dialog.
     #   s = runItem.data(startRole)
     #   if s is None:
     #       s = minId
     #   runItem.setData(clamp(s,minId,maxId),startRole)
        
        
    #    e = runItem.data(endRole)
    #    if e is None:
     #       e = minId        
    #    runItem.setData(clamp(e,minId,maxId),endRole)

    
    def runItem(self,run):
        
        for r in range(self.rowCount()):
            i = self.item(r,0)
            if i.data(Qt.EditRole) == run:
                return i
    
    
    #make alphabetical
    
    def _addRun(self,run):
        root = self.invisibleRootItem()
        i = QStandardItem()
        i.setData(run,Qt.EditRole)
        
        root.appendRow(i)
        return i
            
        
        
    def indexIsRun(self,index):
        if index.isValid():
            return not index.parent().isValid()
        return False
     
    
    def indexIsDetail(self,index):
        return index.parent().isValid()
        
    

    def dropDetails(self,indexes):
        toRemove = {}
        for i in indexes:
            if self.indexIsDetail(i):
                runItem = i.parent().row()
                
                if runItem in toRemove:
                    toRemove[runItem].append(i.row())
                else:
                    toRemove[runItem] = [i.row()]
                
        for runRow in toRemove:
            runItem = self.itemFromIndex(self.index(runRow,0))
            for row in reversed(sorted(toRemove[runRow])):
                runItem.removeRow(row)
                self._updateRun(runItem)
        
        
    
        
        
        
def toItem(data):
    i = QStandardItem()
    i.setData(data,Qt.EditRole)
    return i


def clamp(n,minimum,maximum):
    if n < minimum:
        return minimum
    
    if n > maximum:
        return maximum
    
    return n



from PyQt5.QtWidgets import QTreeView
from PyQt5.QtWidgets import QMenu,QAbstractItemView


class imageTreeView(QTreeView):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        
        self.contextRun = QModelIndex()
        
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

        self.detailMenu = QMenu(self)

        markAct = self.detailMenu.addAction('Mark to load')     
        markAct.triggered.connect(self.mark)

        unmarkAct = self.detailMenu.addAction('Unmark to load')     
        unmarkAct.triggered.connect(self.unmark)
    
        dropAct = self.detailMenu.addAction('Remove')
        dropAct.triggered.connect(self.dropSelected)
    
        self.runsMenu = QMenu(self)
        markBetweenAct = self.runsMenu.addAction('Mark between...')     
        markBetweenAct.triggered.connect(self.showMarkBetweenDialog)
    
        markAllAct = self.runsMenu.addAction('Mark all')     
        markAllAct.triggered.connect(self.markAll)
    
        unmarkAllAct = self.runsMenu.addAction('unmark all')     
        unmarkAllAct.triggered.connect(self.unMarkAll)
    
    
    
    def contextMenuEvent(self, event):
        
        index = self.indexAt(event.pos())#index that was right clicked
        if index.isValid():

            if self.model().indexIsDetail(index):
                self.detailMenu.exec_(self.mapToGlobal(event.pos()))
                self.contextRun = QModelIndex()
            
            
            if self.model().indexIsRun(index):
                self.contextRun = index
                self.runsMenu.exec_(self.mapToGlobal(event.pos()))


    def dropSelected(self):
        self.model().dropDetails(self.selectionModel().selectedRows(2))



    def mark(self):
        loadCol = cols['load']

        for i in self.selectionModel().selectedRows(loadCol):
            if self.model().indexIsDetail(i):
                self.model().setData(i,True)
    
    
    #mark all in run
    def markAll(self):
        pass
    
    
    #unmark all in run
    def unMarkAll(self):
        pass
    
    #unmark selected details
    def unmark(self):
        loadCol = cols['load']
        
        for i in self.selectionModel().selectedRows(loadCol):
            if self.model().indexIsDetail(i):
                self.model().setData(i,False)


    def showMarkBetweenDialog(self):
        print(self.contextRun)

    
    #mark run betwwen ids
    def markBetween(self):
        pass
        
    

m = detailsTreeModel()

#m.addRun('a')
#m.addRun('b')

#m.runItem('a')

m.addDetail(run = 'a',imageId = 3)
m.addDetail(run = 'a',imageId = 4)
m.addDetail(run = 'a',imageId = 5)


m.addDetail(run = 'b',imageId = 3)

m._updateRun(m.runItem('a'))

#rowCount counts only childen of root.

#proxy = detailsProxy()
#proxy.setSourceModel(m)

 
#v = QTableView()
v = imageTreeView()
v.setModel(m)
#v.setHeaderHidden(True)
v.show()