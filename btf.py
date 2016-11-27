#!/usr/bin/python

# Profiler:
# import cProfile
# cProfile.run('b.rfact()')

from IPython.core.debugger import Tracer

import sys
import time
import numpy as np

from btf_opt2 import btf_opt2
#from lib.btf_opt2 import btf_opt2

#sys.path.append('lib/')
#import libADDC


class Btf(object):
    """Calculate BTF values"""
    
    def __init__(self, bundleobj):
        self.bundleobj = bundleobj
        #self.rfact()
        #self.pow3d(voi=50,burnup=0)

    def lastindex(self,case_id):
        """Iterate over burnup points"""
        statepoints = self.bundleobj.cases[case_id].states[-1].statepoints
        burnup_old = 0.0
        for idx,p in enumerate(statepoints):
            if p.burnup < burnup_old:
                break
            burnup_old = p.burnup
        return idx

    def intersect_points(self):
        """Find intersection burnup points for all cases"""
        
        segments = self.bundleobj.cases
        nsegments = len(segments)
        idx = self.lastindex(0)
        x = [segments[0].states[-1].statepoints[i].burnup for i in range(idx)]
        for j in range(1,nsegments):
            idx = self.lastindex(j)
            x2 = ([segments[j].states[-1].statepoints[i].burnup
                   for i in range(idx)])
            x = [val for val in x if val in x2]
        return x

    
    def pow3d(self, voi, burnup):
        """Construct a 3D pin power distribution for specific void and burnup.
        Use interpolation if necessary."""

        segments = self.bundleobj.cases
        nsegments = len(segments)
        npst = segments[0].states[0].npst
        POW = np.zeros((nsegments, npst, npst))
        # determine which voids are present in data
        for i in range(nsegments):
            voivec = segments[i].states[-1].voivec
            if str(voi) in voivec:
                i1 = (segments[i].findpoint(stateindex=-1,
                                            burnup=burnup, vhi=voi, voi=voi))
                POW[i, :, :] = segments[i].states[-1].statepoints[i1].POW
            else:
                
                voi1 = max([x for x in map(int,voivec) if x < voi])
                i1 = (segments[i].findpoint(stateindex=-1,
                                            burnup=burnup, vhi=voi1, voi=voi1))
                voi2 = min([x for x in map(int,voivec) if x > voi])
                i2 = (segments[i].findpoint(stateindex=-1,
                                            burnup=burnup, vhi=voi2, voi=voi2))
                P1 = segments[i].states[-1].statepoints[i1].POW
                P2 = segments[i].states[-1].statepoints[i2].POW
                POW[i, :, :] = self.bundleobj.interp2(P1, P2, voi1, voi2, voi)

        POW3 = self.bundleobj.pow3(POW)
        return POW3

    def calc_btf(self):
        """Calculating BTF"""
        print "Calculating BTF"
        print self.data.fuetype
        tic = time.time()
        x = self.intersect_points()
        npst = self.bundleobj.cases[0].states[0].npst
        self.DOX = np.zeros((len(x),npst,npst))
        
        voi = 50
        
        for i, burnup in enumerate(x):
            POW3 = self.pow3d(voi, burnup)
            self.DOX[i,:,:] = self.rfact(self.bundleobj.data.fuetype, POW3)
        self.burnup = x
        print "Done in "+str(time.time()-tic)+" seconds."
        
    def rfact(self, fuetype, POW3):
        if fuetype == 'OPT2':
            #print "Calculating BTF for OPT2"
            DOX = btf_opt2(POW3)
        elif fuetype == 'ATXM':
            print "Calculating BTF for ATXM"
            # DOX = btf_atxm(AC, POW3)
        return DOX

    if __name__ == '__main__':
        import bundle
        import btf
        inpfile = sys.argv[1]
        bundleobj = bundle.Bundle(inpfile)
        bundleobj.readcax()
        b = btf.Btf(bundleobj)
        b.calc_btf()
        
