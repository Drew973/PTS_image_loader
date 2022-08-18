from image_loader.test import test_runs_model,test_image_model
from image_loader.test.get_db import getDb

from image_loader.widgets.runs_view import runsView


def test():
    db = getDb()
    im = test_image_model.testInit(db)
    rm = test_runs_model.testInit(db)
    test_image_model.testFromFolder(im)
    rm.select()
    print(im.rowCount())

    v = runsView()
    v.setModel(rm)
    v.show()
    return v


if __name__ == '__console__':
    v = test()