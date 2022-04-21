# -*- coding: utf-8 -*-
"""
Created on Wed Apr 20 09:21:38 2022

@author: Drew.Bennett

unused
"""

from PyQt5.QtCore import QSortFilterProxyModel,QRegExp
from PyQt5.QtWidgets import QFileDialog



'''
'''
class regexFileModel(QSortFilterProxyModel):
        
    def __init__(self,expression,parent = None,caseSensitive=False):
        super().__init__(parent)
        self.expression = QRegExp(expression)
        self.caseSensitive = caseSensitive
    
    def filterAcceptsRow(self,sourceRow,sourceParent):
        index0 = self.sourceModel().index(sourceRow, 0, sourceParent);
        fileModel = self.sourceModel()
        
        if fileModel.isDir(index0) or fileModel is None:
            return True
        
        fn = fileModel.fileName(index0)#filename
        if not self.caseSensitive:
            fn = fn.lower()
        
        return self.expression.exactMatch(fn)

'''
returns list of files.
filters by regex filterExpression (filename will be treated as lower case when not caseSensitive).
also filters by extensionFilter.
untested for saving.

not working. sidebar not showing bookmarks
'''
def getFileName(filterExpression,parent=None,mode=QFileDialog.ExistingFile,caption='',dir='',extensionFilter='',caseSensitive=False):   
    
    dialog = QFileDialog(parent,caption=caption)
    dialog.setOption(QFileDialog.DontUseNativeDialog)
    dialog.setSidebarUrls(QFileDialog().sidebarUrls())#dirty hack
    dialog.setFileMode(mode)
    dialog.setProxyModel(regexFileModel(filterExpression))
    dialog.setNameFilter(extensionFilter)
    dialog.setDirectory(dir)
    if dialog.exec():
        return dialog.selectedFiles()



if __name__ == '__console__':
    expression = '.*Raster Image Load.*'
    mode = QFileDialog.ExistingFile
    extensionFilter = "txt (*.txt)"
    
    print(getFileName(expression,
    mode,
    parent = None,
    dir = '',
    caption ='a caption',
    extensionFilter=extensionFilter))
