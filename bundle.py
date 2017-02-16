#!/usr/bin/env python

from __future__ import division
from IPython.core.debugger import Tracer  # Debugging
from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
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
import ConfigParser
import copy

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
    segment = tup[0]  # First argument should always be an instance of the class
    segment.quickcalc(*tup[1:])
    return segment
    # case, voi, maxdep, opt = tup
    # case.quickcalc(voi, maxdep, opt)
    # return case


class Bundle(object):
    """Read, save and load cases"""

    #def __init__(self, parent=None):
    def __init__(self, inpfile=None):
        self.data = DataStruct()
        #self.cases = []
        # self.btf = Btf(self)
        self.states = []
        self.states.append(DataStruct())

        #self.parent = parent
        if inpfile:
            self.readinp(inpfile)

        # self.readinpfile(inpfile)
        # self.readcas()
        # self.savecasobj()
        # self.loadcasobj(inpfile)
        # self.interp2(P1,P2,x1,x2,x)

    def readinp(self, cfgfile):

        config = ConfigParser.ConfigParser()
        try:
            if not config.read(cfgfile):
                print "Could not open file '" + cfgfile + "'"
                return
        except:
            print "An error occured trying to read the file '" + cfgfile + "'"
            return

        # Get fuel type
        self.data.fuetype = config.get("Bundle", "fuetype")
        if self.data.fuetype not in ('A10XM', 'A10B', 'AT11', 'OPT2', 'OPT3'):
            print("Error: Unknown fuel type.")
            return

        # cax files
        files = config.get("Bundle", "files")
        self.data.caxfiles = filter(None, re.split("\n", files))

        # node list
        nodes = re.split("\s+|,\s*", config.get("Bundle", "nodes"))
        nodes = filter(None, nodes)
        self.data.nodes = map(int, nodes)
        if len(self.data.nodes) != len(self.data.caxfiles):
            print "Error: Invalid node list."
            return

        if config.has_section("BTF"):
            # BTF zone vector
            btf_zones = re.split("\s+|,\s*", config.get("BTF", "zones"))
            btf_zones = filter(None, btf_zones)
            self.data.btf_zones = map(int, btf_zones)
            # BTF nodes
            btf_nodes = re.split("\s+|,\s*", config.get("BTF", "nodes"))
            btf_nodes = filter(None, btf_nodes)
            self.data.btf_nodes = map(int, btf_nodes)
        else:
            self.data.btf_zones = [1] * len(self.data.nodes)
            self.data.btf_nodes = self.data.nodes

    '''
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
        if fuetype not in ('A10XM', 'A10B', 'AT11', 'OPT2', 'OPT3'):
            print("Error: Unknown fuel type.")
            return
        # Search for caxfiles
        reCAX = re.compile('.cax\s*$')
        caxfiles = []
        for i, x in enumerate(flines[1:]):
            if reCAX.search(x):
                if os.path.isfile(x):
                    caxfiles.append(x)
                else:
                    print x + "\nError: File does not exist."
                    return
            else:
                break

        nodes = map(int, re.split('\s+', flines[i+1]))
        if i != len(nodes):
            print "Error: Invalid node list."
            return

        btf_cases = map(int, re.split('\s+', flines[i+2]))
        if i != len(btf_cases):
            print "Error: Invalid node list."
            return

        self.data.fuetype = fuetype
        self.data.inpfile = inpfile
        self.data.caxfiles = caxfiles
        self.data.nodes = nodes
        self.data.btf_cases = btf_cases
    '''
    def readcax(self, read_all=False):
        """Read multiple caxfiles using multithreading.
        Syntax:
        readcax() reads the first part of the file (where voi=vhi)
        readcax('all') reads the whole file."""

        inlist = []  # Bundle input args
        for caxfile in self.data.caxfiles:
            inlist.append((caxfile, read_all))

        n = len(self.data.caxfiles)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        # Start processes in their own threads and return the results
        self.states[0].segments = p.map(readcax_fun, inlist)
        #self.cases = p.map(readcax_fun, inlist)
        # self.cases = p.map(casdata, self.data.caxfiles)
        p.close()
        p.join()
        
        for i, node in enumerate(self.data.nodes):
            self.states[0].segments[i].topnode = node
            #self.cases[i].topnode = node

        # for i,f in enumerate(self.data.caxfiles):
        #     case = casdata(f)
        #     case.data.topnode = self.data.nodes[i]
        #     self.cases.append(case)

    def new_calc(self, voi=None, maxdep=60, depthres=None, refcalc=False,
                 grid=False, model='c3', box_offset=0, neulib=False):

        # For storage of new calculation
        #self.new_state()

        #for s in self.states[-1].segments:
        #    s.set_data(box_offset=box_offset)
            
        # self.cases[i].add_state() 

        # ----Code block only for testing purpose-----
        #segments = self.states[0].segments
        # if not refcalc:
        #for i in range(len(self.states[0].segments)):
        #    LFU = self.states[0].segments[i].data.LFU
        #    FUE = self.states[0].segments[i].data.FUE
        #    BA = self.states[0].segments[i].data.BA
        #    voivec = self.states[0].segments[i].data.voivec
        #    
        #    self.states[-1].segments[i].set_data(LFU, FUE, BA, voivec)
        #    #self.states[-1].segments[i].data.LFU = LFU
        #    self.states
        #        self.cases[i].add_calc(LFU)
        #        #self.cases[i].data[-1].data.LFU = \
        #        #self.cases[i].data[0].data.LFU
        # --------------------------------------------
        inlist = []  # Bundle input args
        
        segments = self.states[-1].segments
        for s in segments:
            inlist.append((s, voi, maxdep, depthres, refcalc, grid,
                           model, box_offset, neulib))
        
        #quickcalc_fun(inlist[0])
        #Tracer()()
        n = len(segments)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        
        self.states[-1].segments = p.map(quickcalc_fun, inlist)
        #self.cases = p.map(quickcalc_fun, inlist)
        # cases = p.map(quickcalc_fun, self.cases)
        p.close()
        p.join()

    def append_state(self):
        """Append a list element to store new segment instancies"""

        self.states.append(DataStruct())  # Add an new state element
        self.states[-1].segments = []
        for s in self.states[0].segments: # Add new segments
            self.states[-1].segments.append(Segment())
            # deep copy data from original state
            self.states[-1].segments[-1].data = copy.deepcopy(s.data)

    def savepic(self, pfile):
        """Save objects to a python pickle file"""

        with open(pfile, 'wb') as fp:
            pickle.dump(self.data, fp, 1)
            pickle.dump(self.cases, fp, 1)
            pickle.dump(self.states, fp, 1)
        print "Saved data to file " + pfile

    def loadpic(self, pfile):
        """Save objects from a python pickle file"""

        print "Loading data from file " + pfile
        with open(pfile, 'rb') as fp:
            self.data = pickle.load(fp)
            self.cases = pickle.load(fp)
            self.states = pickle.load(fp)
            
        self.data.pfile = pfile

    def new_btf(self):
        """Administrates btf calculation by composition of the Btf class"""

        nstates = len(self.states)
        #nstates = len(self.cases[0].states)
        #while len(self.states) < nstates:
        #    self.states.append(DataStruct())

        self.states[-1].btf = Btf(self)
        self.states[-1].btf.calc_btf()
        
    def ave_enr_calc(self, state_num=-1):
        """The method calculates the average enrichment of the bundle.
        This algorithm is likely naive and needs to be updated in the future"""

        nodelist = self.data.nodes
        # nodelist.insert(0, 0)  # prepend 0
        # nodes = np.array(nodelist)
        nodes = np.array([0]+nodelist)  # prepend 0
        dn = np.diff(nodes)
        segments = self.states[state_num].segments
        enrlist = [seg.data.ave_enr for seg in segments]
        seg_enr = np.array(enrlist)

        ave_enr = sum(seg_enr*dn) / sum(dn)
        self.states[state_num].ave_enr = ave_enr

    def pow3(self, POW, nodes):
        """Expanding a number of 2D pin power distributions into a 3D
        distribution.
        Syntax: POW3D = pow3(POW1,POW2,POW3,...)"""

        xdim = POW.shape[1]
        ydim = POW.shape[2]
        # powlist = [arg for arg in args]
        # xdim = powlist[0].shape[0]
        # ydim = powlist[0].shape[1]
        # nodes = self.data.nodes
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
    pass
    #cio = casio()
    #cio.readinp(sys.argv[1])
    #cio.readcax()
    #cio.runc3()

    '''
    P1 = sys.argv[1]
    P2 = sys.argv[2]
    x1 = sys.argv[3]
    x2 = sys.argv[4]
    x = sys.argv[5]
    casio(P1,P2,x1,x2,x)
    '''
