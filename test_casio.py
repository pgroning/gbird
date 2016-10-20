import unittest
import sys,os

sys.path.append('../')
from casio import casio

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.testfile = "test/caxfiles_opt2.inp"
        self.cio = casio()
        self.cio.readinp(self.testfile)

    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_readinp(self):
        f = self.cio.data.inpfile
        self.assertEqual(f,self.testfile)
        nodes = self.cio.data.nodes
        self.assertTrue(type(nodes) is list, "nodes is not list")


if __name__ == '__main__':
    unittest.main()
