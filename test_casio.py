import unittest
import sys,os

sys.path.append('../')
from casio import Casio

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.testfile = "../best/caxfiles_a10xm.inp"
        self.cio = Casio()


    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_readinp(self):
        self.cio.readinp(self.testfile)
        f = self.cio.data.get('inpfile')
        self.assertEqual(f,self.testfile)



if __name__ == '__main__':
    unittest.main()
