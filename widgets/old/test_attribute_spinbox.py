from image_loader.widgets import attribute_spin_box
from qgis.core import QgsProject


if __name__ == '__console__':
    layer = QgsProject.instance().mapLayersByName('MFV2_01 Spatial Frame Data')[0]
    
    s = attribute_spin_box.attributeSpinBox()
    s.setLayer(layer)
    s.setField('sectionID')
    
    s.show()