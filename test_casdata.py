import unittest
#!/usr/bin/env python

import sys
import os

sys.path.append('../')
from casdata import casdata

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.testfile = "test/topol/OPT2/10g40bot/e29OPT2-382-10g40bot-cas.cax"
        #self.testfile = "test/topol/OPT2_2/12g30bot/e32OPT2-382-12g30bot-cas.cax"
     
        #self.testfile = "../best/cax/ATXM/10g35dom/e28ATXM-385-10g35dom-cas.cax"
        #self.testfile = "../best/cax/A10XM/10g35dom/e28ATXM-385-10g35dom-cas.cax"
        self.cas = casdata(self.testfile)
        #self.cas.readcax(self.testfile,0)


    def tearDown(self):
        unittest.TestCase.tearDown(self)


    def test_readcax(self):
        f = self.cas.data[0].info.caxfile
        self.assertEqual(f,self.testfile)
        Nstatepoints = len(self.cas.data[0].statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoinst is less than 10")
        
    '''
    @unittest.skip("Skip test_read_all")
    def test_read_all(self):
        self.cas.readcax(self.testfile,'all')
        f = self.cas.data[0]['info'].get('caxfile')
        self.assertEqual(f,self.testfile)
        Nstatepoints = len(self.cas.data[0].get('statepoints'))
        self.assertTrue(Nstatepoints > 0)
    '''
    
    def test_ave_enr(self):
        self.cas.ave_enr()
        ave_enr = self.cas.data[0].info.ave_enr
        self.assertTrue(ave_enr > 0)
    
    def test_writec3cai(self):
        filebasename = self.cas.writec3cai()
        self.assertTrue(type(filebasename) == str, "filebasename is not a string")
        os.remove(filebasename + ".inp")
    
    def test_runc3(self):
        filebasename = self.cas.writec3cai()
        self.cas.runc3(filebasename)
        caxfile = filebasename + ".cax"
        self.assertTrue(os.path.isfile(caxfile), "cax file was not created")
        # check file content
        with open(caxfile) as f:
            flines = f.read().splitlines()
        print len(flines)
        self.assertTrue(len(flines) > 100,"file content is not complete")
        try: os.remove(caxfile)
        except: pass

    def test_readc3cax_ref(self):
        filebasename = self.cas.writec3cai()
        self.cas.runc3(filebasename)
        self.cas.readc3cax(filebasename,'refcalc')
        Nstatepoints = len(self.cas.data[0].refcalc.statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoints is less than 10")
    
    def test_readc3cax_add(self):
        filebasename = self.cas.writec3cai()
        self.cas.runc3(filebasename)
        self.cas.add_calc()
        self.cas.readc3cax(filebasename)
        Nstatepoints = len(self.cas.data[1].statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoints is less than 10")
    

if __name__ == '__main__':
    unittest.main()
