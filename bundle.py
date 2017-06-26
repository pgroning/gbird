#!/usr/bin/env python

from __future__ import division
from IPython.core.debugger import Tracer  # Debugging
from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
''' ipy example:
import bundle
: b = bundle.Bundle()
: b.readinp("file.pro")
: b.readcax()
After some code modification:
: reload(bundle)
: b.readcax()
Usage:
b0 = Bundle('file.pro')
b0.readcax()
b1 = Bundle()
b1.setup(b0)
b1.new_calc()
b1.new_btf()
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

from segment import Segment
from btf import Btf
from fileio import InpFileParser


def readcax_fun(tup):
    """Unpack input arguments for use with the Segment class"""
    return Segment(*tup)


def quickcalc_fun(tup):
    """Wrapper function used for multithreaded quickcalc"""
    segment = tup[0]  # First arg should always be an instance of the class
    segment.quickcalc(*tup[1:])
    return segment


class Data(object):
    """Empty class with the purpose to organize data"""
    pass


class Bundle(object):
    """Read, save and load cases"""

    def __init__(self, profile=None, parent=None):
        self.data = Data()

        #self.parent = parent
        if profile:
            self.readinp(profile)
        elif parent:
            self.setup(parent)

        # self.readinpfile(inpfile)
        # self.readcas()
        # self.savecasobj()
        # self.loadcasobj(inpfile)
        # self.interp2(P1,P2,x1,x2,x)

    def readinp(self, cfgfile):
        """Read project setup file"""
        
        pfile = InpFileParser(self.data)
        pfile.read(cfgfile)

        #config = ConfigParser.SafeConfigParser()
        #try:
        #    if not config.read(cfgfile):
        #        print "Could not open file '" + cfgfile + "'"
        #        return False
        #except:
        #    print "An error occured trying to read the file '" + cfgfile + "'"
        #    return False

        # Get fuel type
        #self.data.fuetype = config.get("Bundle", "fuel")
        #if self.data.fuetype not in ('A10XM', 'A10B', 'AT11', 'OPT2', 'OPT3'):
        #    print("Error: Unknown fuel type.")
        #    return False
        
        # cax files
        #files = config.get("Bundle", "files")
        #file_list = filter(None, re.split("\n", files))
        #file_list.reverse()
        #file_list = file_list[::-1]  # reverse order
        #self.data.caxfiles = file_list
        
        # relative heights
        #nodes = re.split("\s+|,\s*", config.get("Bundle", "nodes"))
        #nodes = filter(None, nodes)
        #self.data.nodes = map(int, nodes)
        #if len(self.data.nodes) != len(self.data.caxfiles):
        #    print "Error: Invalid node list."
        #    return False
        
        # content read option
        #self.data.content = "filtered"  # default value
        #if config.has_option("Bundle", "content"):
        #    self.data.content = config.get("Bundle", "content")
        #if self.data.content not in ("filtered", "unfiltered"):
        #    print "Error: Unknown content option."
        #    return False
        
        # BTF options
        #if config.has_section("BTF"):
            # BTF zone vector
            #btf_zones = re.split("\s+|,\s*", config.get("BTF", "zones"))
            #btf_zones = filter(None, btf_zones)
            #self.data.btf_zones = map(int, btf_zones)
            # BTF nodes
        #    btf_nodes = re.split("\s+|,\s*", config.get("BTF", "nodes"))
        #    btf_nodes = filter(None, btf_nodes)
        #    self.data.btf_nodes = map(int, btf_nodes)
        #else:
        #    #self.data.btf_zones = [1] * len(self.data.nodes)
        #    self.data.btf_nodes = self.data.nodes

        # Perturbation calculation
        #self.data.dep_max = None
        #self.data.dep_thres = None
        #self.data.voi = None
        #self.data.model = "c3"
        #
        #if config.has_section("Pertcalc"):
        #    if config.has_option("Pertcalc", "dep_max"):
        #        dep_max = config.get("Pertcalc", "dep_max")
        #        if dep_max != "undef":
        #            self.data.dep_max = float(dep_max)
        #    if config.has_option("Pertcalc", "dep_thres"):
        #        dep_thres = config.get("Pertcalc", "dep_thres")
        #        if dep_thres != "undef":
        #            self.data.dep_thres = float(dep_thres)
        #    if config.has_option("Pertcalc", "voi"):
        #        voi = config.get("Pertcalc", "voi")
        #        if voi != "undef":
        #            self.data.voi = int(voi)
        #    if config.has_option("Pertcalc", "model"):
        #        model = config.get("Pertcalc", "model")
        #        if model != "undef":
        #            self.data.model = model

        #return True
    

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
    def readcax(self, content="filtered"):
        """Read multiple caxfiles using multithreading.
        Syntax:
        readcax() reads the first part of the file where voi=vhi
        readcax('unfiltered') reads the whole file."""

        inlist = []  # Bundle input args
        for caxfile in self.data.caxfiles:
            inlist.append((caxfile, content))

        n = len(self.data.caxfiles)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        # Start processes in their own threads and return the results
        self.segments = p.map(readcax_fun, inlist)
        #self.cases = p.map(readcax_fun, inlist)
        # self.cases = p.map(casdata, self.data.caxfiles)
        p.close()
        p.join()
        
        for i, node in enumerate(self.data.nodes):
            self.segments[i].topnode = node

        # for i,f in enumerate(self.data.caxfiles):
        #     case = casdata(f)
        #     case.data.topnode = self.data.nodes[i]
        #     self.cases.append(case)

    def read_single_cax(self, caxfile):
        print "Reading single cax file..."
        # Init data
        self.data.caxfiles = [caxfile]
        self.data.nodes = [25]  # max node
        # BTF
        self.data.btf_zones = [1] * len(self.data.nodes)
        self.data.btf_nodes = self.data.nodes
        # Read data
        self.readcax()
        # Guess fuel type
        fuetype = self.segments[0].looks_like_fuetype()
        if fuetype == "S96":
            self.data.fuetype = "OPT2"
        elif fuetype == "A10":
            self.data.fuetype = "A10B"

    def new_calc(self, voi=None, dep_max=None, dep_thres=None, grid=False,
                 model="c3", box_offset=0.0, c4ver=None, neulib=None,
                 gamlib=None, keepfiles=False):
        
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
        
        segments = self.segments
        for s in segments:
            inlist.append((s, voi, dep_max, dep_thres, grid, model,
                           box_offset, c4ver, neulib, gamlib, keepfiles))
        
        #quickcalc_fun(inlist[0])
        
        n = len(segments)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        
        self.segments = p.map(quickcalc_fun, inlist)
        #self.cases = p.map(quickcalc_fun, inlist)
        # cases = p.map(quickcalc_fun, self.cases)
        p.close()
        p.join()

    def setup(self, parent):
        """Setup new Bundle instance and copy/link data from parent"""

        self.data = parent.data
        self.segments = []
        for s in parent.segments:
            self.segments.append(Segment())
            self.segments[-1].data = copy.copy(s.data)
            self.segments[-1].topnode = s.topnode
            #self.segments[-1].statepoints = s.statepoints
            self.segments[-1].burnlist = [s.burnpoints(voi=v) 
                                          for v in s.data.voilist]

#    def append_state(self):
#        """Append a list element to store new segment instancies"""
#
#        self.states.append(DataStruct())  # Add an new state element
#        self.states[-1].segments = []
#        for s in self.states[0].segments:  # Add new segments
#            self.states[-1].segments.append(Segment())
#            # copy data from original state
#            self.states[-1].segments[-1].data = copy.copy(s.data)
#            #self.states[-1].segments[-1].data = copy.deepcopy(s.data)

#    def savepic(self, pfile):
#        """Save objects to a python pickle file"""
#
#        with open(pfile, 'wb') as fp:
#            pickle.dump(self.data, fp, 1)
#            pickle.dump(self.cases, fp, 1)
#            pickle.dump(self.states, fp, 1)
#        print "Saved data to file " + pfile

#    def loadpic(self, pfile):
#        """Load objects from a python pickle file"""
#
#        print "Loading data from file " + pfile
#        with open(pfile, 'rb') as fp:
#            self.data = pickle.load(fp)
#            self.cases = pickle.load(fp)
#            self.states = pickle.load(fp)
#           
#        self.data.pfile = pfile

    def new_btf(self):
        """Administrates btf calculation by composition of the Btf class"""
        
        #nstates = len(self.states)
        #nstates = len(self.cases[0].states)
        #while len(self.states) < nstates:
        #    self.states.append(DataStruct())
        self.btf = Btf(self)
        self.btf.calc_btf()
        
    def ave_enr_calc(self):
        """The method calculates the average enrichment of the bundle."""

        nodelist = self.data.nodes
        dn = np.array(nodelist)
        #nodes = np.array([0] + nodelist)  # prepend 0
        #dn = np.diff(nodes)
        
        segments = self.segments
        #qtrace()
        enrlist = [seg.ave_enr for seg in segments]
        #enrlist = [seg.data.ave_enr for seg in segments]
        seg_enr = np.array(enrlist)

        ave_enr = sum(seg_enr * dn) / sum(dn)
        #self.states[state_num].ave_enr = ave_enr
        return ave_enr

    def pow3(self, POW, nodes, zdim=25):
        """Expanding a list of 2D pin power distributions into a 3D array."""

        xdim = POW.shape[1]
        ydim = POW.shape[2]
        # powlist = [arg for arg in args]
        # xdim = powlist[0].shape[0]
        # ydim = powlist[0].shape[1]
        # nodes = self.data.nodes

        # only non-zero elements should be considered
        nodes = [n for n in nodes if n]
        #nodes = np.array(nodes).astype(int)
        nodes = np.array(nodes).astype(float)
        
        #zdim = max(nodes)
        #zdim = 25  # number of nodes
        POW3 = np.zeros((zdim, xdim, ydim))

        #nodes = map(float, nodes) / sum(nodes) * zdim  # rescaling
        nodes = nodes / sum(nodes) * zdim  # rescaling
        #nodes = nodes / nodes[-1] * zdim  # rescale nodes
        
        # convert to int and make sure sum of nodes equals zdim
        #i = np.argmax(nodes-nodes.astype(int))
        nodes_int = nodes.round().astype(int)
        if zdim > sum(nodes_int):
            i = np.argmax(nodes-nodes_int) 
            nodes_int[i] += zdim - sum(nodes_int)
        elif zdim < sum(nodes_int):
            i = np.argmin(nodes-nodes_int) 
            nodes_int[i] += zdim - sum(nodes_int)

        z = 0
        for i, n in enumerate(nodes_int):
            for j in range(n):
                POW3[z, :, :] = POW[i]
                z += 1

        #z0 = 0
        #for i, P in enumerate(POW):
        #    z1 = nodes[i]
        #    for z in range(z0, z1):
        #        POW3[z, :, :] = P
        #    z0 = z1
        
        return POW3

    def interp2(self, P1, P2, x1, x2, x):
        """Lagrange two point (P2) interpolation
        Syntax: Pi = interp2(P1, P2, x1, x2, x)"""

        # Lagrange P2 polynomial
        L1 = (x-x2) / (x1-x2)
        L2 = (x-x1) / (x2-x1)
        Pi = L1*P1 + L2*P2
        return Pi

    def interp3(self, P1, P2, P3, x1, x2, x3, x):
        """Lagrange three point (P3) interpolation
        Syntax: Pi = interp3(P1, P2, P3, x1, x2, x3, x)"""

        # Lagrange P3 polynomial
        L1 = ((x-x2) * (x-x3)) / ((x1-x2) * (x1-x3))
        L2 = ((x-x1) * (x-x3)) / ((x2-x1) * (x2-x3))
        L3 = ((x-x1) * (x-x2)) / ((x3-x1) * (x3-x2))
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
