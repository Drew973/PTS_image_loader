from qgis.core import QgsProject,QgsLayerTreeGroup



'''
functions for QgsLayerTreeGroup
'''

'''
returns new or existing QgsLayerTreeGroup with name child and parent
#child:str
#parent:QgsLayerTreeGroup or QgsLayerTree
'''
def findOrMake(child,parent=QgsProject.instance().layerTreeRoot()):
    for c in parent.children():
        if c.name() == child and isinstance(c,QgsLayerTreeGroup):
            return c
    
    return parent.addGroup(child)
    



def findGroup(child,parent=QgsProject.instance().layerTreeRoot()):
    for c in parent.children():
        if c.name() == child and isinstance(c,QgsLayerTreeGroup):
            return c



#finds or makes group from list of ancestors.
#groups: list of strings
def getGroup(groups):
    parent = QgsProject.instance().layerTreeRoot()
    for name in groups:
        parent = findOrMake(name,parent)
    return parent



#remove direct child group from parent
def removeChild(child,parent=QgsProject.instance().layerTreeRoot()):
        for c in parent.children():
            if c.name() == child and isinstance(c,QgsLayerTreeGroup):
                parent.removeChildNode(c)
                
                



import re
for layer in QgsProject.instance().layerTreeRoot().findLayers():
    print(layer.name())
    #{type}_{startFrame}_to_{endFrame}.vrt
    pattern = '(\D+)_(\d+)_to_(\d+)\.vrt'
    match = re.match(pattern,layer.name())
    if match:
        tp = match.group(1)
        start = match.group(2)
        end = match.group(3)
        print(tp,start,end)

def test1():
    print(findOrMake('image_loader3'))
    groups=['a','b','c']
    print(getGroup(groups))



if __name__ == '__console__':
    test1()
    
    
    
