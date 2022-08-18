import logging
import image_loader


logFile = os.path.join(os.path.dirname(image_loader.__file__),'log.txt')
#logFile = os.path.normpath(os.path.join(os.path.dirname(image_loader.__file__),'log.txt'))
#logFile = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\log.txt'

logging.basicConfig(filename=logFile,filemode='w',encoding='utf-8', level=logging.DEBUG, force=True)

logging.debug('test')
logging.info('Started')