from image_loader.widgets import details_view
from image_loader.models.image_model_spatialite.image_model import imageModel


dbFile = r'C:\Users\drew.bennett\Documents\image_loader\test.sqlite'

m = imageModel(parent=None,db=QSqlDatabase.database('image_loader'))

v = details_view.detailsView()
v.setModel(m)
v.show()


#v = QTableView()
#v.setModel(m)
#v.show()