
from image_loader.image_model import load_layer

if __name__ == '__console__':
    from console.console import _console
    testFolder = os.path.dirname(_console.console.tabEditorWidget.currentWidget().path)

else:
    testFolder = os.path.dirname(__file__)
    
def testLoadLayer():
    #loadLayer(filePath,layerName,groups,createOverview=False,hide=False,expand=False)
    filePath = os.path.join(testFolder,'inputs','MFV2_01_ImageInt_000005.tif')
    layerName = 'test layer'
    groups = ['test group']
    load_layer.loadLayer(filePath,layerName,groups)


if __name__ == '__console__':
   testLoadLayer() 