#!/usr/bin/env python

# Run from ipython:
# > from segment import Segment
# > s = Segment('caxfile')
#
# or:
# run segment "caxfile"
#
# How to reach name mangling ("private") methods example:
# self._Segment__matchcontent()
#

# For debugging. Add Tracer()() inside the code to break at that line
from IPython.core.debugger import Tracer
from pyqt_trace import pyqt_trace as qtrace  # Break point that works with Qt
# Inside iptyhon shell: run -d b<L> readfile.py
# sets a break point add line L.

import numpy as np
import re
import os
import sys
import time
from subprocess import call, STDOUT
import uuid  # used for random generated file names
import shlex  # used for splitting subprocess call argument string into a list
import copy

from fileio import DefaultFileParser


class Data(object):
    """A class that can be used to organize data in its attributes"""
    pass


class Segment(object):

    def __init__(self, caxfile=None, content="filtered"):
        self.verbose = False

        path = os.path.realpath(__file__)
        self.appdir = os.path.split(path)[0] + os.sep
        
        self.data = Data()
        self.config = DefaultFileParser(self.appdir + "gb.defaults")

        if caxfile:
            self.readcax(caxfile, content)

    # -------Read cax file---------
    def __matchcontent(self, flines, regexp, opt='all'):
        rec = re.compile(regexp)
        if opt == 'all':
            out = [i for i, x in enumerate(flines) if rec.match(x)]
        elif opt == 'next':
            out = next((i for i, x in enumerate(flines) if rec.match(x)), None)
        elif opt == 'object':
            out = (i for i, x in enumerate(flines) if rec.match(x))
        return out

    def __symmap(self, lines, npst, dtype=float):
        M = self.__symtrans(self.__map2mat(lines, npst)).astype(dtype)
        return M

    def __get_FUE(self, flines, iFUE):
        Nfue = len(iFUE)
        FUE = np.zeros((Nfue, 5))
        FUE.fill(np.nan)
        for i, idx in enumerate(iFUE):
            rstr = flines[idx].replace(',', ' ').strip()
            rstr = rstr.replace('/', ' ').strip()
            rstr = rstr.replace('=', ' ').strip()
            rvec = re.split('\*', rstr, 1)  # split on first occurence
            rstr = rvec[0].strip()
            rvec = re.split('\s+', rstr)
            FUE[i, :len(rvec[1:])] = rvec[1:]
        return FUE

    def __get_pin(self, flines, iPIN):
        plist = []
        for idx in iPIN:
            rstr = flines[idx].replace(',', ' ').strip()
            rvec = re.split('/|\*', rstr)
            rstr = rvec[0].strip()
            rvec = re.split('\s+', rstr.strip())
            rlen = np.size(rvec)
            plist.append(rvec[1:])

        Npin = len(plist)
        ncols = max(map(len, plist))
        PIN = np.zeros((Npin, ncols), dtype=float)
        PIN.fill(np.nan)
        for i, pl in enumerate(plist):
            PIN[i, :len(pl)] = pl
        return PIN

    def __lfu2enr(self, LFU, FUE):
        ENR = np.zeros(LFU.shape)
        Nfue = FUE.shape[0]
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            ENR[LFU == ifu] = FUE[i, 2]
        return ENR

    def __lfu2ba(self, LFU, FUE):
        BA = np.zeros(LFU.shape)
        Nfue = FUE.shape[0]
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            if np.isnan(FUE[i, 3]):
                BA[LFU == ifu] = 0.0
            else:
                BA[LFU == ifu] = FUE[i, 4]
        return BA

    def readcax(self, caxfile, content="filtered"):

        if not os.path.isfile(caxfile):
            print "Error: Could not open file " + caxfile
            return
        elif self.verbose:
            print "Reading file " + caxfile

        # Read the whole file
        with open(caxfile) as f:
            flines = f.read().splitlines()  # exclude \n

        # Find last index containing voids voi=vhi
        tmp_voilist = []  # temporary list of voids
        oTIT = self.__matchcontent(flines, '^TIT', 'object')
        while True:
            try:
                i = oTIT.next()
            except:  # Reaching end of flines
                i = len(flines)
                break
            # split on spaces or '/'
            rstr = re.split('[/\s+]+', flines[i+2].strip())
            voi, vhi = rstr[1], rstr[2]
            if voi != vhi:
                break
            tmp_voilist.append(voi)
        # Reduce to a unique list and also keep the order
        tmp = []
        tmp_voilist = [x for x in tmp_voilist 
                       if x not in tmp and (tmp.append(x) or True)]
        voilist = map(int, map(float, tmp_voilist))

        if content == "filtered":
            flines = flines[:i]  # Reduce the number of lines in list

        iTIT = self.__matchcontent(flines, '^TIT')
        iFUE = self.__matchcontent(flines, '^\s*FUE')
        iPOW = self.__matchcontent(flines, 'POW\s+')
        iSIM = self.__matchcontent(flines, '^\s*SIM')
        iSPA = self.__matchcontent(flines, '^\s*SPA')
        iGAM = self.__matchcontent(flines, '^\s*GAM')
        iCRD = self.__matchcontent(flines, '^\s*CRD')
        iPOL = self.__matchcontent(flines, '^POL')
        iXFL = self.__matchcontent(flines, '^XFL')
        iPIN = self.__matchcontent(flines, '^\s*PIN')
        iTTL = self.__matchcontent(flines, '^\s*TTL')
        iVOI = self.__matchcontent(flines, '^\s*VOI')
        iDEP = self.__matchcontent(flines, '^\s*DEP')
        
        # Stop looping at first finding
        iEND = self.__matchcontent(flines, '^\s*END', 'next')
        iBWR = self.__matchcontent(flines, '^\s*BWR', 'next')
        iLFU = self.__matchcontent(flines, '^\s*LFU', 'next')
        iLPI = self.__matchcontent(flines, '^\s*LPI', 'next')
        iTFU = self.__matchcontent(flines, '^\s*TFU', 'next')
        iTMO = self.__matchcontent(flines, '^\s*TMO', 'next')
        iPDE = self.__matchcontent(flines, '^\s*PDE', 'next')
        try:  # Card for water cross (valid for OPT2/3)
            iSLA = self.__matchcontent(flines, '^\s*SLA', 'next')
        except:
            iSLA = None
        iWRI = self.__matchcontent(flines, '^\s*WRI', 'next')
        iSTA = self.__matchcontent(flines, '^\s*STA', 'next')

        iLDX = self.__matchcontent(flines, '^\s*LDX', 'next')
        iLDY = self.__matchcontent(flines, '^\s*LDY', 'next')
        
        # Miscellaneous compositions
        iMIx = self.__matchcontent(flines[:iLPI], '^\s*MI[1-9]')

        # Store geninfo
        self.data.title = flines[iTTL[0]]
        self.data.sim = flines[iSIM[0]]
        self.data.tfu = flines[iTFU]
        self.data.tmo = flines[iTMO]
        self.data.voi = flines[iVOI[0]]
        self.data.pde = flines[iPDE]
        self.data.bwr = flines[iBWR]
        self.data.spa = flines[iSPA[0]]
        self.data.dep = flines[iDEP[0]]
        self.data.gam = flines[iGAM[0]]
        if iWRI:
            self.data.wri = flines[iWRI]
        self.data.sta = flines[iSTA]
        if iCRD:
            self.data.crd = flines[iCRD[0]]
        
        # get fuel dimension
        npst = int(flines[iBWR][5:7])
        # Read LFU map
        maplines = flines[iLFU+1:iLFU+1+npst]
        LFU = self.__symmap(maplines, npst, int)

        # If exist, read LDX and LDY displacement maps
        if iLDX:
            self.data.ldx_lines = flines[iLDX + 1 : iLDX + 1 + npst]
        else:
            self.data.ldx_lines = []
        if iLDY:
            self.data.ldy_lines = flines[iLDY + 1 : iLDY + 1 + npst]
        else:
            self.data.ldy_lines = []
        
        # Get MIx strings
        self.data.milines = [flines[i] for i in iMIx]
        
        # Read LPI map
        maplines = flines[iLPI+1:iLPI+1+npst]
        LPI = self.__symmap(maplines, npst, int)

        # Get FUE array
        iFUE = [i for i in iFUE if i < iEND]
        FUE = self.__get_FUE(flines, iFUE)

        # Translate LFU map to ENR map
        ENR = self.__lfu2enr(LFU, FUE)

        # Translate LFU map to BA map
        BA = self.__lfu2ba(LFU, FUE)

        # Determine number of BA rods types
        Nba = 0
        for content in FUE[:, 4]:
            if not np.isnan(content):
                Nba += 1

        # Read PIN (pin radius)
        PIN = self.__get_pin(flines, iPIN)
        Npin = PIN.shape[0]
        self.data.pinlines = flines[iPIN[0]:iPIN[0]+Npin]
        
        # Read SLA
        if iSLA is not None:
            self.data.slaline = flines[iSLA]

        # ------Iterate state points----------
        Nburnpts = len(iTIT)
        burnup = np.zeros(Nburnpts)
        burnup.fill(np.nan)
        voi = np.zeros(Nburnpts)
        voi.fill(np.nan)
        vhi = np.zeros(Nburnpts)
        vhi.fill(np.nan)
        tfu = np.zeros(Nburnpts)
        tfu.fill(np.nan)
        tmo = np.zeros(Nburnpts)
        tmo.fill(np.nan)
        kinf = np.zeros(Nburnpts)
        kinf.fill(np.nan)
        POW = np.zeros((npst, npst, Nburnpts))
        POW.fill(np.nan)
        XFL1 = np.zeros((npst, npst, Nburnpts))
        XFL1.fill(np.nan)
        XFL2 = np.zeros((npst, npst, Nburnpts))
        XFL2.fill(np.nan)

        # Read title cards
        titcrd = [flines[i] for i in iTIT]

        for i in xrange(Nburnpts):

            # Read burnup, voids, tfu and tmo
            rvec = re.split('[/\s+]+', flines[iTIT[i]+2].strip())
            burnup[i] = rvec[0]
            voi[i] = rvec[1]
            vhi[i] = rvec[2]
            tfu[i] = rvec[3]
            tmo[i] = rvec[4]
            # Read kinf
            kinfstr = flines[iPOL[i]+5]
            kinf[i] = re.split('\s+', kinfstr.strip())[0]
            # Read radial power distribution map
            powlines = flines[iPOW[i]+2:iPOW[i]+2+npst]
            POW[:, :, i] = self.__symmap(powlines, npst)
            # Read XFL maps
            if iXFL:  # check if XFL exists
                xfl1lines = flines[iXFL[i]+2:iXFL[i]+2+npst]
                XFL1[:, :, i] = self.__symmap(xfl1lines, npst)
                xfl2lines = flines[iXFL[i]+3+npst:iXFL[i]+3+2*npst]
                XFL2[:, :, i] = self.__symmap(xfl2lines, npst)
        # --------------------------------------------------------------------
        # Calculate radial burnup distributions
        EXP = self.expcalc(POW, burnup)
        # Calculate Fint:
        fint = self.fintcalc(POW)

        # Append state instancies
        self.statepoints = []
        for i in range(Nburnpts):
            # append new instance to list
            self.statepoints.append(Data())
            self.statepoints[i].titcrd = titcrd[i]
            self.statepoints[i].burnup = burnup[i]
            self.statepoints[i].voi = voi[i]
            self.statepoints[i].vhi = vhi[i]
            self.statepoints[i].tfu = tfu[i]
            self.statepoints[i].tmo = tmo[i]
            self.statepoints[i].kinf = kinf[i]
            self.statepoints[i].fint = fint[i]
            self.statepoints[i].EXP = EXP[:, :, i]
            if iXFL:
                self.statepoints[i].XFL1 = XFL1[:, :, i]
                self.statepoints[i].XFL2 = XFL2[:, :, i]
            self.statepoints[i].POW = POW[:, :, i]

        # Store geninfo
        self.data.caxfile = caxfile
        self.data.ENR = ENR
        self.data.BA = BA
        self.data.PIN = PIN
        self.data.LPI = LPI
        self.data.FUE = FUE
        self.data.LFU = LFU
        self.data.npst = npst
        self.data.voilist = voilist

    def __map2mat(self, caxmap, dim):
        M = np.zeros((dim, dim))
        M.fill(np.nan)
        for i in range(dim):
            rstr = caxmap[i]
            rvec = re.split('\s+', rstr.strip())
            M[i, 0:i+1] = rvec
        return M

    def __symtrans(self, M):
        Mt = M.transpose()
        dim = M.shape[0]
        for i in range(1, dim):
            Mt[i, 0:i] = M[i, 0:i]
        return Mt

    # --------Calculate average enrichment----------
    def ave_enr_calc(self, LFU=None, FUE=None):
        
        # Translate LFU map to DENS and ENR map
        npst = self.data.npst
        DENS = np.zeros((npst, npst))
        ENR = np.zeros((npst, npst))
        if LFU is None:
            LFU = self.data.LFU
        if FUE is None:
            FUE = self.data.FUE
        Nfue = FUE[:, 0].size
        for i in range(Nfue):
            ifu = int(FUE[i, 0])
            DENS[LFU == ifu] = FUE[i, 1]
            ENR[LFU == ifu] = FUE[i, 2]
        
        # Translate LPI map to pin radius map
        RADI = np.zeros((npst, npst))
        LPI = self.data.LPI
        PIN = self.data.PIN
        Npin = PIN[:, 0].size
        for i in range(Npin):
            ipi = int(PIN[i, 0])
            RADI[LPI == ipi] = PIN[i, 1]
        
        # Calculate mass
        VOLU = np.pi*RADI**2
        MASS = DENS*VOLU
        mass = np.sum(MASS)
        MASS_U235 = MASS*ENR
        mass_u235 = np.sum(MASS_U235)
        ave_enr = mass_u235/mass
        self.ave_enr = ave_enr

    def runc4(self, file_base_name, c4ver=None, neulib=None, gamlib=None, 
              grid=False):
        """Running C4E model"""
        
        c4inp = file_base_name + ".inp"
        # C4 executable
        c4exe = self.config.c4exe
        #c4exe = "cas4 -e"

        libdir = self.config.libdir
        
        if not c4ver:
            c4ver = self.config.default_version
        if not neulib:
            neulib = self.config.default_neulib
        if not gamlib:
            gamlib = self.config.default_gamlib

        outdir = os.path.split(file_base_name)[0]
        
        cmd = ' -o ' + outdir
        cmd += ' -k '
        cmd += ' -G ' + libdir + gamlib
        cmd += ' -V ' + c4ver + ' -N ' + libdir + neulib + ' ' + c4inp
        
        arglist = shlex.split(c4exe + cmd)
        arglist = shlex.split('linrsh ' + c4exe + cmd)
        # specify grid que
        arglist.insert(1, '-q')
        grid_que = self.config.grid_que
        arglist.insert(2, grid_que)
        fout = open('/dev/null', 'wb')
        if self.verbose:
            print "Running C4E model"
        if grid:
            try:  # use linrsh if available
                call(arglist, stdout=fout, stderr=STDOUT, shell=False)
                c4cax = file_base_name + ".cax"
                if not os.path.isfile(c4cax):
                    raise Exception("Grid calculation failed!")
            except:  # fallback to local machine
                print "Warning: Grid is not available on the system. Using local machine."
                call(arglist[3:], stdout=fout, stderr=STDOUT, shell=False)
        else:  # use local machine
            call(arglist[3:], stdout=fout, stderr=STDOUT, shell=False)
    
    def set_data(self, LFU=None, FUE=None, BA=None, voi=None, box_offset=0.0):
        """Append a list element to store result of new calculation"""
       
        if LFU is not None:
            self.data.LFU = LFU
        
        if FUE is not None:
            self.data.FUE = FUE
        
        if BA is not None:
            self.data.BA = BA
        
        if (LFU is not None) and (FUE is not None):
            ENR = np.zeros(LFU.shape)
            Nfue = FUE[:, 0].size
            for i in range(Nfue):
                ifu = int(FUE[i, 0])
                ENR[LFU == ifu] = FUE[i, 2]
            self.data.ENR = ENR
        
        if voi is not None:
            self.data.voilist = [int(voi)]
        
        self.data.box_offset = box_offset

    def reduce_burnpoints(self, dep_max=None, dep_thres=None):
        """Reduce number of depletion points"""
        
        if dep_max is not None:
            burnlist = []
            for burnpoints in self.burnlist:
                red_pts = [x for x in burnpoints if x <= dep_max]
                burnlist.append(red_pts)
        else:
            burnlist = self.burnlist

        if dep_thres is not None:
            thres_burnlist = []
            for burnpoints in burnlist:
                red_pts = [x for x in burnpoints if x <= dep_thres]
                pts = [x for x in burnpoints if x >= red_pts[-1]]
                red_pts2 = pts[6::6]  # reduce number of points
                if not red_pts2 or red_pts2[-1] < pts[-1]:
                    # add last point if list is empty or not included
                    red_pts2.append(pts[-1])
                red_pts.extend(red_pts2)
                thres_burnlist.append(red_pts)
            return thres_burnlist
        else:
            return burnlist

    def writecai(self, file_base_name, voi=None, dep_max=None, dep_thres=None,
                   box_offset=0.0, model="c3"):
        """Write cai file for models c3 or c4"""
        
        cinp = file_base_name + ".inp"

        # Creating dep strings
        info = self.data
                
        if not hasattr(self, "burnlist"):
            self.burnlist = [self.burnpoints(voi=v) for v in self.data.voilist]

        if dep_max or dep_thres:
            burnlist = self.reduce_burnpoints(dep_max, dep_thres)
        else:
            burnlist = self.burnlist
        
        if voi is not None:
            # set burnlist to union of all lists
            ulist = []
            for blist in burnlist:
                ulist = list(set().union(ulist, blist))
            ulist.sort()
            burnlist = [ulist]
            voilist = [int(voi)]
            self.data.voilist = voilist
        else:
            voilist = self.data.voilist
                
        if hasattr(self.data, "LFU"):
            LFU = self.data.LFU
        else:
            print "Error: LFU is missing."
            return
        
        f = open(cinp, "w")

        tit_1 = "TIT "
        tit_2 = re.sub('\s+=|=\s+|,', '=', info.tfu.split('*')[0]
                       .strip()) + " "
        tit_3 = re.sub('\s+|,', '=', info.tmo.split('*')[0].strip()) + " "
        tit = tit_1 + tit_2 + tit_3
        if voi is None:
            tit = tit + "VOI=" + str(voilist[0]) + " "
            ide = ["'BD" + str(x) + "'" for x in voilist]
            f.write(tit + "IDE=" + ide[0] + '\n')
        else:
            tit = tit + "VOI=" + str(voi) + " "
            f.write(tit + '\n')
        f.write(info.sim.strip() + '\n')
        
        FUE = info.FUE
        Nfue = FUE.shape[0]
        baid_offset = 0  # The same BA id must not occur more than once in c3
        for i in xrange(Nfue):
            f.write('FUE  %d ' % (FUE[i, 0]))
            f.write('%5.3f/%5.3f' % (FUE[i, 1], FUE[i, 2]))
            if ~np.isnan(FUE[i, 3]):
                f.write(' %d=%4.2f' % (FUE[i, 3] + baid_offset, FUE[i, 4]))
                baid_offset += 1
            f.write('\n')

        f.write('LFU\n')
        for i in xrange(info.npst):
            for j in xrange(i+1):
                f.write('%d ' % LFU[i, j])
            f.write('\n')

        pde = info.pde.split('\'')[0]
        f.write(pde.strip() + '\n')
                
        if hasattr(self.data, 'box_offset'):
            box_offset = self.data.box_offset
        bwr = self.__boxbow(box_offset)
        
        # box corner radius (extra thickness). Valid for AT11
        if model == "c3":
            if '/' in bwr:
                bwr = bwr.replace('/', '//')  # a '//' is needed for c3
        f.write(bwr + '\n')

        Npin = np.size(info.pinlines)
        if model == "c3":
            for i in xrange(Npin):
                # Remove comments etc
                tmpstr = re.split('\*|/', info.pinlines[i].strip())[0]
                pinarr = re.split(',|\s+', tmpstr.strip())  # Split for segments
                npinsegs = len(pinarr)-2
                if npinsegs > 3:
                    # c3 can handle no more than 3 radial pin segments
                    red_pinstr = ' '.join(pinarr[0:3]+pinarr[-2:])
                else:
                    red_pinstr = info.pinlines[i].strip()
                f.write(red_pinstr.strip() + '\n')
        elif model == "c4e":
            for i in xrange(Npin):
                f.write(info.pinlines[i] + '\n')
            for line in info.milines:
                f.write(line + '\n')
                
        if hasattr(info, 'slaline'):  # has water cross?
            if info.slaline:  # check that it is not empty
                f.write(info.slaline.strip() + '\n')
        
        f.write('LPI\n')
        for i in xrange(info.npst):
            for j in xrange(i+1):
                f.write('%d ' % info.LPI[i, j])
            f.write('\n')

        # Displacement
        if model == "c4e":
            if info.ldx_lines:
                f.write("LDX\n")
                for line in info.ldx_lines:
                    f.write(line + "\n")
            if info.ldy_lines:
                f.write("LDY\n")
                for line in info.ldy_lines:
                    f.write(line + "\n")

        # Spacer
        f.write(info.spa.strip() + '\n')
        
        if model == "c3":
            f.write("DEP" + '\n')
            for x in burnlist[0]:
                f.write(str(x) + '\n')
        elif model == "c4e":
            f.write(self.data.dep.strip() + "\n")
        
        f.write('NLI\n')
        f.write('STA\n')

        if voi is None:
            N = len(ide)
            for i in xrange(1, N):
                f.write("TIT " + "IDE=" + ide[i] + '\n')
                res = "RES," + ide[i-1] + ",0"
                f.write(res + '\n')
                f.write("VOI " + str(voilist[i]) + '\n')

                if model == "c3":
                    f.write("DEP" + '\n')
                    for x in burnlist[i]:
                        f.write(str(x) + '\n')
                elif model == "c4e":
                    f.write(self.data.dep.strip() + "\n")

                f.write('STA\n')

        f.write('END\n')
        f.close()

    def fill_statepoints(self):
        """Insert statepoints by interpolation of nearby points"""
        
        for j in range(len(self.data.voilist)):
            sp_burnup = [s.burnup for s in self.statepoints
                         if s.voi == self.data.voilist[j]]
        
            for i, burnpoint in enumerate(self.burnlist[j]):
                if burnpoint not in sp_burnup:
                    sp = copy.copy(self.statepoints[i-1])
                    sp.burnup = burnpoint
                    #self.statepoints.insert(i, sp)
        
    def runc3(self, filebasename, grid=False):
        """Running C3 perturbation model"""
        
        # C3 temporary file
        c3inp = filebasename + ".inp"
        c3out = filebasename + ".out"
        c3cax = filebasename + ".cax"
        # C3 libs
        lib1 = self.appdir + "lib/c3/e4lbj40"
        lib2 = self.appdir + "lib/c3/bal8ab4"
        lib3 = self.appdir + "lib/c3/galb410"
        # C3 executable
        c3exe = self.appdir + "bin/casmo3"
        if os.path.isfile(c3exe):
            pass  # no need to change the location of executable and libs
        elif os.path.isfile("." + c3exe):
            c3exe = "." + c3exe
            lib1 = "." + lib1
            lib2 = "." + lib2
            lib3 = "." + lib3
        else:
            print "Error: Could not locate C3 executable"
            return

        # Write C3 configuration file
        c3cfg = filebasename + ".cfg"
        f = open(c3cfg, "w")
        f.write(c3inp + "\n")
        f.write(c3out + "\n")
        f.write(lib1 + "\n")
        f.write(lib2 + "\n")
        f.write("\n")
        f.write(lib3 + "\n")
        f.write(c3cax + "\n")
        newlines = '\n' * 7
        f.write(newlines)
        f.close()

        # Run C3 executable
        if self.verbose:
            print "Running C3 model..."
        arglist = ['linrsh', c3exe, c3cfg]
        arglist.insert(1, '-q')
        arglist.insert(2, 'all.q@wrath,all.q@envy,all.q@pride')

        if grid:
            try:  # use linrsh if available
                call(arglist, shell=False)
                if not os.path.isfile(c3cax):
                    raise Exception("Grid calculation failed!")
            except:  # fallback to local machine
                print "Warning: Grid is not available on the system. Using local machine."
                os.environ["TMPDIR"] = "/tmp" 
                call(arglist[3:], shell=False)
        else:  # use local machine
            os.environ["TMPDIR"] = "/tmp"
            call(arglist[3:], shell=False)

        os.remove(c3cfg)  # Remove files

    def readc3cax(self, file_base_name):

        caxfile = file_base_name + ".cax"
        if not os.path.isfile(caxfile):
            print "Error: Could not open file " + caxfile
            return
        else:
            pass
        
        # Read the whole file at once
        with open(caxfile) as f:
            flines = f.read().splitlines()  # exclude \n

        # ------Search for regexp matches-------
        iTIT = self.__matchcontent(flines, '^TIT')
        iPOW = self.__matchcontent(flines, 'POW\s+')
        iPOL = self.__matchcontent(flines, '^POL')
        
        # Read fuel dimension
        npst = int(flines[iPOW[0]+1][4:6])

        # ------Step through the state points----------
        Nburnpts = len(iTIT)

        burnup = np.zeros(Nburnpts)
        burnup.fill(np.nan)
        voi = np.zeros(Nburnpts)
        voi.fill(np.nan)
        vhi = np.zeros(Nburnpts)
        vhi.fill(np.nan)
        tfu = np.zeros(Nburnpts)
        tfu.fill(np.nan)
        tmo = np.zeros(Nburnpts)
        tmo.fill(np.nan)
        kinf = np.zeros(Nburnpts)
        kinf.fill(np.nan)
        POW = np.zeros((npst, npst, Nburnpts))
        POW.fill(np.nan)

        # Row vector containing burnup, voi, vhi, tfu and tmo
        rvec = [re.split('[/\s+]+', flines[i+2].strip()) for i in iTIT]

        # Row containing Kinf
        kinfstr = [flines[i+5] for i in iPOL]

        # Rows containing radial power distribution map
        powmap = [flines[i+2:i+2+npst] for i in iPOW]

        for i in xrange(Nburnpts):
            # Read burnup, voids, tfu and tmo
            burnup[i] = rvec[i][0]
            voi[i] = rvec[i][1]
            vhi[i] = rvec[i][2]
            tfu[i] = rvec[i][3]
            tmo[i] = rvec[i][4]
            # Read kinf
            kinf[i] = re.split('\s+', kinfstr[i].strip())[0]
            # Read radial power distribution map
            POW[:, :, i] = self.__symmap(powmap[i], npst, float)

        # Calculate radial burnup distributions
        EXP = self.expcalc(POW, burnup)
        # Calculate Fint:
        fint = self.fintcalc(POW)

        # Append state instancies
        statepoints = []
        for i in xrange(Nburnpts):
            # append new instance to list
            statepoints.append(Data())
            statepoints[i].burnup = burnup[i]
            statepoints[i].voi = voi[i]
            statepoints[i].vhi = vhi[i]
            statepoints[i].tfu = tfu[i]
            statepoints[i].tmo = tmo[i]
            statepoints[i].kinf = kinf[i]
            statepoints[i].fint = fint[i]
            statepoints[i].POW = POW[:, :, i]
            statepoints[i].EXP = EXP[:, :, i]
        self.statepoints = statepoints

    def complete_calc(self, c4ver=None, neulib=None, gamlib=None, grid=False):
        """Performing a complete calculation"""
        
        caxfile = self.data.caxfile
        basename = os.path.splitext(caxfile)[0]   # remove suffix
        basename += ".T"
        if os.path.exists(basename + '.inp'):
            self.runc4(basename, c4ver=c4ver, neulib=neulib, gamlib=gamlib, 
                       grid=grid)

    def cas_calc(self, voi=None, dep_max=None, dep_thres=None, grid=False,
                  model="c3", box_offset=0.0, c4ver=None, neulib=None, 
                  gamlib=None, keepfiles=False):
        
        file_base_name = "./tmp." + str(uuid.uuid4()).split('-')[0]
        self.writecai(file_base_name, voi, dep_max, dep_thres, box_offset, 
                        model.lower())
        
        if model.lower() == "c3":
            self.runc3(file_base_name, grid)
        elif model.lower() == "c4e":
            self.runc4(file_base_name, c4ver=c4ver, neulib=neulib, 
                       gamlib=gamlib, grid=grid)
        else:
            print "Perturbation model is unknown"
            return
        self.readc3cax(file_base_name)
        self.ave_enr_calc()

        os.remove(file_base_name + ".out")
        try:
            os.remove(file_base_name + ".log")
        except:
            pass
        if not keepfiles:
            os.remove(file_base_name + ".inp")
            os.remove(file_base_name + ".cax")
        else:
            inpfile_old = file_base_name + ".inp"
            bname = os.path.basename(self.data.caxfile)
            inpfile_new = "gb-" + os.path.splitext(bname)[0] + ".inp"
            os.rename(inpfile_old, inpfile_new)
            
            caxfile_old = file_base_name + ".cax"
            caxfile_new = "gb-" + os.path.basename(self.data.caxfile)
            os.rename(caxfile_old, caxfile_new)
        if self.verbose:
            print "Done."

    def __boxbow(self, box_offset=0.0):
        """Updating the BWR card to account for box bowing."""
        bwr = self.data.bwr
        bwr_arr = re.split(',|\s+', bwr.strip())
        
        gaw = float(bwr_arr[5]) + box_offset
        gan = float(bwr_arr[6]) - box_offset  # gaw + gan = constant
        bwr_arr[5] = str(gaw)
        bwr_arr[6] = str(gan)
        bwr_offset = ' '.join(bwr_arr)
        self.data.box_offset = box_offset
        return bwr_offset

    def expcalc(self, POW, burnup):
        Nburnpts = burnup.size
        npst = POW.shape[0]
        EXP = np.zeros((npst, npst, Nburnpts))
        EXP.fill(np.nan)
        for i in range(Nburnpts):
            if burnup[i] == 0:
                EXP[:, :, i] = 0
            else:
                dburn = burnup[i] - burnup[i-1]
                if dburn < 0:
                    EXP[:, :, i] = POW[:, :, i]*burnup[i]
                else:
                    EXP[:, :, i] = EXP[:, :, i-1] + POW[:, :, i]*dburn
        return EXP

    def fintcalc(self, POW):
        Nburnpts = POW.shape[2]
        fint = np.zeros(Nburnpts)
        fint.fill(np.nan)
        for i in range(Nburnpts):
            fint[i] = POW[:, :, i].max()
        return fint

    def findpoint(self, burnup=None, vhi=None, voi=None, tfu=None):
        """Return statepoint index that correspond to specific burnup,
        void and void history
        Syntax: pt = findpoint(burnup=burnup_val,vhi=vhi_val,voi=voi_val,
        tfu=tfu_val)"""
        
        if tfu is not None:
            ipoint = next((i for i, p in enumerate(self.statepoints) 
                           if p.tfu == tfu and p.vhi == vhi and p.voi == voi),
                          None)
        elif burnup is not None:
            ipoint = next((i for i, p in enumerate(self.statepoints)
                           if p.burnup == burnup and
                           p.vhi == vhi and p.voi == voi), None)
        else:
            ipoint = next((i for i, p in enumerate(self.statepoints)
                           if p.vhi == vhi and p.voi == voi), None)
        return ipoint

    def get_statepoints(self, voi, vhi, tfu=None):
        """get a list of all state points for given voi, vhi, tfu"""

        i = self.findpoint(voi=voi, vhi=vhi, tfu=tfu)  # first index
        if i is None:
            splist = None
        else:
            splist = [self.statepoints[i]]
            Nstatepoints = len(self.statepoints)
            while ((i < Nstatepoints-1) and
                   (self.statepoints[i].burnup <= 
                    self.statepoints[i+1].burnup)):
                splist.append(self.statepoints[i+1])
                i += 1
        return splist

    def burnpoints(self, voi=40, vhi=None):
        """Return depletion vector for given voi (and vhi)"""
        
        if vhi is None:
            vhi = voi
        statepoints = self.statepoints
        i = self.findpoint(voi=voi, vhi=vhi)
        burnlist = [statepoints[i].burnup]
        Nstatepoints = len(statepoints)
        while ((i < Nstatepoints-1) and
               (statepoints[i].burnup <= statepoints[i+1].burnup)):
            burnlist.append(statepoints[i+1].burnup)
            i += 1
        return burnlist
    
    def looks_like_fuetype(self):
        if hasattr(self.data, "slaline"):  # has water cross?
            fuetype = "S96"
        elif self.data.npst == 10:
            fuetype = "A10"
        elif self.data.npst == 11:
            fuetype = "A11"
        return fuetype


if __name__ == '__main__':
    s = Segment(sys.argv[1])
