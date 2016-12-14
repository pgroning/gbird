# python test/test_segment.py
#
# Output status:
# OK (skipped=1)
# FAILED (failures=1, skipped=1)
# FAILED (errors=1, skipped=1)
#

import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os
import re
import numpy as np
import mock
from mock import patch

sys.path.append('./')
from segment import Segment

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        #self.seg = Segment(self.testfile)
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

    def test_readcax_topol_atxm(self):
        testfile = "test/topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        segObj = Segment(testfile)
        #f = segObj.states[0].caxfile
        #self.assertEqual(f,self.testfile)
        Nstatepoints = len(segObj.states[0].statepoints)
        self.assertTrue(Nstatepoints > 99, 
                        "Number of statepoinst is less than 100")

    @unittest.skip("test_readcax_topol_atxm_all")
    def test_readcax_topol_atxm_all(self):
        testfile = "test/topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        s = Segment(testfile, 'all')
        Nstatepoints = len(s.states[0].statepoints)
        self.assertTrue(Nstatepoints > 499, 
                        "Number of statepoinst is less than 500")

    def test_readcax_tosim_at11(self):
        testfile = "test/tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        s = Segment(testfile)
        Nstatepoints = len(s.states[0].statepoints)
        self.assertTrue(Nstatepoints > 99, 
                        "Number of statepoinst is less than 100")
        
    def test_get_voivec(self):
        testfile = "test/tosim/OPT2/12g30mid/e32OPT2-390-12g30mid-cas.cax"
        s = Segment(testfile)
        self.assertEqual(s.states[0].voivec, [0, 40, 80])
        
    def test_ave_enr(self):
        testfile = "test/topol/AT-B/08g30van/e27AT-B-386-08g30van-cas.cax"
        s = Segment(testfile)
        ave_enr = s.states[0].ave_enr
        self.assertTrue(ave_enr > 3.854 and ave_enr < 3.865)
        
    def test_boxbow(self):
        s = Segment()
        s.states[0].bwr = "BWR 11 1.300 13.580 0.14 0.762 0.753 1.27   * xyz"
        box_offset = 0.1
        bwr = s.boxbow(box_offset)
        result = "11 1.300 13.580 0.14 0.862 0.653 1.27"
        self.assertTrue(result in bwr)
    
    def test_add_state(self):
        testfile = "test/tosim/OPT2/12g30mid/e32OPT2-390-12g30mid-cas.cax"
        s = Segment(testfile)
        LFU = s.states[0].LFU
        FUE = s.states[0].FUE
        voi = 50
        s.add_state(LFU, FUE, voi)
        self.assertTrue((s.states[1].LFU == LFU).all())
    
    def test_writec3cai_at11(self):
        testfile = "test/tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        s = Segment(testfile)
        s.writec3cai(self.file_base_name)
        caifile = self.file_base_name + ".inp"
        # check file content
        with open(caifile) as f:
            flines = f.read().splitlines()
        rec = re.compile('^\s*BWR')
        iBWR = next(i for i, x in enumerate(flines) if rec.match(x))
        self.assertTrue('//' in flines[iBWR],
                        "double // is missing in BWR card for AT11 fuel")

    def test_runc3(self):
        testfile = "test/tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        s = Segment(testfile)
        s.writec3cai(self.file_base_name)
        s.runc3(self.file_base_name, grid=True)
        caxfile = self.file_base_name + ".cax"
        # check file content
        with open(caxfile) as f:
            flines = f.read().splitlines()
        self.assertTrue(len(flines) > 99,
                        "file content is less than 100 lines")

    @unittest.skip('skip test_runc4')
    def test_runc4(self):
        testfile = "test/topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        s = Segment(testfile)
        s.writec3cai(self.file_base_name, voi=60, depthres=20, box_offset=-0.1)
        s.runc4(self.file_base_name, grid=True)
        caxfile = self.file_base_name + ".cax"
        with open(caxfile) as f:
            flines = f.read().splitlines()
        self.assertTrue(len(flines) > 99,
                        "file content is less than 100 lines")
    
    def test_readc3cax(self):
        testfile = "test/tosim/OPT3/11g50bot/e33OPT3-383-11g50bot-cas.cax"
        s = Segment(testfile)
        s.writec3cai(self.file_base_name, voi=50, maxdep=20, box_offset=0.1)
        s.runc3(self.file_base_name, grid=False)
        s.readc3cax(self.file_base_name)
        Nstatepoints = len(s.states[0].statepoints)
        self.assertTrue(Nstatepoints > 19, 
                        "Number of statepoints is less than 20")
    
    def test_quickcalc(self):
        testfile = "test/tosim/OPT3/11g50bot/e33OPT3-383-11g50bot-cas.cax"
        s = Segment(testfile)
        s.quickcalc()
        Nstatepoints = len(s.states[1].statepoints)
        self.assertTrue(Nstatepoints > 99, 
                        "Number of statepoints is less than 100")



if __name__ == '__main__':
    unittest.main()
