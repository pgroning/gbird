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

import sys
import numpy as np
import copy
from multiprocessing import Pool

from segment import Segment
from btf import Btf
from fileio import InpFileParser


def readcax_fun(tup):
    """Unpack input arguments for use with the Segment class"""
    return Segment(*tup)


def calc_fun(tup):
    """Wrapper function used for multithreaded quickcalc"""
    segment = tup[0]  # First arg should always be an instance of the class
    segment.cas_calc(*tup[1:])
    return segment


class Data(object):
    """Empty class with the purpose to organize data"""
    pass


class Bundle(object):
    """Read, save and load cases"""

    def __init__(self, inpfile=None, parent=None):
        self.data = Data()

        if inpfile:
            self.readinp(inpfile)
        elif parent:
            self.setup(parent)

    def readinp(self, inpfile):
        """Read project setup file"""
        
        pfile = InpFileParser(self.data)
        pfile.read(inpfile)

    def readcax(self, content="filtered"):
        """Read multiple caxfiles using multithreading.
        Syntax:
        readcax('filtered') reads the first part of the file where voi=vhi
        readcax('unfiltered') reads the complete file."""

        inlist = []  # Bundle input args
        for caxfile in self.data.caxfiles:
            inlist.append((caxfile, content))

        n = len(self.data.caxfiles)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        # Start processes in their own threads and return the results
        self.segments = p.map(readcax_fun, inlist)
        p.close()
        p.join()
        
        for i, node in enumerate(self.data.nodes):
            self.segments[i].topnode = node

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
        
        inlist = []  # Bundle input args
        segments = self.segments
        for s in segments:
            inlist.append((s, voi, dep_max, dep_thres, grid, model,
                           box_offset, c4ver, neulib, gamlib, keepfiles))
        
        n = len(segments)  # Number of threads
        p = Pool(n)  # Make the Pool of workers
        self.segments = p.map(calc_fun, inlist)
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
            self.segments[-1].burnlist = [s.burnpoints(voi=v) 
                                          for v in s.data.voilist]
            
    def new_btf(self):
        """Administrates btf calculation"""
        
        self.btf = Btf(self)
        self.btf.calc_btf()
        
    def ave_enr_calc(self):
        """The method calculates the average enrichment of the bundle."""

        nodelist = self.data.nodes
        dn = np.array(nodelist)
        
        segments = self.segments
        enrlist = [seg.ave_enr for seg in segments]
        seg_enr = np.array(enrlist)

        ave_enr = sum(seg_enr * dn) / sum(dn)
        return ave_enr

    def pow3(self, POW, nodes, zdim=25):
        """Expanding a list of 2D pin power distributions into a 3D array."""

        xdim = POW.shape[1]
        ydim = POW.shape[2]

        # only non-zero elements should be considered
        nodes = [n for n in nodes if n]
        nodes = np.array(nodes).astype(float)
        
        POW3 = np.zeros((zdim, xdim, ydim))

        nodes = nodes / sum(nodes) * zdim  # rescaling
        
        # convert to int and make sure sum of nodes equals zdim
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
    b = Bundle(sys.argv[1])
