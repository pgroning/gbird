# python test/test_bundle.py
#
# Run single test:
# $ python test_bundle.py UnitTest.test_xyz
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
import copy
import numpy

sys.path.append('./')
from bundle import Bundle

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    #@unittest.skip("skip this test")
    def test_readinp(self):
        testfile = "test/topol/a10xm.inp"
        b = Bundle(testfile)
        self.assertTrue(b.data.fuetype == "A10XM" and 
                        type(b.data.nodes) is list,
                        "reading inp file failed")

    #@unittest.skip("skip this test")
    def test_readcax(self):
        testfile = "test/topol/a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        self.assertTrue(len(b.segments) == 5, "reading cax files failed")
    
    #@unittest.skip("skip this test")
    def test_readrun_all(self):
        testfile = "test/topol/opt2.inp"
        b = Bundle(testfile)
        b.readcax(content='Unfiltered')
        b1 = Bundle()
        b1.setup(b)
        b1.new_calc()
        self.assertEqual(18500, len(b.segments[2].statepoints), 
                        "read all failed")
        self.assertEqual(144, len(b1.segments[2].statepoints), 
                        "new calculation failed")

    #@unittest.skip("skip this test")
    def test_bundle_ave_enr(self):
        testfile = "test/topol/a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        for s in b.segments:
            s.ave_enr_calc()
        bundle_enr = b.ave_enr_calc()
        self.assertTrue(bundle_enr > 0, 
                        "bundle enrichment is invalid")

    #@unittest.skip("skip this test")
    def test_new_calc(self):
        testfile = "test/tosim/at11.inp"
        b = Bundle(testfile)
        b.readcax()
        b1 = Bundle()
        b1.setup(b)
        b1.new_calc(grid=False)
        self.assertTrue(len(b1.segments[4].statepoints) > 10, 
                        "new c3 calculation failed")
        b2 = Bundle()
        b2.setup(b)
        b2.new_calc(grid=False, voi=60, dep_max=20)
        self.assertEqual(b2.segments[2].data.voilist, [60],
                        "void failed to update correctly")
        self.assertEqual(b2.segments[1].statepoints[-1].voi,
                         60, "Void is incorrect")
        self.assertEqual(b2.segments[1].statepoints[-1].burnup,
                         20, "Max depletion is incorrect")
        b3 = Bundle()
        b3.setup(b)
        b3.new_calc(grid=False, dep_thres=20)
        self.assertTrue(len(b3.segments[3].statepoints) > 10, 
                        "new c3 calculation with depthres failed")
        b4 = Bundle()
        b4.setup(b)
        b4.new_calc(box_offset=0.2)
        self.assertEqual(b4.segments[1].data.box_offset, 0.2,
                         "box offset calculation failed")
        
    #@unittest.skip("skip test_new_calc_c4")
    def test_new_calc_c4(self):
        testfile = "test/topol/at11.inp"
        b = Bundle(testfile)
        b.readcax()
        b1 = Bundle()
        b1.setup(b)
        b1.new_calc(grid=True, model='c4e', voi=60)
        self.assertTrue(len(b1.segments[0].statepoints) > 10, 
                        "new c4 calculation failed")

    #@unittest.skip("skip this test")
    def test_new_ave_enr_calc(self):
        testfile = "test/tosim/a10b.inp"
        b = Bundle(testfile)
        b.readcax()
        b1 = Bundle()
        b1.setup(b)
        b1.new_calc(grid=False)
        for s in b1.segments:
            s.ave_enr_calc()
        bundle_enr = b1.ave_enr_calc()
        self.assertTrue(bundle_enr > 0, 
                        "bundle enrichment is invalid")

    #@unittest.skip("skip this test")
    def test_btf_calc_a10xm(self):
        testfile = "test/topol/a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        b.new_btf()
        self.assertTrue(hasattr(b.btf,"DOX") and 
                        type(b.btf.DOX) is numpy.ndarray,
                        "Btf calculation failed")
        self.assertFalse(numpy.isnan(b.btf.DOX).any(), "Btf is NaN")

    #@unittest.skip("skip this test")
    def test_btf_calc_a10b(self):
        testfile = "test/tosim/a10b.inp"
        b = Bundle(testfile)
        b.readcax()
        b.new_btf()
        self.assertTrue(hasattr(b.btf,"DOX") and 
                        type(b.btf.DOX) is numpy.ndarray,
                        "Btf calculation failed")
        self.assertFalse(numpy.isnan(b.btf.DOX).any(), "Btf is NaN")

    #@unittest.skip("skip this test")
    def test_new_btf_calc(self):
        testfile = "test/tosim/opt2.inp"
        b = Bundle(testfile)
        b.readcax()
        b.new_btf()
        b1 = Bundle()
        b1.setup(b)
        b1.new_calc(grid=False, voi=50, dep_thres=20)
        b1.new_btf()
        self.assertTrue(type(b.btf.DOX) is numpy.ndarray and 
                        type(b1.btf.DOX) is numpy.ndarray,
                        "new btf calculation failed")
        self.assertFalse(numpy.isnan(b1.btf.DOX).any(), "Btf is NaN")

    def test_bundle_setup(self):
        testfile = "test/tosim/opt2.inp"
        b = Bundle(testfile)
        b.readcax()
        b1 = Bundle(parent=b)
        
        self.assertTrue(numpy.array_equal(b.segments[1].data.LFU,
                                           b1.segments[1].data.LFU),
                         "LFU is not equal")
        
        LFU_new = copy.copy(b.segments[1].data.LFU)
        LFU_new[1, 1] += 1
        b1.segments[1].set_data(LFU=LFU_new)
        self.assertFalse(numpy.array_equal(b.segments[1].data.LFU,
                                           b1.segments[1].data.LFU),
                         "LFU is equal")
        
        
if __name__ == '__main__':
    unittest.main()
