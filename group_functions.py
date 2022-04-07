from qgis.core import QgsProject,QgsLayerTreeGroup
import json



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
                
                
                
    

#string representing groups to list.
#csv and database contain string.
def groupStringToList(text):
    try:
        return json.loads(text)
    except:
        print('Could not read groups from {t}. Reverting to empty list.'.format(t=text))
        return []



def listToGroupString(groups):
    return json.dumps(groups)



def test1():
    print(findOrMake('image_loader3'))
    groups=['a','b','c']
    print(getGroup(groups))



if __name__ == '__console__':
    test1()
    
    
    
