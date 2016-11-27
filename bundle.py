#!/usr/bin/env python

from __future__ import division
from IPython.core.debugger import Tracer  # Debugging
''' ipy example:
import bundle
: obj = bundle.bundle()
: obj.readinp("file.inp")
: obj.readcax()
After some code modification:
: reload(bundle)
: obj.readcax()
'''

try:
    import cPickle as pickle
except:
    import pickle

import sys
import os.path
import re
import numpy as np

from multiprocessing import Pool
from segment import Segment, DataStruct
from btf import Btf


def readcax_fun(tup):
    """Unpack input arguments for use with the casdata class"""
    return Segment(*tup)
    # caxfile, opt = tup
    # return casdata(caxfile, opt)


def quickcalc_fun(tup):
    """Wrapper function used for multithreaded quickcalc"""
    case = tup[0]  # First arg should always be the object
    case.quickcalc(*tup[1:])
    return case
    # case, voi, maxdep, opt = tup
    # case.quickcalc(voi, maxdep, opt)
    # return case


class Bundle(Btf):
    """Read, save and load cases"""

    def __init__(self, inpfile=None):
        super(Bundle, self).__init__(self)
        self.data = DataStruct()
        self.cases = []

        if inpfile:
            self.readinp(inpfile)
            
        # self.readinpfile(inpfile)
        # self.readcas()
        # self.savecasobj()
        # self.loadcasobj(inpfile)
        # self.interp2(P1,P2,x1,x2,x)

    def readinp(self, inpfile):
        if not os.path.isfile(inpfile):
            print "Could not open file " + inpfile
            return
        else:
            print "Reading file " + inpfile

        with open(inpfile) as f:
            flines = f.read().splitlines()  # exclude \n

        # Read fuel type
        fuetype = flines[0].strip()
        # Search for caxfiles
        reCAX = re.compile('.cax\s*$')
        caxfiles = []
        for i, x in enumerate(flines[1:]):
            if reCAX.search(x):
                caxfiles.append(x)
            else:
                break
        i += 1
        nodes = map(int, re.split('\s+', flines[i]))

        self.data.fuetype = fuetype
        self.data.inpfile = inpfile
        self.data.caxfiles = caxfiles
        self.data.nodes = nodes

    def readcax(self, read_content=None):
        """Read multiple caxfiles using multithreading.
        Syntax:
        readcax() reads the first part of the file (where voi=vhi)
        readcax('all') reads the whole file."""

        inlist = []  # Bundle input args
        for caxfile in self.data.caxfiles:
            inlist.append((caxfile, read_content))

        n = len(self.data.caxfiles)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        # Start processes in their own threads and return the results
        self.cases = p.map(readcax_fun, inlist)
        # self.cases = p.map(casdata, self.data.caxfiles)
        p.close()
        p.join()
        for i, node in enumerate(self.data.nodes):
            self.cases[i].topnode = node

        # for i,f in enumerate(self.data.caxfiles):
        #     case = casdata(f)
        #     case.data.topnode = self.data.nodes[i]
        #     self.cases.append(case)

    def runc3(self, voi=None, maxdep=None, opt='refcalc'):

        # ----Code block only for testing purpose-----
        if opt != 'refcalc':
            for i in range(len(self.cases)):
                self.cases[i].add_calc()
                self.cases[i].data[-1].data.LFU = \
                self.cases[i].data[0].data.LFU
        # --------------------------------------------

        inlist = []  # Bundle input args
        for case in self.cases:
            inlist.append((case, voi, maxdep, opt))

        # quickcalc_fun(inlist[1])
        n = len(self.cases)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        self.cases = p.map(quickcalc_fun, inlist)
        # cases = p.map(quickcalc_fun, self.cases)
        p.close()
        p.join()

    def savepic(self, pfile):
        # pfile = os.path.splitext(self.data.inpfile)[0] + '.p'
        with open(pfile, 'wb') as fp:
            pickle.dump(self.data, fp, 1)
            pickle.dump(self.cases, fp, 1)
            try:
                pickle.dump(self.btf, fp, 1)
            except:
                print "Warning: Could not save BTF"
        print "Saved data to file " + pfile

    def loadpic(self, pfile):
        print "Loading data from file " + pfile
        with open(pfile, 'rb') as fp:
            self.data = pickle.load(fp)
            self.cases = pickle.load(fp)
            try:
                self.btf = pickle.load(fp)
            except:
                print "Warning: Could not load BTF"
        self.data.pfile = pfile

    #def calc_btf(self):
    #    """Administrates btf calculation by composition of the Btf class"""
    #    self.btf = Btf(self)
    #    self.btf.calc_btf()

    def ave_enr(self):
        """The method calculates the average enrichment of the bundle.
        This algorithm is likely naive and needs to be updated in the future"""

        nodelist = self.data.nodes
        nodelist.insert(0, 0)  # prepend 0
        nodes = np.array(nodelist)
        dn = np.diff(nodes)

        enrlist = [case.data[-1].data.ave_enr for case in self.cases]
        seg_enr = np.array(enrlist)

        ave_enr = sum(seg_enr*dn) / sum(dn)
        self.data.ave_enr = ave_enr

    def pow3(self, POW):
        """Expanding a number of 2D pin power distributions into a 3D
        distribution.
        Syntax: POW3D = pow3(POW1,POW2,POW3,...)"""

        xdim = POW.shape[1]
        ydim = POW.shape[2]
        # powlist = [arg for arg in args]
        # xdim = powlist[0].shape[0]
        # ydim = powlist[0].shape[1]
        nodes = self.data.nodes
        zdim = max(nodes)
        POW3 = np.zeros((zdim, xdim, ydim))
        z0 = 0
        for i, P in enumerate(POW):
            z1 = nodes[i]
            for z in range(z0, z1):
                POW3[z, :, :] = P
            z0 = z1

        return POW3

    def interp2(self, P1, P2, x1, x2, x):
        """Lagrange two point (P2) interpolation
        Syntax: Pi = interp2(P1, P2, x1, x2, x)"""

        # Lagrange P2 polynomial
        L1 = (x-x2)/(x1-x2)
        L2 = (x-x1)/(x2-x1)
        Pi = L1*P1 + L2*P2
        return Pi

    def interp3(self, P1, P2, P3, x1, x2, x3, x):
        """Lagrange three point (P3) interpolation
        Syntax: Pi = interp3(P1, P2, P3, x1, x2, x3, x)"""

        # Lagrange P3 polynomial
        L1 = ((x-x2)*(x-x3))/((x1-x2)*(x1-x3))
        L2 = ((x-x1)*(x-x3))/((x2-x1)*(x2-x3))
        L3 = ((x-x1)*(x-x2))/((x3-x1)*(x3-x2))
        Pi = L1*P1 + L2*P2 + L3*P3
        return Pi


if __name__ == '__main__':
    cio = casio()
    cio.readinp(sys.argv[1])
    cio.readcax()
    cio.runc3()

    '''
    P1 = sys.argv[1]
    P2 = sys.argv[2]
    x1 = sys.argv[3]
    x2 = sys.argv[4]
    x = sys.argv[5]
    casio(P1,P2,x1,x2,x)
    '''
