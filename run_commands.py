# -*- coding: utf-8 -*-
"""
Created on Fri May 19 07:57:15 2023

@author: Drew.Bennett
"""



from PyQt5.QtCore import QProcess


'''
run iterable of commands as subprocess in paralell.
update progress bar and allow cancelling
todo: use [(program,[args])]

run batchsize at time. Too high causes os error whilst too low results in unnecessary waiting.

'''
def runCommands(commands,progress,batchSize=20,shell=False):
    
    #increase progress by 1
    def commandFinished(status):
        progress.setValue(progress.value()+1)
    
    progress.setRange(0,len(commands))
    progress.setValue(0)
    split = [s for s in splitList(commands,batchSize)]#.

    for s in split:
        processes = []
        for c in s:
            proc = QProcess()
            processes.append(proc)
            proc.finished.connect(commandFinished)
            proc.start(c)#obsolete. should change this 
        
        for p in processes:
            if progress.wasCanceled():
                p.close()
            p.waitForFinished()
        
        if progress.wasCanceled():
            break


#split Iterible into lists up to maxSize long
def splitList(lis, maxSize = 10):
    c = []
    for d in lis:
        if len(c) >= maxSize:
            yield c
            c = []
        c.append(d)
    if len(c)>0:
        yield c
        
        
        
def testSplitList():
    test = [i for i in range(0,53)]
    print(test)
    for d in splitList(test):
        print(d)
#testSplitList()  