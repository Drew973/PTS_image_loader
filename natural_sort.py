# -*- coding: utf-8 -*-
"""
Created on Mon Jun 26 10:59:26 2023

@author: Drew.Bennett
"""
#import re    
from PyQt5.QtCore import QSortFilterProxyModel

#sort list
##def naturalSort(l): 
  #  convert = lambda text: int(text) if text.isdigit() else text.lower()
 #   alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
  #  return sorted(l, key=alphanum_key)
    

#def lessThan(left,right):
  #  s = naturalSort([left,right])
   # return s[0] == left
            

#s:str ->[str]
#convert string to list, merging adjacent numbers
def mergeAdjacentDigits(s):
    if not s:
        return []
    r = ['']
    for c in s:
        if c.isdigit() and r[-1].isdigit():
            r[-1] += c
        else:
            r.append(c)
    return r[1::]

#print(mergeAdjacentDigits('ab23c'))
    


#true if left<right
def lt(left,right):
    s1 = mergeAdjacentDigits(left)
    s2 = mergeAdjacentDigits(right)
  #  print(s1,s2)
    for i,c1 in enumerate(s1):
        if i>=len(s2):
            return False
        c2 = s2[i]
        if c2!=c1:
            if c1.isdigit() and c2.isdigit():
                return int(c1)<int(c2)
            return c1<c2
   
    return len(s1)<len(s2)#longer string should be after shorter.
    
    
 

#print(lt('ab2','ab23'))
print(lt('3','16'))

            
#s = '2test1a5'
#print(toList(s))
#print(lessThan('1qgfd4.66','20'))
    
    
class naturalSortProxy(QSortFilterProxyModel):
    
    #QModelIndex,QModelIndex
    def lessThan(self,left,right):
        return lt(left.data(),right.data())
        
        