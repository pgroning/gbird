# python test/test_segment.py
#
# Run single test:
# $ python test_segment.py UnitTest.test_xyz
# Run all tests in directory test:
# $ python -m unittest discover test
#
# Output status:
# OK (skipped=1)
# FAILED (failures=1, skipped=1)
# FAILED (errors=1, skipped=1)
#

from IPython.core.debugger import Tracer
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os
import re
import numpy as np
import shutil
import mock
from mock import patch

sys.path.append('./')
from segment import Segment

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.file_base_name = "test_file_base_name"

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        try: os.remove(self.file_base_name + ".inp")
        except: pass
        try: os.remove(self.file_base_name + ".out")
        except: pass
        try: os.remove(self.file_base_name + ".cax")
        except: pass
        try: os.remove(self.file_base_name + ".log")
        except: pass

    def test_readcax_topol_atxm(self):
        testfile = "test/topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        s = Segment(testfile)
        Nstatepoints = len(s.statepoints)
        self.assertEqual(153, Nstatepoints, 
                         "Number of state points is incorrect")
        self.assertListEqual([40, 0, 80], s.data.voilist,
                         "void list is incorrect")

    #@unittest.skip("test_readcax_topol_atxm_all")
    def test_readcax_topol_atxm_all(self):
        testfile = "test/topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        s = Segment(testfile, content='Unfiltered')
        Nstatepoints = len(s.statepoints)
        self.assertEqual(19482, Nstatepoints,
                        "Number of state points is incorrect")

    def test_readcax_topol_opt3_small(self):  # read small cax file
        testfile = "test/topol/OPT3_small/e31OPT3-220-00g00eb-seg.cax"
        s = Segment(testfile)
        Nstatepoints = len(s.statepoints)
        self.assertEqual(84, Nstatepoints, 
                         "Number of state points is incorrect")

    #@unittest.skip("skip this test")
    def test_readcax_tosim_at11(self):
        testfile = "test/tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        s = Segment(testfile)
        Nstatepoints = len(s.statepoints)
        self.assertEqual(145, Nstatepoints,
                        "Number of state points is incorrect")
        self.assertEqual(s.data.voilist, [0, 40, 80])

    #@unittest.skip("test_get_voilist")
    def test_get_voilist(self):
        testfile = "test/tosim/OPT2/12g30mid/e32OPT2-390-12g30mid-cas.cax"
        s = Segment(testfile)
        self.assertEqual(s.data.voilist, [0, 40, 80])
    
    #@unittest.skip("skip this test")
    def test_ave_enr(self):
        testfile = "test/topol/AT-B/08g30van/e27AT-B-386-08g30van-cas.cax"
        s = Segment()
        s.readcax(testfile)
        s.ave_enr_calc()
        ave_enr = s.ave_enr
        #ave_enr = s.data.ave_enr
        self.assertTrue(ave_enr > 3.854 and ave_enr < 3.865)
    
    #@unittest.skip("skip this test")
    def test_boxbow(self):
        s = Segment()
        s.data.bwr = "BWR 11 1.300 13.580 0.14 0.762 0.753 1.27   * xyz"
        box_offset = 0.1
        bwr = s._Segment__boxbow(box_offset)  # reaching "private" method
        result = "11 1.300 13.580 0.14 0.862 0.653 1.27"
        self.assertTrue(result in bwr)
        
    #@unittest.skip("test_writec3cai_at11")
    def test_writecai_c3_at11(self):
        testfile = "test/tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        #testfile = "test/tosim/OPT2/12g30mid/e32OPT2-390-12g30mid-cas.cax"
        s = Segment(testfile)
        s.writecai(self.file_base_name)
        caifile = self.file_base_name + ".inp"
        
        # check file content
        with open(caifile) as f:
            flines = f.read().splitlines()
        rec = re.compile('^\s*BWR')
        iBWR = next(i for i, x in enumerate(flines) if rec.match(x))
        self.assertTrue('//' in flines[iBWR],
                        "double // is missing in BWR card for AT11 fuel")
    
    #@unittest.skip("skip this test")
    def test_runc3(self):
        # testfile = "test/tosim/AT11/14g35top/exxAT11-384-14g35top-cas.cax"
        # s = Segment(testfile)
        # s.writec3cai(self.file_base_name)
        # s.runc3(self.file_base_name, grid=True)
        s = Segment()
        caxfile = self.file_base_name + ".cax"
        inpfile = self.file_base_name + ".inp"
        shutil.copy2("test/files/e33OPT3-383-11g50bot-cas_test_c3.inp", inpfile)
        s.runc3(self.file_base_name, grid=False)
        # check file content
        with open(caxfile) as f:
            flines = f.read().splitlines()
        self.assertEqual(13200, len(flines),
                        "number of lines in file is wrong")

    #@unittest.skip('skip test_runc4')
    def test_runc4(self):
        testfile = "test/topol/ATXM/10g40dom/e28ATXM-385-10g40dom-cas.cax"
        s = Segment(testfile)
        s.writecai(self.file_base_name, voi=60, dep_thres=20, box_offset=-0.1,
                   model="c4e")
        s.runc4("./" + self.file_base_name, grid=True)
        caxfile = self.file_base_name + ".cax"
        with open(caxfile) as f:
            flines = f.read().splitlines()
        self.assertTrue(len(flines) > 200,
                        "file content is less than 200 lines")
    
    #@unittest.skip("skip this test")
    def test_readc3cax(self):
        s = Segment()
        s.readc3cax("test/files/e33OPT3-383-11g50bot-cas_test_c3")
        Nstatepoints = len(s.statepoints)
        self.assertEqual(147, Nstatepoints,
                        "Number of statepoints is less than 20")

    #@unittest.skip("skip this test")
    def test_quickcalc(self):
        testfile = "test/tosim/OPT3/11g50bot/e33OPT3-383-11g50bot-cas.cax"
        s = Segment(testfile)
        s.cas_calc(grid=False)
        Nstatepoints = len(s.statepoints)
        self.assertEqual(147, Nstatepoints, 
                        "Number of state points is incorrect")


if __name__ == '__main__':
    unittest.main()
