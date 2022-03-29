from zipfile import ZipFile
import os


#copys everything except .git ,__pycache__ folders and .pyc extention in folder to zip file zip_name
#need filenames 1st otherwise looping through zip?
def package(folder,zipPath=None,excludeExt=['.pyc','.zip','.gitignore'],excludeDir=['.git','test','tests']):
    
    print('package(%s,%s,%s)'%(str(folder),str(zipPath),str(excludeExt)))
    if not zipPath:
        zipPath =os.path.join(folder,os.path.basename(folder)+'.zip')

    print('zip file:',zipPath)
    with ZipFile(zipPath, 'w') as z:
      
        for folderName, subfolders, filenames in os.walk(folder):
            for filename in filenames:
                toZip = os.path.join(folderName,filename)
                if checkExt(toZip,excludeExt) and checkDir(toZip,excludeDir):
                    arcPath = os.path.join(os.path.basename(folder),os.path.relpath(toZip,folder))
                    z.write(toZip,arcPath)
                    #2nd arg archname is path within archive
        

#returns false if extention in exclude
def checkExt(fileName,exclude=[]):
    ext = os.path.splitext(fileName)[1]
    if ext in exclude:
        return False
    return True
    
#returns False if any element of exclude contained in dir name
def checkDir(fileName,exclude=[]):
    folder = os.path.dirname(fileName)
    parents = [p for p in parentNames(os.path.dirname(fileName))]
    for ex in exclude:
        if ex in parents:
            return False
    return True
    
    
def parentNames(dir,maxCount=1000):
    remainder = dir
    counter = 0
    while remainder!=os.path.dirname(remainder) and counter<maxCount:
        yield os.path.basename(remainder)
        remainder = os.path.dirname(remainder)
        counter+=1


if __name__ == "__main__":
    package(os.getcwd())

if __name__ == '__console__':
    from console.console import _console    
    script_path = _console.console.tabEditorWidget.currentWidget().path
    package(folder=os.path.dirname(script_path))
