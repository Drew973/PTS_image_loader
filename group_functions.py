from qgis.core import QgsProject
import json

#QgsLayerTreeNode
#returns QgsLayerTreeNode named name or None
#does not search recursively
def findChild(node,name):
    
    for c in node.children():
        if c.name()==name:
            return c
   # print('findChild')
   # g = node.findGroups()
   # print(g)
    
    #if g:
    #    return g[0]


def findGroup(name,parent=QgsProject.instance().layerTreeRoot()):
    for g in parent.findGroups(recursive=False):
        if g.name()==name:
            return g   
    


#list of strings from root.
#returns group, makes if doesn't exist
def getGroup(groups):
    lastGroup = QgsProject.instance().layerTreeRoot()
    for g in groups:
        existingGroup = findGroup(g,lastGroup) 
        if existingGroup is None:
            lastGroup = lastGroup.addGroup(g)
        else:
            lastGroup = existingGroup
   
    return lastGroup


#remove direct child nodes named name
def removeChild(name,node=QgsProject.instance().layerTreeRoot()):
    for g in node.findGroups(recursive=False):
        if g.name()==name:
            node.removeChildNode(g)


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


if __name__ == '__console__':
    root = QgsProject.instance().layerTreeRoot()
    groups = ['a','b','c','d']
    getGroup(groups)