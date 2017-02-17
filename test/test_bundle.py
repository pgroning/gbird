# python test/test_bundle.py
#
# Run single test:
# $ python test_bundle.py UnitTest.test_append_state
# Run all tests in directory test:
# $ python -m unittest discover test
#

from IPython.core.debugger import Tracer
import sys
if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest
import os
import numpy

sys.path.append('./')
from bundle import Bundle

class UnitTest(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        #self.testfile = "caxfiles_opt2.inp"
        #self.bo = Bundle()
        #self.bo.readinp(self.testfile)

    def tearDown(self):
        unittest.TestCase.tearDown(self)

    #@unittest.skip("skip this test")
    def test_readinp(self):
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        self.assertTrue(b.data.fuetype == "A10XM" and 
                        type(b.data.nodes) is list,
                        "reading inp file failed")

    #@unittest.skip("skip this test")
    def test_readcax(self):
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        self.assertTrue(len(b.states[0].segments) == 5, "reading cax files failed")
    
    @unittest.skip("skip this test")
    def test_readrun_all(self):
        testfile = 'test/topol/bundle_opt2.inp'
        b = Bundle(testfile)
        b.readcax(read_all=True)
        b.append_state()
        b.new_calc()
        self.assertEqual(18500, len(b.states[0].segments[2].statepoints), 
                        "read all failed")
        self.assertEqual(119, len(b.states[1].segments[2].statepoints), 
                        "new calculation failed")

    #@unittest.skip("skip this test")
    def test_bundle_ave_enr(self):
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        b.ave_enr_calc()
        self.assertTrue(b.states[0].ave_enr > 0, 
                        "bundle enrichment is invalid")

    #@unittest.skip("skip this test")
    def test_new_calc(self):
        #testfile = "test/tosim/bundle_at11.inp"
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        b.append_state()
        b.new_calc(grid=False)
        self.assertTrue(len(b.states[1].segments[4].statepoints) > 10, 
                        "new c3 calculation failed")
        b.append_state()
        b.new_calc(grid=False, voi=60, maxdep=20)
        self.assertEqual(b.states[2].segments[2].data.voilist, [60],
                        "void failed to update correctly")
        self.assertEqual(b.states[2].segments[1].statepoints[-1].voi,
                         60, "Void is incorrect")
        self.assertEqual(b.states[2].segments[1].statepoints[-1].burnup,
                         20, "Max depletion is incorrect")
        b.append_state()
        b.new_calc(grid=False, depthres=20)
        self.assertTrue(len(b.states[3].segments[3].statepoints) > 10, 
                        "new c3 calculation with depthres failed")
        b.append_state()
        b.new_calc(box_offset=0.2)
        self.assertEqual(b.states[4].segments[1].data.box_offset, 0.2,
                        "box offset calculation failed")
        
    #@unittest.skip("skip test_new_calc_c4")
    def test_new_calc_c4(self):
        #testfile = "test/tosim/bundle_at11.inp"
        testfile = "test/topol/bundle_a10xm.inp"
        b = Bundle(testfile)
        b.readcax()
        b.append_state()
        b.new_calc(grid=True, model='c4', voi=60)
        self.assertTrue(len(b.states[1].segments[0].statepoints) > 10, 
                        "new c4 calculation failed")

    #@unittest.skip("skip this test")
    def test_new_ave_enr_calc(self):
        #testfile = "test/tosim/bundle_at11.inp"
        testfile = 'test/tosim/bundle_a10b.inp'
        b = Bundle(testfile)
        b.readcax()
        b.append_state()
        b.new_calc(grid=True)
        b.ave_enr_calc()
        self.assertTrue(b.states[1].ave_enr > 0, 
                        "bundle enrichment is invalid")

    #@unittest.skip("skip this test")
    def test_btf_calc_a10xm(self):
        testfile = 'test/topol/bundle_a10xm.inp'
        b = Bundle(testfile)
        b.readcax()
        b.new_btf()
        self.assertTrue(hasattr(b.states[0].btf,"DOX") and 
                        type(b.states[0].btf.DOX) is numpy.ndarray,
                        "Btf calculation failed")
        self.assertFalse(numpy.isnan(b.states[0].btf.DOX).any(), "Btf is NaN")

    #@unittest.skip("skip this test")
    def test_btf_calc_a10b(self):
        testfile = 'test/tosim/bundle_a10b.inp'
        b = Bundle(testfile)
        b.readcax()
        b.new_btf()
        self.assertTrue(hasattr(b.states[0].btf,"DOX") and 
                        type(b.states[0].btf.DOX) is numpy.ndarray,
                        "Btf calculation failed")
        self.assertFalse(numpy.isnan(b.states[0].btf.DOX).any(), "Btf is NaN")

    #@unittest.skip("skip this test")
    def test_new_btf_calc(self):
        testfile = 'test/tosim/bundle_opt2.inp'
        b = Bundle(testfile)
        b.readcax()
        b.new_btf()
        b.append_state()
        b.new_calc(grid=False, voi=50, depthres=20)
        b.new_btf()
        self.assertTrue(type(b.states[0].btf.DOX) is numpy.ndarray and 
                        type(b.states[1].btf.DOX) is numpy.ndarray,
                        "new btf calculation failed")
        self.assertFalse(numpy.isnan(b.states[1].btf.DOX).any(), "Btf is NaN")

    def test_append_state(self):
        testfile = 'test/tosim/bundle_opt2.inp'
        b = Bundle(testfile)
        b.readcax()
        b.append_state()
        self.assertEqual(b.states[0].segments[1].data.LFU.any(),
                         b.states[1].segments[1].data.LFU.any(),
                         "LFU is not equal")
        LFU_new = numpy.zeros((11, 11))
        b.states[1].segments[1].set_data(LFU=LFU_new)
        self.assertNotEqual(b.states[0].segments[1].data.LFU.any(),
                         b.states[1].segments[1].data.LFU.any(),
                         "LFU is equal")
        
        
if __name__ == '__main__':
    unittest.main()
