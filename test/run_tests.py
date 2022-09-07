import unittest

suite = unittest.TestSuite()

from image_loader.models.runs_model_spatialite import test_runs_model
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_runs_model))

from image_loader.models.details import test_image_details
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_image_details))

from image_loader.models.image_model_spatialite import test_image_model
suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(test_image_model))


r = unittest.TextTestRunner(verbosity=2).run(suite)
#if len(r.errors)>0:
  #  print('failed')
    
    