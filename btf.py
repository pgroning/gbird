from IPython.core.debugger import Tracer

import numpy as np

class Btf:
    """Calculate BTF values"""
    
    def __init__(self, bundleobj):
        self.bundleobj = bundleobj
        self.pow3d(voi=50,burnup=0)
        
        
    def pow3d(self, voi, burnup):
        """Construct a 3D pin power distribution for specific void and burnup.
        Use interpolation if necessary."""

        segments = self.bundleobj.cases
        nsegments = len(segments)
        # determine which voids are present in data
        i = 0
        voivec = segments[i].states[-1].voivec
        #statepoints = segments[i].states[-1].statepoints
        if str(voi) in voivec:
            i1 = (segments[i].findpoint(stateindex=-1,
                                        burnup=burnup, vhi=voi, voi=voi))
        else:
            voi1 = int(voivec[0])
            i1 = (segments[i].findpoint(stateindex=-1,
                                        burnup=burnup, vhi=voi1, voi=voi1))
            voi2 = int(voivec[2])
            i2 = (segments[i].findpoint(stateindex=-1,
                                        burnup=burnup, vhi=voi2, voi=voi2))
            
            
        Tracer()()


    def pow3(self, POW):
        """Populate a bundle array with pin powers"""
        pass
    

    
