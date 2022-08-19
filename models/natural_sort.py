# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 15:11:00 2022

@author: Drew.Bennett


SortFilterProxyModel with natural sort order.

https://en.wikipedia.org/wiki/Natural_sort_order


"""

from PyQt5.QtCore import QSortFilterProxyModel
import re


class naturalSortFilterProxyModel(QSortFilterProxyModel):
    @staticmethod
    def _human_key(key):
        parts = re.split('(\d*\.\d+|\d+)', key)
        return tuple((e.swapcase() if i % 2 == 0 else float(e)) for i, e in enumerate(parts))

    def lessThan(self, left, right):
        leftData = str(self.sourceModel().data(left))
        rightData = str(self.sourceModel().data(right))
        return self._human_key(leftData) < self._human_key(rightData)