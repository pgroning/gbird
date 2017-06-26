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


class Btf(object):
    """Calculate BTF values"""

    def __init__(self, bundle=None):
        self.bundle = bundle
        
    def lastindex(self, segment):
        """Iterate over burnup points"""
        
        statepoints = segment.statepoints
        previous_burnup = 0.0
        for idx, p in enumerate(statepoints):
            if p.burnup < previous_burnup:
                break
            previous_burnup = p.burnup
        return idx

    def intersect_points(self, segments):
        """Find intersection burnup points for segments"""
        
        nsegments = len(segments)
        idx = self.lastindex(segments[0])
        x = [segments[0].statepoints[i].burnup for i in range(idx)]
        
        for j in range(1, nsegments):
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

    def pow3d(self, segments, voi, burnup, zdim):
        """Construct a 3D pin power distribution for specific void and burnup.
        Use interpolation if necessary."""
                
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

        # Find the segments included in BTF calculations
        all_segments = self.bundle.segments
        nodes = self.bundle.data.btf_nodes
        segments = [s for i, s in enumerate(all_segments) if nodes[i]]

        x = self.intersect_points(segments)
        
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
            voi = 60
            rfact_fun = btf_a10b
        elif fuetype == "AT11":
            voi = 60
            rfact_fun = btf_at11
        else:
            print "Error: BTF is not implemented for this fuel type"
            return

        POW3_list = []
        for i, burnup in enumerate(x):
            POW3 = self.pow3d(segments, voi, burnup, zdim)
            POW3_list.append(POW3)
        
        n = min(len(POW3_list), 16)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        DOX_list = p.map(rfact_fun, POW3_list)
        p.close()
        p.join()
        
        for i, DOX in enumerate(DOX_list):
            self.DOX[i, :, :] = DOX

        self.burnpoints = np.array(x).astype(float)
        
        print "Done."


    if __name__ == '__main__':
        pass
