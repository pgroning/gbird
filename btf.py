#!/usr/bin/python

# Profiler:
# import cProfile
# cProfile.run('b.rfact()')

from IPython.core.debugger import Tracer

import sys
import time
import numpy as np

from btf_opt2 import btf_opt2
# from lib.btf_opt2 import btf_opt2
from btf_a10xm import btf_a10xm
from btf_a10b import btf_a10b

# sys.path.append('lib/')
# import libADDC


class Btf(object):
    """Calculate BTF values"""

    def __init__(self, bundle=None):
        self.bundle = bundle
        # self.rfact()
        # self.pow3d(voi=50,burnup=0)

    def lastindex(self, case_id):
        """Iterate over burnup points"""
        
        statepoints = self.bundle.states[-1].segments[case_id].statepoints
        burnup_old = 0.0
        for idx, p in enumerate(statepoints):
            if p.burnup < burnup_old:
                break
            burnup_old = p.burnup
        return idx

    def intersect_points(self):
        """Find intersection burnup points for all cases"""
        
        segments = self.bundle.states[-1].segments
        nsegments = len(segments)
        idx = self.lastindex(0)
        
        x = [segments[0].statepoints[i].burnup for i in range(idx)]
        for j in range(1, nsegments):
            idx = self.lastindex(j)
            x2 = ([segments[j].statepoints[i].burnup
                   for i in range(idx)])
            x = [val for val in x if val in x2]
        return x

    def pow3d(self, voi, burnup):
        """Construct a 3D pin power distribution for specific void and burnup.
        Use interpolation if necessary."""
        
        all_segments = self.bundle.states[-1].segments
        #all_segments = self.bundle.cases

        btf_zones = self.bundle.data.btf_zones
        segments = [s for i, s in enumerate(all_segments) if btf_zones[i]]
        nodes = self.bundle.data.btf_nodes
        
        nsegments = len(segments)
        npst = segments[0].data.npst
        POW = np.zeros((nsegments, npst, npst))
        
        # determine which voids are present in data
        for i in range(nsegments):
            voivec = segments[i].data.voivec
            
            if int(voi) in voivec:
                i1 = segments[i].findpoint(burnup=burnup, vhi=voi, voi=voi)
                POW[i, :, :] = segments[i].statepoints[i1].POW
            else:
                voi1 = max([x for x in voivec if x < voi])
                i1 = segments[i].findpoint(burnup=burnup, vhi=voi1, voi=voi1)
                voi2 = min([x for x in voivec if x > voi])
                i2 = segments[i].findpoint(burnup=burnup, vhi=voi2, voi=voi2)
                P1 = segments[i].statepoints[i1].POW
                P2 = segments[i].statepoints[i2].POW
                POW[i, :, :] = self.bundle.interp2(P1, P2, voi1, voi2, voi)
                
        POW3 = self.bundle.pow3(POW, nodes)
        return POW3

    def calc_btf(self):
        """Calculating BTF"""
        print "Calculating BTF"
        tic = time.time()
        x = self.intersect_points()
        
        npst = self.bundle.states[0].segments[0].data.npst
        self.DOX = np.zeros((len(x), npst, npst))

        fuetype = self.bundle.data.fuetype
        if fuetype == "OPT2":
            voi = 50
            rfact_fun = btf_opt2
        elif fuetype == "OPT3":
            print "Warning: BTF is not yet implemented for this fuel type."
            print "Using OPT2 dryout performance calculation instead."
            voi = 50
            rfact_fun = btf_opt2
        elif fuetype == "A10XM":
            voi = 60
            rfact_fun = btf_a10xm
        elif fuetype == "A10B":
            voi = 60
            rfact_fun = btf_a10b
        else:
            print "Error: BTF is not implemented for this fuel type"

        for i, burnup in enumerate(x):
            POW3 = self.pow3d(voi, burnup)
            self.DOX[i, :, :] = rfact_fun(POW3)
            # self.DOX[i, :, :] = self.rfact(POW3)
        self.burnpoints = np.array(x).astype(float)
        print "Done in "+str(time.time()-tic)+" seconds."


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
