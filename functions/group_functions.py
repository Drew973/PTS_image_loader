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
                
                




def test1():
    print(findOrMake('image_loader3'))
    groups=['a','b','c']
    print(getGroup(groups))



if __name__ == '__console__':
    test1()
    
    
    
