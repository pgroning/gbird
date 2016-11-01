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
        self.file_base_name = "test_file_base_name"

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        try: os.remove(self.file_base_name + ".inp")
        except: pass
        try: os.remove(self.file_base_name + ".out")
        except: pass
        try: os.remove(self.file_base_name + ".cax")
        except: pass


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
        self.cas.writec3cai(self.file_base_name)
        caifile = self.file_base_name + ".inp"
        with open(caifile) as f:  # check file content
            flines = f.read().splitlines()
        self.assertTrue(len(flines) >= 10, "file content is less than 10 lines")
    
    def test_runc3(self):
        self.cas.writec3cai(self.file_base_name)
        self.cas.runc3(self.file_base_name)
        caxfile = self.file_base_name + ".cax"
        self.assertTrue(os.path.isfile(caxfile), "cax file was not created")
        with open(caxfile) as f:  # check file content
            flines = f.read().splitlines()
        self.assertTrue(len(flines) >= 100,"file content is less than 100 lines")

    def test_readc3cax_ref(self):
        self.cas.writec3cai(self.file_base_name)
        self.cas.runc3(self.file_base_name)
        self.cas.readc3cax(self.file_base_name,'refcalc')
        Nstatepoints = len(self.cas.data[0].refcalc.statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoints is less than 10")
    
    def test_readc3cax_add(self):
        self.cas.writec3cai(self.file_base_name)
        self.cas.runc3(self.file_base_name)
        self.cas.add_calc()
        self.cas.readc3cax(self.file_base_name)
        Nstatepoints = len(self.cas.data[1].statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoints is less than 10")
    

if __name__ == '__main__':
    unittest.main()
