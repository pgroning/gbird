from __future__ import division
from IPython.core.debugger import Tracer

try:
    import cPickle as pickle
except:
    import pickle

import sys
import os
import re
import numpy as np
from multiprocessing import Pool

from casdata import casdata

# from btf import btf

'''
class datastruct(object):
    """Dummy class used to structure data"""
    pass
'''

class Casio(object):
    """Read, save and load cases"""

    def __init__(self):
        self.data = {}
        # self.data = datastruct()
        self.case = []

        '''
        #self.readinpfile(inpfile)
        #self.readcas()
        #self.savecasobj()
        #self.loadcasobj(inpfile)
        #self.interp2(P1,P2,x1,x2,x)
        '''

    def readinp(self, inpfile):
        """Reading caxfiles and nodes from input file"""

        if not os.path.isfile(inpfile):
            print "Could not open file " + inpfile
            return
        else:
            print "Reading file " + inpfile

        with open(inpfile) as f:
            flines = f.read().splitlines()  # exclude \n

        fuetype = flines[0].strip()  # Read fuel type
        reCAX = re.compile('.cax\s*$')  # Search for caxfiles
        caxfiles = []
        for i, x in enumerate(flines[1:]):
            if reCAX.search(x):
                caxfiles.append(x)
            else:
                break
        i += 1
        nodes = map(int, re.split('\s+', flines[i]))

        self.data.update({'fuetype': fuetype, 'inpfile': inpfile,
                          'caxfiles': caxfiles, 'nodes': nodes})

        '''
        self.data.fuetype = fuetype
        self.data.inpfile = inpfile
        self.data.caxfiles = caxfiles
        self.data.nodes = nodes
        '''

    def readcax(self):
        n = len(self.data.caxfiles) # Number of threads
        p = Pool(n) # Make the Pool of workers
        # Start processes in their own threads and return the results
        self.cases = p.map(casdata, self.data.caxfiles)
        for i,node in enumerate(self.data.nodes):
            self.cases[i].data.topnode = node

        #for i,f in enumerate(self.data.caxfiles):
        #    case = casdata(f)
        #    case.data.topnode = self.data.nodes[i]
        #    self.cases.append(case)


    def savepic(self,pfile):
        #pfile = os.path.splitext(self.data.inpfile)[0] + '.p'
        with open(pfile,'wb') as fp:
            pickle.dump(self.data,fp,1)
            pickle.dump(self.cases,fp,1)
            try:
                pickle.dump(self.btf,fp,1)
            except:
                print "Warning: Could not save BTF"
        print "Saved data to file " + pfile
        

    def loadpic(self,pfile):
        print "Loading data from file " + pfile
        with open(pfile,'rb') as fp:
            self.data = pickle.load(fp)
            self.cases = pickle.load(fp)
            try:
                self.btf = pickle.load(fp)
            except:
                print "Warning: Could not load BTF"
        self.data.pfile = pfile


    def calcbtf(self):
        self.btf = btf(self)
        #fuetype = 'SVEA-96'
        #self.btf = btf(self,fuetype)


    def pow3(self,POW):
    #def pow3(self,*args):
        """Expanding a number of 2D pin power distributions into a 3D distribution.
        Syntax: POW3D = pow3(POW1,POW2,POW3,...)"""
        #print "Expanding a number of 2D pin power distributions into a 3D distribution"
   
        xdim = POW.shape[1]
        ydim = POW.shape[2]
        #powlist = [arg for arg in args]
        #xdim = powlist[0].shape[0]
        #ydim = powlist[0].shape[1]
        nodes = self.data.nodes
        zdim = max(nodes)
        POW3 = np.zeros((zdim,xdim,ydim))
        z0 = 0
        for i,P in enumerate(POW):
        #for i,POW in enumerate(powlist):
            z1 = nodes[i]
            for z in range(z0,z1):
                POW3[z,:,:] = P 
            z0 = z1

        return POW3
        

    def interp2(self,P1,P2,x1,x2,x):
        """Lagrange two point (P2) interpolation
        Syntax: Pi = interp2(P1,P2,x1,x2,x)"""

        # Lagrange P2 polynomial
        L1 = (x-x2)/(x1-x2)
        L2 = (x-x1)/(x2-x1)
        Pi = L1*P1 + L2*P2
        return Pi


    def interp3(self,P1,P2,P3,x1,x2,x3,x):
        """Lagrange three point (P3) interpolation
        Syntax: Pi = interp3(P1,P2,P2,x1,x2,x3,x)"""

        # Lagrange P3 polynomial
        L1 = ((x-x2)*(x-x3))/((x1-x2)*(x1-x3))
        L2 = ((x-x1)*(x-x3))/((x2-x1)*(x2-x3))
        L3 = ((x-x1)*(x-x2))/((x3-x1)*(x3-x2))
        Pi = L1*P1 + L2*P2 + L3*P3
        return Pi


#    def findpoint(self,case,burnup=None,vhi=None,voi=None):
#        """Return statepoint index that correspond to specific burnup, void and void history
#        Syntax: pt = findpoint(case,burnup,vhi,voi)"""
#
#        #print "Finding statepoints"
#
#        #for i,p in enumerate(self.cases[case].statepts):
#        #    if p.burnup==burnup and p.vhi==vhi and p.voi==voi:
#        #        pindex = i
#        #        break
#        #Tracer()()
#        
#        if burnup is not None:
#            pindex = next(i for i,p in enumerate(self.cases[case].statepts)
#                          if p.burnup==burnup and p.vhi==vhi and p.voi==voi)
#        else:
#            pindex = next(i for i,p in enumerate(self.cases[case].statepts)
#                          if p.vhi==vhi and p.voi==voi)    
#        return pindex


if __name__ == '__main__':
    P1 = sys.argv[1]
    P2 = sys.argv[2]
    x1 = sys.argv[3]
    x2 = sys.argv[4]
    x = sys.argv[5]
    casio(P1,P2,x1,x2,x)
