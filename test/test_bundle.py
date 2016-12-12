# python test/test_bundle.py
#

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os

#sys.path.append('../')
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
        
        nodes = b.data.nodes
        self.assertEqual(b.data.fuetype is "A10XM")
        #nodes = self.bo.data.nodes
        #self.assertTrue(type(nodes) is list, "nodes is not list")

    @unittest.skip("skip this test")
    def test_readcax(self):
        self.bo.readcax()
        #f = self.bo.info.caxfile

if __name__ == '__main__':
    unittest.main()
