from qgis.gui import QgsRubberBand
from qgis.utils import iface
from qgis.core import QgsPointXY

b = QgsRubberBand(iface.mapCanvas())
b.setWidth(5)

b.setColor(QColor('red'))
b.setIcon(QgsRubberBand.ICON_CROSS)
b.setIconSize(5)

points = [QgsPointXY(354456.951,321915.668),
QgsPointXY(354464.122,321914.278)]

for p in points:
    b.addPoint(p)
    
b.show()
#iface.mapCanvas().scene().removeItem(b)