# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 13:09:42 2025

@author: Drew.Bennett
"""


import os
from image_loader import process_runner , test
from PyQt5.QtCore import QProcess , Qt
from PyQt5.QtWidgets import QProgressDialog


N = 100
waitScript = os.path.join(test.testFolder,'wait5.bat')
#waitScript = os.path.join(test.testFolder,'wait5.py')

runner = process_runner.processRunner()



processes = []
for i in range(N):
    p = QProcess()
    p.setProgram(waitScript)
  #  p.setProgram('python')
 #   p.setArguments([waitScript])    
    processes.append(p)

d = QProgressDialog()
d.setRange(0,N)
d.canceled.connect(runner.cancel)
runner.progressChanged.connect(d.setValue)
d.setWindowModality(Qt.WindowModal)
#print(processes)
d.show()
runner.beginProcesses(processes)
#runner.waitForFinished()
print('ok')
