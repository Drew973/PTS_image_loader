# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 08:52:11 2024

@author: Drew.Bennett
"""

from PyQt5.QtWidgets import QStyledItemDelegate

class noEditDelegate(QStyledItemDelegate):
    def setModelData(self,editor,model,index):
        return