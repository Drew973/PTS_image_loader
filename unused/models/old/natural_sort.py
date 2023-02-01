# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 15:11:00 2022

@author: Drew.Bennett


SortFilterProxyModel with natural sort order.

https://en.wikipedia.org/wiki/Natural_sort_order


"""

from PyQt5.QtCore import QSortFilterProxyModel
#import re


class naturalSortFilterProxyModel(QSortFilterProxyModel):
  #  @staticmethod
    #def _human_key(key):
    #    parts = re.split('(\d*\.\d+|\d+)', key)
    #    return tuple((e.swapcase() if i % 2 == 0 else float(e)) for i, e in enumerate(parts))

   # def lessThan(self, left, right):
    #    leftData = str(self.sourceModel().data(left))
    #    rightData = str(self.sourceModel().data(right))
      #  return self._human_key(leftData) < self._human_key(rightData)
    
    
    def lessThan(self, left, right):
        return lessThan(str(left.data()),str(right.data()))
    
    
    #alphabetical. treat multi digit numbers as single charactor.
    
    
def isDigit(char):
    return char in ['1','2','3','4','5','6','7','8','9','0']
    
#split str into charactors. merge adjacant numbers[str]
def toList(string):
    r = []
    for c in string:
        if len(r) ==0:
            r.append(c)
        else:
            if isDigit(r[-1]) and isDigit(c):
                r[-1] = r[-1]+c
            else:
                r.append(c)
    return r
            


def isInt(string):
    try:
        int(string)
        return True
    except Exception:
        return False
    

#compare strings. convert to int if possible.
def lt(string1,string2):
    if isInt(string1) and isInt(string2):
        return int(string1) < int(string2)
    return string1 < string2
    

#true if a<b
def lessThan(a,b):
    a = toList(a)
    b = toList(b)
    
    for i in range(min([len(a),len(b)])):
        if lt(a[i],b[i]):
            return True
        if lt(b[i],a[i]):
            return False
        
    if len(a)<len(b):
        return True
    
    return False
        
    
    

#print(toList('test10g45'))
#print(lessThan('ab10cd','ab1cd'))#should be false
#print(lessThan('ab1cd','ab10cd'))#should be True
#print(lessThan('ab1cd','ab1cd'))#should be False
#print(lessThan('ac1cd','ab10cd'))#should be False
#print(lessThan('',''))#should be False

print(lessThan('1','10'))#should be true
print(lessThan('3','27'))#should be True
