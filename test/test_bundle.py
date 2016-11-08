import unittest
import sys
import os

sys.path.append('../')
from bundle import Bundle

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.testfile = "caxfiles_opt2.inp"
        self.bo = Bundle()
        self.bo.readinp(self.testfile)

    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_readinp(self):
        f = self.bo.data.inpfile
        self.assertEqual(f,self.testfile)
        nodes = self.bo.data.nodes
        self.assertTrue(type(nodes) is list, "nodes is not list")

    def test_readcax(self):
        self.bo.readcax()
        #f = self.bo.info.caxfile

if __name__ == '__main__':
    unittest.main()
