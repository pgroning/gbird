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
        f = self.bo.info.inpfile
        self.assertEqual(f,self.testfile)
        nodes = self.bo.info.nodes
        self.assertTrue(type(nodes) is list, "nodes is not list")

    def test_readcax(self):
        pass

if __name__ == '__main__':
    unittest.main()
