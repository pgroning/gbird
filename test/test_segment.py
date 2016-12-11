import unittest
#!/usr/bin/env python

import sys
import os
import mock
from mock import patch

sys.path.append('../')
from segment import Segment

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        #self.seg = Segment(self.testfile)
        #self.cas.readcax(self.testfile,0)
        #self.file_base_name = "test_file_base_name"

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        try: os.remove(self.file_base_name + ".inp")
        except: pass
        try: os.remove(self.file_base_name + ".out")
        except: pass
        try: os.remove(self.file_base_name + ".cax")
        except: pass


    def test_readcax_topol_atxm(self):
        testfile = "topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        segObj = Segment(testfile)
        #f = segObj.states[0].caxfile
        #self.assertEqual(f,self.testfile)
        Nstatepoints = len(segObj.states[0].statepoints)
        self.assertTrue(Nstatepoints >= 100, "Number of statepoinst is less than 100")

    @unittest.skip("Skip test_read_all")
    def test_readcax_topol_atxm_all(self):
        testfile = "topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        s = Segment(testfile, 'all')
        Nstatepoints = len(s.states[0].statepoints)
        self.assertTrue(Nstatepoints >= 500, "Number of statepoinst is less than 500")

    def test_readcax_tosim_at11(self):
        testfile = "tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        s = Segment(testfile)
        Nstatepoints = len(s.states[0].statepoints)
        self.assertTrue(Nstatepoints >= 100, "Number of statepoinst is less than 100")
        
    def test_get_voivec(self):
        testfile = "tosim/OPT2/12g30mid/e32OPT2-390-12g30mid-cas.cax"
        s = Segment(testfile)
        self.assertTrue(s.states[0].voivec, [0, 40, 80])

    def test_ave_enr(self):
        testfile = "topol/AT-B/08g30van/e27AT-B-386-08g30van-cas.cax"
        s = Segment(testfile)
        ave_enr = s.states[0].ave_enr
        self.assertTrue(ave_enr > 3.854 and ave_enr < 3.865)
        
    def test_boxbow(self):
        s = Segment()
        s.states[0].bwr = "BWR 11 1.300 13.580 0.14 0.762 0.753 1.27   * xyz"
        box_offset = 0.1
        bwr = s.boxbow(box_offset)
        res = "11 1.300 13.580 0.14 0.862 0.653 1.27"
        self.assertTrue(res in bwr)
        


        
        '''
    def test_writec3cai(self):
        self.seg.writec3cai(self.file_base_name)
        caifile = self.file_base_name + ".inp"
        with open(caifile) as f:  # check file content
            flines = f.read().splitlines()
        self.assertTrue(len(flines) >= 10, "file content is less than 10 lines")
    
    def test_runc3(self):
        self.seg.writec3cai(self.file_base_name)
        self.seg.runc3(self.file_base_name)
        caxfile = self.file_base_name + ".cax"
        self.assertTrue(os.path.isfile(caxfile), "cax file was not created")
        with open(caxfile) as f:  # check file content
            flines = f.read().splitlines()
        self.assertTrue(len(flines) >= 100,"file content is less than 100 lines")

    def test_readc3cax_ref(self):
        self.seg.writec3cai(self.file_base_name)
        self.seg.runc3(self.file_base_name, grid=False)
        self.seg.readc3cax(self.file_base_name,'refcalc')
        Nstatepoints = len(self.seg.states[0].refcalc.statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoints is less than 10")
    
    def test_readc3cax_add(self):
        LFU = self.seg.states[0].LFU
        self.seg.add_calc(LFU)
        self.seg.writec3cai(self.file_base_name)
        self.seg.runc3(self.file_base_name)
        self.seg.readc3cax(self.file_base_name)
        Nstatepoints = len(self.seg.states[1].statepoints)
        self.assertTrue(Nstatepoints >= 10, "Number of statepoints is less than 10")
   '''

if __name__ == '__main__':
    unittest.main()
