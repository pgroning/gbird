import unittest
import sys,os

sys.path.append('../')
from casio import Casio

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.testfile = "test/caxfiles_atxm.inp"
        self.cio = Casio()
        self.cio.readinp(self.testfile)

    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_readinp(self):
        f = self.cio.data.get('inpfile')
        self.assertEqual(f,self.testfile)
        nodes = self.cio.data.get('nodes')
        self.assertTrue(type(nodes) is list, "nodes is not list")


if __name__ == '__main__':
    unittest.main()
