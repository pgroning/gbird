# python test/test_bundle.py
#

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os

sys.path.append('./')
from bundle import Bundle

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        #self.testfile = "caxfiles_opt2.inp"
        #self.bo = Bundle()
        #self.bo.readinp(self.testfile)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    def test_readinp(self):
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        self.assertTrue(b.data.fuetype == "A10XM" and 
                        type(b.data.nodes) is list,
                        "reading inp file failed")

    #@unittest.skip("skip this test")
    def test_readcax(self):
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        self.assertTrue(len(b.cases) > 0, "reading cax files failed")
        
    def test_bundle_ave_enr(self):
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        b.ave_enr()
        self.assertTrue(b.states[0].ave_enr > 0, 
                        "bundle enrichment is invalid")
    #@unittest.skip("skip this test")
    def test_new_calc(self):
        testfile = "test/tosim/bundle_at11.inp"
        b = Bundle(testfile)
        b.readcax()
        b.new_calc(grid=True)
        self.assertTrue(len(b.cases[0].states[1].statepoints) > 10, 
                        "new calculation failed")
    #@unittest.skip("skip this test")
    def test_new_ave_enr_calc(self):
        testfile = "test/tosim/bundle_at11.inp"
        b = Bundle(testfile)
        b.readcax()
        b.new_calc(grid=True)
        b.ave_enr()
        self.assertTrue(b.states[1].ave_enr > 0, 
                        "bundle enrichment is invalid")

if __name__ == '__main__':
    unittest.main()
