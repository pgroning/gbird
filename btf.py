#!/usr/bin/python

# Profiler:
# import cProfile
# cProfile.run('b.rfact()')

from IPython.core.debugger import Tracer
from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt

import sys
import time
import numpy as np
from multiprocessing import Pool

from lib import btf_a10b, btf_a10xm, btf_at11, btf_opt2, btf_opt3

#from btf_opt2 import btf_opt2
#from btf_opt3 import btf_opt3
#from btf_a10xm import btf_a10xm
#from btf_a10b import btf_a10b
#from btf_at11 import btf_at11

# sys.path.append('lib/')
# import libADDC


class Btf(object):
    """Calculate BTF values"""

    def __init__(self, bundle=None):
        self.bundle = bundle
        # self.rfact()
        # self.pow3d(voi=50,burnup=0)

    def lastindex(self, segment):
        """Iterate over burnup points"""
        
        #statepoints = self.bundle.segments[case_id].statepoints
        statepoints = segment.statepoints
        burnup_old = 0.0
        for idx, p in enumerate(statepoints):
            if p.burnup < burnup_old:
                break
            burnup_old = p.burnup
        return idx

    def intersect_points(self, segments):
        """Find intersection burnup points for segments"""
        
        #segments = self.bundle.segments
        nsegments = len(segments)
        #idx = self.lastindex(0)
        idx = self.lastindex(segments[0])
        x = [segments[0].statepoints[i].burnup for i in range(idx)]
        
        for j in range(1, nsegments):
            #idx = self.lastindex(j)
            idx = self.lastindex(segments[j])
            x2 = ([segments[j].statepoints[i].burnup
                   for i in range(idx)])
            x = [val for val in x if val in x2]
        return x

    def union_points(self):
        """Find union burnup points for segments"""

        segments = self.bundle.segments
        nsegments = len(segments)
        idx = self.lastindex(0)

        xlist = []
        for j, seg in enumerate(segments):
            idx = self.lastindex(j)
            x = [seg.statepoints[i].burnup for i in range(idx)]
            xlist.append(x)
        #qtrace()

    def pow3d(self, segments, voi, burnup, zdim):
        """Construct a 3D pin power distribution for specific void and burnup.
        Use interpolation if necessary."""
        
        #all_segments = self.bundle.segments
        ##btf_zones = self.bundle.data.btf_zones
        ##segments = [s for i, s in enumerate(all_segments) if btf_zones[i]]
        #nodes = self.bundle.data.btf_nodes
        #segments = [s for i, s in enumerate(all_segments) if nodes[i]]
        
        nsegments = len(segments)
        npst = segments[0].data.npst
        POW = np.zeros((nsegments, npst, npst))
        
        # determine which voids are present in data
        for i in range(nsegments):
            voilist = segments[i].data.voilist
            if int(voi) in voilist:
                i1 = segments[i].findpoint(burnup=burnup, vhi=voi, voi=voi)
                POW[i, :, :] = segments[i].statepoints[i1].POW
            else:
                voi1 = max([x for x in voilist if x < voi])
                i1 = segments[i].findpoint(burnup=burnup, vhi=voi1, voi=voi1)
                voi2 = min([x for x in voilist if x > voi])
                i2 = segments[i].findpoint(burnup=burnup, vhi=voi2, voi=voi2)
                P1 = segments[i].statepoints[i1].POW
                P2 = segments[i].statepoints[i2].POW
                POW[i, :, :] = self.bundle.interp2(P1, P2, voi1, voi2, voi)
        
        nodes = self.bundle.data.btf_nodes
        POW3 = self.bundle.pow3(POW, nodes, zdim)
        return POW3

    def calc_btf(self):
        """Calculating BTF"""
        print "Calculating BTF..."

        #tic = time.time()

        # Find the segments included in BTF calculations
        all_segments = self.bundle.segments
        nodes = self.bundle.data.btf_nodes
        segments = [s for i, s in enumerate(all_segments) if nodes[i]]

        x = self.intersect_points(segments)
        #x = self.union_points()
        
        #npst = self.bundle.segments[0].data.npst
        npst = segments[0].data.npst
        self.DOX = np.zeros((len(x), npst, npst))
        
        fuetype = self.bundle.data.fuetype
        zdim = 25  # default number of nodes
        if fuetype == "OPT2":
            voi = 50
            rfact_fun = btf_opt2
        elif fuetype == "OPT3":
            zdim = 100
            voi = 50
            rfact_fun = btf_opt3
        elif fuetype == "A10XM":
            voi = 60
            rfact_fun = btf_a10xm
        elif fuetype == "A10B":
            zdim = 25 
            voi = 60
            rfact_fun = btf_a10b
        elif fuetype == "AT11":
            voi = 60
            rfact_fun = btf_at11
        else:
            print "Error: BTF is not implemented for this fuel type"
            return

        #tic = time.time()
        POW3_list = []
        for i, burnup in enumerate(x):
            POW3 = self.pow3d(segments, voi, burnup, zdim)
            POW3_list.append(POW3)
            #self.DOX[i, :, :] = rfact_fun(POW3)
            ## self.DOX[i, :, :] = self.rfact(POW3)
        
        n = min(len(POW3_list), 16)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        DOX_list = p.map(rfact_fun, POW3_list)
        p.close()
        p.join()
        
        for i, DOX in enumerate(DOX_list):
            self.DOX[i, :, :] = DOX

        self.burnpoints = np.array(x).astype(float)
        
        print "Done."
        #print "Done in "+str(time.time()-tic)+" seconds."

    #def rfact(self, POW3):
    #    fuetype = self.bundle.data.fuetype
    #    if fuetype == 'OPT2':
    #        # print "Calculating BTF for OPT2"
    #        DOX = btf_opt2(POW3)
    #    elif fuetype == 'A10XM':
    #        # print "Calculating BTF for ATXM"
    #        DOX = btf_a10xm(POW3)
    #    elif fuetype == 'A10B':
    #        DOX = btf_a10b(POW3)
    #    return DOX


    if __name__ == '__main__':
        import bundle
        import btf
        inpfile = sys.argv[1]
        bundle = bundle.Bundle(inpfile)
        bundle.readcax()
        b = btf.Btf(bundle)
        b.calc_btf()
